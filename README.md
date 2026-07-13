# hoolysweep

Minimal source for the flashed HolyKeebs `holykeebs/sweeq` layout:

- keymap: `indianpojken_macos_sv`
- OS: macOS
- input language: Swedish
- pointing combo: left trackpoint + right TPS43
- USB/master side: left

## Fresh Clone Build

From the repo root:

```sh
./samu left
./samu right
```

That will:

1. enter a Nix dev shell,
2. fetch the HolyKeebs `qmk_firmware` and `qmk-userspace` sources into `.vendor/`,
3. copy this keymap into the fetched `qmk_firmware` tree,
4. build the requested half.

Artifacts end up in:

- `artifacts/holykeebs_sweeq_indianpojken_macos_sv_left.uf2`
- `artifacts/holykeebs_sweeq_indianpojken_macos_sv_right.uf2`

## Other Targets

Build both halves:

```sh
./samu all
```

Clean generated files:

```sh
./samu clean
```

## Notes

- this repo uses Nix, not Docker
- the root build entrypoint is `build.ninja`, executed through the `./samu` wrapper
- upstream QMK still compiles through `make` internally; this repo just gives you a root-level `samu` workflow
- the HolyKeebs `qmk_firmware` and `qmk-userspace` revisions are pinned to the exact commits this layout was built and flashed from
- left UF2 goes to the left half
- right UF2 goes to the right half
- connect USB to the left half in normal use
- never connect or disconnect the interconnect cable while a half is powered
