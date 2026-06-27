import sys
import subprocess
import os
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

class Command:
    def __init__(self, kb, km) -> None:
        self.kb = kb
        self.km = km
        self.arguments = []
        self.left_pointing_device = None
        self.right_pointing_device = None
        self.oled = None

    def prepend_argument(self, argument):
        self.arguments.insert(0, argument)
        self.arguments.insert(0, '-e')

    def set_pointing(self, kind, side):
        if side == 'left':
            self.left_pointing_device = kind
        elif side == 'right':
            self.right_pointing_device = kind
        else:
            raise ValueError('Invalid side: {}'.format(side))

    def add_argument(self, argument):
        self.arguments.append('-e')
        self.arguments.append(argument)

    def add_argument_raw(self, argument):
        self.arguments.append(argument)

    def arguments_list(self):
        a = list(self.arguments)
        if self.oled:
            a.append('-e')
            a.append(f'OLED={self.oled}')
        return a

    def build(self):
        return ' '.join(self.build_list())

    def build_list(self):
        l = ['make', f'{self.kb}:{self.km}'] + self.arguments_list()
        return l

    def file_name(self):
        parts = []
        parts.append(self.kb.replace('/', '_'))
        parts.append(self.km)

        if not self.kb.startswith('keyball'):
            if not self.left_pointing_device and not self.right_pointing_device:
                if self.oled:
                    parts.append('oled')
                else:
                    parts.append('none')
            else:
                if self.left_pointing_device:
                    parts.append(self.left_pointing_device)
                elif self.oled:
                    parts.append('oled')
                else:
                    parts.append('none')

                if self.right_pointing_device:
                    parts.append(self.right_pointing_device)
                elif self.oled:
                    parts.append('oled')
                else:
                    parts.append('none')

        console = False
        for argument in self.arguments:
            if argument.startswith('SIDE='):
                side = argument[len('SIDE='):]
                parts.append('flash_on_' + side)
            elif argument == 'CONSOLE=yes':
                console = True
        if console:
            parts.insert(0, 'debug')
        return '_'.join(parts)

def build_commands():
    commands = []
    skip_pointing_devices =[('cirque35', 'cirque40'), ('cirque40', 'cirque35')]
    for console_enabled in [True, False]:
        for kb in ['crkbd/rev1', 'holykeebs/spankbd', 'lily58/rev1', 'holykeebs/sweeq']:
            for left_pointing_device in ['trackpoint', 'trackball', 'cirque35', 'cirque40', 'tps43', '']:
                for right_pointing_device in ['trackpoint', 'trackball', 'cirque35', 'cirque40', 'tps43', '']:
                    if (left_pointing_device, right_pointing_device) in skip_pointing_devices:
                        print('Skipping configuration: ', left_pointing_device, right_pointing_device)
                        continue
                    # by default use the via keymap, but if we have a pointing device, pull in the hk keymap with the pointing
                    # device layer
                    keymap = 'via'
                    if left_pointing_device or right_pointing_device:
                        keymap = 'hk'
                    if left_pointing_device and right_pointing_device:
                        for side in ('left', 'right'):
                            command = Command(kb, keymap)
                            if keymap == 'hk' and console_enabled:
                                command.add_argument(f'CONSOLE=yes')
                            command.set_pointing(left_pointing_device, 'left')
                            command.set_pointing(right_pointing_device, 'right')
                            command.add_argument(f'POINTING_DEVICE={left_pointing_device}_{right_pointing_device}')
                            command.add_argument(f'SIDE={side}')
                            if left_pointing_device == 'trackball' or right_pointing_device == 'trackball':
                                command.add_argument(f'TRACKBALL_RGB_RAINBOW=yes')
                            commands.append(command)
                    else:
                        for with_oled in [True, False]:
                            command = Command(kb, keymap)
                            if keymap == 'hk' and console_enabled:
                                command.add_argument(f'CONSOLE=yes')
                            if with_oled:
                                command.oled = 'stock' if keymap == 'via' else 'yes'
                                # flip the OLED if there's a pointing device so the one on the peripheral side shows the
                                # layer and keylogger, otherwise we get the logo
                                if left_pointing_device or right_pointing_device:
                                    command.add_argument(f'OLED_FLIP=yes')
                            if left_pointing_device:
                                command.set_pointing(left_pointing_device, 'left')
                                command.add_argument(f'POINTING_DEVICE={left_pointing_device}')
                                command.add_argument(f'POINTING_DEVICE_POSITION=left')
                                if left_pointing_device == 'trackball':
                                    command.add_argument(f'TRACKBALL_RGB_RAINBOW=yes')
                            elif right_pointing_device:
                                command.set_pointing(right_pointing_device, 'right')
                                command.add_argument(f'POINTING_DEVICE={right_pointing_device}')
                                command.add_argument(f'POINTING_DEVICE_POSITION=right')
                                if right_pointing_device == 'trackball':
                                    command.add_argument(f'TRACKBALL_RGB_RAINBOW=yes')
                            else:
                                pass

                            commands.append(command)

    return commands

