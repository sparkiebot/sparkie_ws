#!/usr/bin/env bash

set -e

if [ -z "${1:-}" ]; then
    echo "Usage: $0 <angle_value>"
    exit 1
fi

/usr/local/bin/distrobox enter \
    -n ros-jazzy \
    --no-tty \
    -- \
    bash -lc '
        set -e

        source /opt/ros/jazzy/setup.bash
        source /home/sparkie/sparkie/sparkie_ws/install/setup.bash

        exec ros2 topic pub \
            --once \
            /sparkie/board/head/tilt \
            std_msgs/msg/Float32 \
            "{data: $1}"
    ' _ "$1"