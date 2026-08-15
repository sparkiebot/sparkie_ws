#!/usr/bin/env bash

set -Eeuo pipefail

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly ALSA_CONFIG="${SCRIPT_DIR}/config/alsa/asound.conf"

command -v sudo >/dev/null 2>&1 || {
    printf 'ERROR: sudo is required\n' >&2
    exit 1
}
command -v distrobox >/dev/null 2>&1 || {
    printf 'ERROR: distrobox is required\n' >&2
    exit 1
}

printf '[sparkie-audio] Installing the host ALSA default\n'
sudo install -m 0644 "$ALSA_CONFIG" /etc/asound.conf

printf '[sparkie-audio] Default output configured as CARD=Device,DEV=0\n'