class BuildError(Exception):
    def __init__(self, file_name, log_path, message):
        super().__init__(message)
        self.file_name = file_name
        self.log_path = log_path

def destination_for(base_dir, file_name):
    if file_name.startswith('debug'):
        return f'{base_dir}/debug/{file_name}.uf2'
    return f'{base_dir}/{file_name}.uf2'

def finalize_command(command, make_jobs, parallel):
    if parallel > 1:
        # Make each `make` process report its own exit code independently. By
        # default QMK records build failures in a *shared* .build/error_occurred
        # file (it `rm`s it at startup and re-checks it at the end of every
        # invocation), so concurrent make processes race on that file and corrupt
        # each other's exit codes. BREAK_ON_ERRORS makes a failing build `exit 1`
        # directly instead. SKIP_GIT avoids concurrent `git submodule --sync`
        # writes to .git/config at startup.
        command.add_argument('BREAK_ON_ERRORS=yes')
        command.add_argument('SKIP_GIT=yes')
    command.add_argument_raw(f'-j{make_jobs}')
    # A unique TARGET gives each build its own .build/obj_<TARGET> directory and
    # root <TARGET>.uf2, so concurrent builds never clobber each other's output.
    command.prepend_argument(f'TARGET={command.file_name()}')

def run_build(command, base_dir):
    file_name = command.file_name()
    destination = destination_for(base_dir, file_name)
    log_path = f'{base_dir}/logs/{file_name}.log'

    # Archive firmware from a previous run before overwriting it.
    if os.path.exists(destination):
        os.rename(destination, f'{base_dir}/previous/{file_name}.uf2')

    with open(log_path, 'wb') as log:
        log.write(f'{command.build()}\n\n'.encode())
        log.flush()
        proc = subprocess.run(command.build_list(), stdout=log, stderr=subprocess.STDOUT)

    if proc.returncode != 0:
        raise BuildError(file_name, log_path, f'make exited with {proc.returncode}')

    os.rename(f'{file_name}.uf2', destination)
    return file_name

def main() -> int:
    cpu = os.cpu_count() or 4
    parser = argparse.ArgumentParser(description='Build the holykeebs firmware matrix.')
    parser.add_argument('-p', '--parallel', type=int, default=max(1, cpu // 4),
                        help='number of builds to run concurrently (default: %(default)s)')
    parser.add_argument('-j', '--jobs', type=int, default=0,
                        help='make jobs per build (default: cpu // parallel)')
    args = parser.parse_args()

    parallel = max(1, args.parallel)
    make_jobs = args.jobs if args.jobs > 0 else max(1, cpu // parallel)

    commands = [
        Command('keyball/keyball39', 'via'),
        Command('keyball/keyball44', 'via'),
        Command('keyball/keyball61', 'via'),
    ]
    for command in build_commands():
        command.prepend_argument('USER_NAME=holykeebs')
        commands.append(command)

    base_dir = 'build_all'
    for sub in ('debug', 'previous', 'logs'):
        os.makedirs(f'{base_dir}/{sub}', exist_ok=True)

    for command in commands:
        finalize_command(command, make_jobs, parallel)

    with open(f'{base_dir}/commands.txt', 'w') as commands_file:
        for command in commands:
            commands_file.write(f'{command.file_name()}: {command.build()}\n')

    total = len(commands)
    print(f'Building {total} firmwares with {parallel} concurrent build(s) x '
          f'make -j{make_jobs} (detected {cpu} CPUs)')

    done = 0
    with ThreadPoolExecutor(max_workers=parallel) as executor:
        futures = [executor.submit(run_build, c, base_dir) for c in commands]
        try:
            for future in as_completed(futures):
                file_name = future.result()  # re-raises BuildError on failure
                done += 1
                print(f'[{done}/{total}] OK {file_name}')
        except BuildError as err:
            for future in futures:
                future.cancel()
            print(f'\nBuild failed: {err.file_name}: {err} (see {err.log_path})')
            return 1

    print(f'\nAll {total} builds succeeded.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
