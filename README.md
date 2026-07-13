# hoolysweep

Minimal source for the flashed layout on a HolyKeebs `holykeebs/sweeq`:

- keymap: `indianpojken_macos_sv`
- OS: macOS
- input language: Swedish
- pointing combo: left trackpoint + right TPS43
- USB/master side: left

## Files

Copy this folder into the HolyKeebs QMK fork at the same path:

`keyboards/holykeebs/sweeq/keymaps/indianpojken_macos_sv`

## Build

From the HolyKeebs `qmk_firmware` repo root:

```sh
QMK_USERSPACE=/path/to/qmk-userspace \
SKIP_FLASHING_SUPPORT=1 \
./util/docker_build.sh "holykeebs/sweeq:indianpojken_macos_sv" \
  -e USER_NAME=holykeebs \
  -e POINTING_DEVICE=trackpoint_tps43 \
  -e SIDE=left \
  -j8
```

Build the right half the same way, but change `SIDE=left` to `SIDE=right`.

The resulting UF2 files are:

- left: `holykeebs_sweeq_indianpojken_macos_sv.uf2`
- right: build again with `SIDE=right`

## Flash

- left UF2 goes to the left half
- right UF2 goes to the right half
- connect USB to the left half in normal use
- never connect or disconnect the interconnect cable while a half is powered
