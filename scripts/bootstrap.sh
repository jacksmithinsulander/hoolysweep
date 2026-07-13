#!/bin/sh

set -eu

root="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
vendor_dir="${root}/.vendor"

qmk_firmware="${HOOLYSWEEP_QMK_FIRMWARE:-${vendor_dir}/qmk_firmware}"
qmk_userspace="${HOOLYSWEEP_QMK_USERSPACE:-${vendor_dir}/qmk-userspace}"
qmk_firmware_ref="ac473b73b07cb154a4c4c195ddbff42147f4f54d"
qmk_userspace_ref="1b4f1152cc968cf8aeb3f67771b6f3b9489d6004"

clone_or_update() {
    repo_url="$1"
    ref="$2"
    destination="$3"

    if [ -n "${4:-}" ] && [ "$4" = "skip" ]; then
        return 0
    fi

    if [ ! -d "$destination/.git" ]; then
        mkdir -p "$destination"
        git -C "$destination" init
        git -C "$destination" remote add origin "$repo_url"
    fi

    if ! git -C "$destination" rev-parse --verify --quiet "${ref}^{commit}" >/dev/null; then
        git -C "$destination" fetch --depth 1 origin "$ref"
    fi

    git -C "$destination" checkout --detach "$ref"
}

mkdir -p "$vendor_dir"

managed_qmk_firmware="yes"
managed_qmk_userspace="yes"

if [ "${HOOLYSWEEP_QMK_FIRMWARE:-}" ]; then
    managed_qmk_firmware="no"
fi

if [ "${HOOLYSWEEP_QMK_USERSPACE:-}" ]; then
    managed_qmk_userspace="no"
fi

clone_or_update "https://github.com/holykeebs/qmk_firmware.git" "$qmk_firmware_ref" "$qmk_firmware" "$([ "$managed_qmk_firmware" = "yes" ] || printf skip)"
clone_or_update "https://github.com/holykeebs/qmk-userspace.git" "$qmk_userspace_ref" "$qmk_userspace" "$([ "$managed_qmk_userspace" = "yes" ] || printf skip)"

if [ "$managed_qmk_firmware" = "yes" ]; then
    git -C "$qmk_firmware" submodule update --init --recursive
fi

keymap_src="${root}/keyboards/holykeebs/sweeq/keymaps/indianpojken_macos_sv"
keymap_dst="${qmk_firmware}/keyboards/holykeebs/sweeq/keymaps/indianpojken_macos_sv"

rm -rf "$keymap_dst"
mkdir -p "$(dirname "$keymap_dst")"
cp -R "$keymap_src" "$keymap_dst"

mkdir -p "$vendor_dir"
touch "${vendor_dir}/.bootstrapped"
