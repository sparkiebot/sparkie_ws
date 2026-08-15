#!/usr/bin/env bash

set -e

/usr/local/bin/distrobox enter \
    -n ros-jazzy \
    --no-tty \
    -- \
    bash -lc '
        set -e

        source /opt/ros/jazzy/setup.bash
        source /home/sparkie/sparkie/sparkie_ws/install/setup.bash

        VOLTAGE=$(ros2 topic echo \
            --once \
            --field voltage \
            /sparkie/board/battery | head -n 1)

        python3 - "$VOLTAGE" << "PY"
import sys

voltage = float(sys.argv[1])

CELLS = 3
cell_voltage = voltage / CELLS

# Curva LiPo approssimativa: tensione a riposo -> percentuale
curve = [
    (3.30,   0),
    (3.50,   5),
    (3.60,  10),
    (3.70,  20),
    (3.75,  30),
    (3.80,  40),
    (3.85,  50),
    (3.90,  60),
    (3.95,  70),
    (4.00,  80),
    (4.10,  90),
    (4.20, 100),
]

def percentage_from_voltage(v):
    if v <= curve[0][0]:
        return 0.0

    if v >= curve[-1][0]:
        return 100.0

    for (v1, p1), (v2, p2) in zip(curve, curve[1:]):
        if v1 <= v <= v2:
            return p1 + (v - v1) * (p2 - p1) / (v2 - v1)

    return 0.0

percentage = percentage_from_voltage(cell_voltage)

print(
    f"Battery: {voltage:.2f} V | "
    f"{cell_voltage:.2f} V/cell | "
    f"{percentage:.0f}%"
)
PY
    '