# indianpojken_macos_sv for HolyKeebs Sweeq

This is a macOS Swedish variant of the local `indianpojken` port for the
HolyKeebs `holykeebs/sweeq` target.

Assumptions:

- macOS input source: `Swedish`
- QMK symbol mapping: `keymap_swedish_mac_iso.h`
- macOS-style shortcuts for app switching, clipboard, screenshot, Mission
  Control, and zoom

If you use `Swedish - Pro` instead, switch the keymap includes to
`keymap_swedish_pro_mac_ansi.h` or `keymap_swedish_pro_mac_iso.h` as needed.

Build with the HolyKeebs userspace overlay and the dual-pointing-device flags:

```sh
./build-indianpojken.sh left indianpojken_macos_sv
```

Repeat with `right` for the right half.
