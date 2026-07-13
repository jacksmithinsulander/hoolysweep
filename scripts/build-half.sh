#!/bin/sh

set -eu

side="${1:-}"
case "$side" in
    left|right)
        ;;
    *)
        echo "Usage: $0 <left|right>" >&2
        exit 1
        ;;
esac

root="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
"${root}/scripts/bootstrap.sh"

vendor_dir="${root}/.vendor"
qmk_firmware="${HOOLYSWEEP_QMK_FIRMWARE:-${vendor_dir}/qmk_firmware}"
qmk_userspace="${HOOLYSWEEP_QMK_USERSPACE:-${vendor_dir}/qmk-userspace}"
artifacts_dir="${root}/artifacts"
keymap="indianpojken_macos_sv"
jobs="${JOBS:-8}"

mkdir -p "$artifacts_dir"

(
    cd "$qmk_firmware"
    QMK_USERSPACE="$qmk_userspace" \
    make "holykeebs/sweeq:${keymap}" \
        USER_NAME=holykeebs \
        POINTING_DEVICE=trackpoint_tps43 \
        SIDE="$side" \
        -j"$jobs"
)

built_uf2="${qmk_firmware}/holykeebs_sweeq_${keymap}.uf2"
side_uf2="${artifacts_dir}/holykeebs_sweeq_${keymap}_${side}.uf2"

if [ ! -f "$built_uf2" ]; then
    echo "Expected build output not found: $built_uf2" >&2
    exit 1
fi

cp "$built_uf2" "$side_uf2"
echo "Saved $side_uf2"
