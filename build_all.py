import sys
import subprocess
import os
import argparse
import time
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
    # Line-buffer stdout so the live progress feed is visible even when this runs
    # in the background with stdout redirected to a file (block-buffered by default).
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(line_buffering=True)

    cpu = os.cpu_count() or 4
    parser = argparse.ArgumentParser(description='Build the holykeebs firmware matrix.')
    parser.add_argument('-p', '--parallel', type=int, default=max(1, cpu // 2),
                        help='number of builds to run concurrently (default: %(default)s)')
    parser.add_argument('-j', '--jobs', type=int, default=0,
                        help='make jobs per build (default: cpu // parallel)')
    parser.add_argument('--rebuild', action='store_true',
                        help='rebuild every firmware, archiving existing outputs to '
                             'previous/. Default skips configs already present in '
                             'build_all/ (resume-friendly); note it does NOT detect '
                             'stale outputs, so pass --rebuild to refresh after source '
                             'changes.')
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

    # keyball61plus runs on the holykeebs userspace but isn't part of the modular
    # POINTING_DEVICE matrix above: it's always built dual-PMW3360 combined (the
    # installed ball count is detected at runtime), so add its variants directly.
    # The peripheral OLED is rotated via OLED_FLIP.
    for km in ('via', 'default'):
        for with_oled in (True, False):
            command = Command('holykeebs/keyball61plus', km)
            command.add_argument('USER_NAME=holykeebs')
            if with_oled:
                command.oled = 'yes'
                command.add_argument('OLED_FLIP=yes')
            commands.append(command)

    # Drop duplicate configurations. The console_enabled loop in build_commands()
    # regenerates every `via` build identically (CONSOLE only affects `hk`), which
    # both wastes a rebuild and breaks the unique-TARGET invariant that keeps
    # concurrent builds from racing on a shared .build/obj_<TARGET> and output.
    seen = set()
    unique = []
    for command in commands:
        name = command.file_name()
        if name not in seen:
            seen.add(name)
            unique.append(command)
    commands = unique

    base_dir = 'build_all'
    for sub in ('debug', 'previous', 'logs'):
        os.makedirs(f'{base_dir}/{sub}', exist_ok=True)

    for command in commands:
        finalize_command(command, make_jobs, parallel)

    with open(f'{base_dir}/commands.txt', 'w') as commands_file:
        for command in commands:
            commands_file.write(f'{command.file_name()}: {command.build()}\n')

    # By default skip configs whose firmware already exists (resume after an abort);
    # --rebuild forces a full rebuild, archiving the existing outputs to previous/.
    # In skip mode nothing existing is touched, so previous/ is only populated by a
    # full rebuild -- keeping the build dir stable unless you ask for a fresh one.
    if args.rebuild:
        to_build, skipped = commands, []
    else:
        to_build, skipped = [], []
        for command in commands:
            if os.path.exists(destination_for(base_dir, command.file_name())):
                skipped.append(command)
            else:
                to_build.append(command)

    if skipped:
        print(f'Skipping {len(skipped)} firmware(s) already in {base_dir}/ '
              f'(use --rebuild to force a full rebuild)')
    if not to_build:
        print(f'Nothing to build; all {len(commands)} firmwares present.')
        return 0

    total = len(to_build)
    print(f'Building {total} firmwares with {parallel} concurrent build(s) x '
          f'make -j{make_jobs} (detected {cpu} CPUs)')

    start = time.time()
    done = 0
    with ThreadPoolExecutor(max_workers=parallel) as executor:
        futures = [executor.submit(run_build, c, base_dir) for c in to_build]
        try:
            for future in as_completed(futures):
                file_name = future.result()  # re-raises BuildError on failure
                done += 1
                print(f'[{done}/{total}] OK {file_name}  ({time.time() - start:.0f}s)')
        except BuildError as err:
            for future in futures:
                future.cancel()
            print(f'\nBuild failed after {time.time() - start:.0f}s: '
                  f'{err.file_name}: {err} (see {err.log_path})')
            return 1

    elapsed = time.time() - start
    print(f'\nBuilt {total} firmwares in {elapsed:.0f}s ({elapsed / 60:.1f} min); '
          f'{len(commands)} total present.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
