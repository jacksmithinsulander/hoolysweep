# CLAUDE.md

Notes for working in this fork. The upstream QMK docs cover the rest; this file
documents the holykeebs-specific build workflow.

## Compiling a holykeebs keyboard

This fork carries the `users/holykeebs` userspace, which implements the pointing
device handling (Pimoroni trackball, TrackPoint, Cirque, Azoteq TPS), sniping,
drag-scroll, scroll lock, OLED, EEPROM config, and split state sync. Boards
select behavior at build time via `-e VAR=value` flags.

### Command form

```
make <keyboard>:<keymap> -e USER_NAME=holykeebs -e POINTING_DEVICE=<dev> -e POINTING_DEVICE_POSITION=<pos> [-e MORE=val ...]
```

Verified example — single trackball on the right half:

```
make holykeebs/sweeq:hk -e USER_NAME=holykeebs -e POINTING_DEVICE=trackball -e POINTING_DEVICE_POSITION=right
```

Append `:flash` to the target to flash, or copy the resulting `<target>.uf2`
to the RP2040 bootloader drive.

### `USER_NAME=holykeebs` is mandatory (and the failure is silent)

The keymaps include the userspace header by full path
(`#include "users/holykeebs/holykeebs.h"`). So if you omit `USER_NAME`, the
build still **compiles and links successfully** — the header resolves the
`HK_*` keycode enum, and QMK's weak default hooks satisfy the linker — but the
firmware is **silently missing the entire userspace**: none of
`users/holykeebs/*.c` is compiled, so there's no pointing-device processing, no
`HK_*` keycode handling, and no EEPROM config.

`USER_NAME=holykeebs` is what pulls in `users/holykeebs/rules.mk`, which:
- adds `holykeebs.c` / `oled.c` / etc. to the build, and
- sets `SERIAL_DRIVER = vendor` for splits.

Without it, a split board instead fails later with
`SOFT_SERIAL_PIN undeclared` in `platforms/chibios/drivers/serial.c` (the
serial driver was never switched off the soft-serial default). If you see that
error, you forgot `USER_NAME=holykeebs`.

### Keyboards and keymaps

Boards driven by this userspace: `holykeebs/sweeq`, `holykeebs/spankbd`,
`holykeebs/aztec42`, `crkbd/rev1`, `lily58/rev1`.

Keymap: use `hk` when a pointing device is present (it adds the pointer/scroll
layer); `via` for a build with no pointing device. (Some boards, e.g. aztec42,
use `default`/`vial` instead.)

### Build variables

| Variable | Values | Notes |
|---|---|---|
| `USER_NAME` | `holykeebs` | **Required** — see above. |
| `POINTING_DEVICE` | `trackball`, `trackpoint`, `cirque35`, `cirque40`, `tps43`, `tps65`, or `<left>_<right>` (e.g. `trackball_cirque40`) | Omit for no pointing device. Full valid set: `VALID_POINTING_DEVICE_CONFIGURATIONS` in `users/holykeebs/rules.mk`. |
| `POINTING_DEVICE_POSITION` | `right`, `left`, `thumb`, `thumb_inner`, `thumb_outer`, `middle` | Where the (single) device sits. |
| `SIDE` | `left`, `right` | Required for dual (`<left>_<right>`) configs — build once per side. |
| `OLED` | `yes` (holykeebs OLED: status + keylog), `stock` (plain QMK OLED) | Omit for none. |
| `OLED_FLIP` | `yes` | Rotate the OLED 180° (peripheral side). |
| `BONGO_ENABLE` | `yes` | Bongocat OLED animation (needs `OLED=yes`). |
| `TRACKBALL_RGB_RAINBOW` | `yes` | Rainbow-cycle the Pimoroni trackball LED. |
| `HIRES_SCROLL` | `yes` | High-resolution (sub-line) scrolling. |
| `CONSOLE` | `yes` | Enable console for debug (`HK_DUMP`, `printf`). |

The master/peripheral side is derived automatically (`rules.mk` sets
`MASTER_SIDE` → `HK_MASTER_LEFT`/`HK_MASTER_RIGHT`); don't set it by hand.

### Bulk builds

`build_all.py` compiles the full board × pointing-device × OLED matrix. It
always passes `USER_NAME=holykeebs` and a unique `TARGET` per build (so parallel
builds don't clobber each other). Run `python3 build_all.py` (`--help` for jobs
/ parallelism).
