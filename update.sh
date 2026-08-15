#!/usr/bin/env bash

set -Eeuo pipefail

readonly ROS_DISTRO="jazzy"
readonly CONTAINER_NAME="ros-jazzy"
readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

log() {
    printf '[sparkie-update] %s\n' "$*"
}

die() {
    printf '[sparkie-update] ERROR: %s\n' "$*" >&2
    exit 1
}

command -v distrobox >/dev/null 2>&1 || die "distrobox is not installed; run ./install.sh first"
command -v docker >/dev/null 2>&1 || die "docker is not installed; run ./install.sh first"
docker info >/dev/null 2>&1 || die "Docker is not accessible"

if ! distrobox list --no-color 2>/dev/null \
    | awk -F '|' 'NR > 1 {gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2); print $2}' \
    | grep -qx "$CONTAINER_NAME"; then
    die "the ${CONTAINER_NAME} container does not exist; run ./install.sh first"
fi

package_arguments=()
if (($# > 0)); then
    package_arguments=(--packages-up-to "$@")
    log "Building packages up to: $*"
else
    log "Building the complete workspace"
fi

distrobox enter -n "$CONTAINER_NAME" --no-tty -- bash -lc '
    set -Eeuo pipefail
    set +u
    source /opt/ros/'"$ROS_DISTRO"'/setup.bash
    set -u
    cd '"$(printf '%q' "$SCRIPT_DIR")"'

    speech_config="src/sparkie_base/sparkie_base/config/boot_sequence.yaml"
    online_speech="src/sparkie_base/sparkie_base/sounds/startup_online.mp3"
    offline_speech="src/sparkie_base/sparkie_base/sounds/startup_offline.mp3"
    if [[ ! -f "$online_speech" \
        || ! -f "$offline_speech" \
        || "$speech_config" -nt "$online_speech" \
        || "$speech_config" -nt "$offline_speech" ]]; then
        echo "[sparkie-update] Regenerating cached boot speech"
        python3 src/sparkie_base/sparkie_base/scripts/generate_boot_speech.py
    fi

    colcon build --packages-skip sparkie_conversation "$@"
' _ "${package_arguments[@]}"

log "Restarting sparkie.service"
sudo systemctl restart sparkie.service

log "Update complete"
