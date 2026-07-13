#!/bin/sh

set -eu

root="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"

rm -rf "${root}/artifacts" "${root}/.vendor/.bootstrapped"

if [ -d "${root}/.vendor/qmk_firmware/.build" ]; then
    rm -rf "${root}/.vendor/qmk_firmware/.build"
fi

if [ -f "${root}/.vendor/qmk_firmware/holykeebs_sweeq_indianpojken_macos_sv.uf2" ]; then
    rm -f "${root}/.vendor/qmk_firmware/holykeebs_sweeq_indianpojken_macos_sv.uf2"
fi

if [ -f "${root}/.vendor/qmk-userspace/holykeebs_sweeq_indianpojken_macos_sv.uf2" ]; then
    rm -f "${root}/.vendor/qmk-userspace/holykeebs_sweeq_indianpojken_macos_sv.uf2"
fi
