# indianpojken for HolyKeebs Sweeq

This is a local port of the `indianpojken` Ferris layout onto the HolyKeebs
`holykeebs/sweeq` target so it can be built with HolyKeebs' trackpoint/TPS43
userspace.

Build with the HolyKeebs userspace overlay and the dual-pointing-device flags:

```sh
QMK_USERSPACE=../qmk-userspace \
SKIP_FLASHING_SUPPORT=1 \
./util/docker_build.sh \
holykeebs/sweeq:indianpojken \
-e USER_NAME=holykeebs \
-e POINTING_DEVICE=trackpoint_tps43 \
-e SIDE=left
```

Repeat with `-e SIDE=right` for the right half.
