#!/bin/sh

set -eu

side="${1:-}"
keymap="${2:-indianpojken}"

if [ -z "$side" ]; then
    echo "Usage: $0 <left|right> [keymap]"
    exit 1
fi

case "$side" in
    left|right)
        ;;
    *)
        echo "Invalid side: $side"
        echo "Usage: $0 <left|right> [keymap]"
        exit 1
        ;;
esac

script_dir="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
artifact_dir="$script_dir/artifacts"
base_name="holykeebs_sweeq_${keymap}"
built_uf2="$script_dir/$base_name.uf2"
side_uf2="$artifact_dir/${base_name}_${side}.uf2"

mkdir -p "$artifact_dir"

if [ -d "$script_dir/users/holykeebs" ]; then
    SKIP_FLASHING_SUPPORT=1 \
    ./util/docker_build.sh \
    "holykeebs/sweeq:${keymap}" \
    -e USER_NAME=holykeebs \
    -e POINTING_DEVICE=trackpoint_tps43 \
    -e SIDE="$side" \
    -j8
else
    userspace_dir="$script_dir/../qmk-userspace"

    QMK_USERSPACE="$userspace_dir" \
    SKIP_FLASHING_SUPPORT=1 \
    ./util/docker_build.sh \
    "holykeebs/sweeq:${keymap}" \
    -e USER_NAME=holykeebs \
    -e POINTING_DEVICE=trackpoint_tps43 \
    -e SIDE="$side" \
    -j8
fi

if [ ! -f "$built_uf2" ]; then
    echo "Expected build output not found: $built_uf2"
    exit 1
fi

cp "$built_uf2" "$side_uf2"
echo "Saved $side_uf2"
