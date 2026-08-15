#!/usr/bin/env bash

set -e

if [ -z "${1:-}" ]; then
    echo "Usage: $0 <led_value>"
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
            /sparkie/board/ledstrip \
            std_msgs/msg/Int8 \
            "{data: $1}"
    ' _ "$1"