#!/usr/bin/env bash

set -Eeuo pipefail

readonly ROS_DISTRO="jazzy"
readonly CONTAINER_NAME="ros-jazzy"
readonly CONTAINER_IMAGE="docker.io/library/ros:jazzy-ros-base"
readonly SERVICE_NAME="sparkie.service"
readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly SERVICE_SOURCE="${SCRIPT_DIR}/systemd/${SERVICE_NAME}"
readonly SERVICE_TARGET="/etc/systemd/system/${SERVICE_NAME}"
readonly INSTALL_USER="$(id -un)"

log() {
    printf '[sparkie-install] %s\n' "$*"
}

die() {
    printf '[sparkie-install] ERROR: %s\n' "$*" >&2
    exit 1
}

command -v sudo >/dev/null 2>&1 || die "sudo is required"
[[ "$(uname -s)" == "Linux" ]] || die "this installer supports Linux only"
[[ -f /etc/os-release ]] || die "cannot identify the operating system"

# shellcheck disable=SC1091
source /etc/os-release
[[ "${ID:-}" == "ubuntu" ]] || die "Ubuntu is required (found ${ID:-unknown})"
[[ "$INSTALL_USER" == "sparkie" ]] || die "the checked-in service runs as user 'sparkie'; run this installer from that account"
[[ "$SCRIPT_DIR" == "/home/sparkie/sparkie/sparkie_ws" ]] || \
    die "the checked-in service expects the workspace at /home/sparkie/sparkie/sparkie_ws"

log "Installing host prerequisites"
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    ca-certificates \
    curl \
    distrobox \
    docker.io \
    git

sudo systemctl enable --now docker.service

if ! id -nG "$INSTALL_USER" | tr ' ' '\n' | grep -qx docker; then
    sudo usermod -aG docker "$INSTALL_USER"
    die "${INSTALL_USER} was added to the docker group. Log out and back in, then run this script again"
fi

docker info >/dev/null 2>&1 || die "Docker is not accessible; verify the daemon and your docker-group session"

log "Configuring the USB sound card as the host ALSA default"
sudo install -m 0644 "${SCRIPT_DIR}/config/alsa/asound.conf" /etc/asound.conf

log "Initializing Git submodules"
git -C "$SCRIPT_DIR" submodule update --init --recursive

if ! distrobox list --no-color 2>/dev/null \
    | awk -F '|' 'NR > 1 {gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2); print $2}' \
    | grep -qx "$CONTAINER_NAME"; then
    log "Creating the ${CONTAINER_NAME} container"
    distrobox create \
        --name "$CONTAINER_NAME" \
        --image "$CONTAINER_IMAGE" \
        --yes
fi

log "Installing ROS ${ROS_DISTRO} dependencies inside ${CONTAINER_NAME}"
distrobox enter -n "$CONTAINER_NAME" --no-tty -- bash -lc "
    set -Eeuo pipefail
    sudo apt-get update
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \\
        python3-colcon-common-extensions \\
        python3-pip \\
        python3-protobuf \\
        python3-rosdep \\
        python3-serial \\
        alsa-utils \\
        iputils-ping \\
        mpv \\
        ros-${ROS_DISTRO}-cartographer-ros \\
        ros-${ROS_DISTRO}-foxglove-bridge \\
        ros-${ROS_DISTRO}-imu-complementary-filter \\
        ros-${ROS_DISTRO}-imu-filter-madgwick \\
        ros-${ROS_DISTRO}-joy \\
        ros-${ROS_DISTRO}-navigation2 \\
        ros-${ROS_DISTRO}-nav2-bringup \\
        ros-${ROS_DISTRO}-realsense2-camera \\
        ros-${ROS_DISTRO}-robot-localization \\
        ros-${ROS_DISTRO}-robot-state-publisher \\
        ros-${ROS_DISTRO}-rviz2 \\
        ros-${ROS_DISTRO}-teleop-twist-joy \\
        ros-${ROS_DISTRO}-xacro

    sudo install -m 0644 '${SCRIPT_DIR}/config/alsa/asound.conf' /etc/asound.conf

    python3 -m pip install --user --break-system-packages --upgrade edge-tts
    python3 '${SCRIPT_DIR}/src/sparkie_base/sparkie_base/scripts/generate_boot_speech.py'

    if [[ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
        sudo rosdep init
    fi
    rosdep update
    set +u
    source /opt/ros/${ROS_DISTRO}/setup.bash
    set -u
    cd '${SCRIPT_DIR}'
    rosdep install --from-paths src --ignore-src --rosdistro ${ROS_DISTRO} -r -y
    colcon build --packages-skip sparkie_conversation
"

log "Installing and enabling ${SERVICE_NAME}"
sudo install -m 0644 "$SERVICE_SOURCE" "$SERVICE_TARGET"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"

log "Installation complete. Start Sparkie with: sudo systemctl start ${SERVICE_NAME}"
