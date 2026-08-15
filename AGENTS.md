# Sparkie Workspace Agent Guide

This repository is the ROS 2 workspace for the Sparkie robot running on an NVIDIA Jetson Orin Nano.

## Communication

- Always communicate and write documentation, code comments, logs, and user-facing text in English.
- Preserve the user's local changes. This workspace intentionally contains modified Git submodules.
- Do not edit generated `build/`, `install/`, or `log/` content directly.

## Environment

- Host: Ubuntu 22.04 on Jetson Linux R36.4.0.
- ROS: ROS 2 Jazzy inside the Docker-backed Distrobox named `ros-jazzy`.
- Workspace: `/home/sparkie/sparkie/sparkie_ws`.
- Runtime service: `sparkie.service`.
- The service executes `bin/start-sparkie`, which waits for `/dev/ttyACM0` and launches `sparkie_base sparkie.launch.py` inside Distrobox.
- Source ROS before running ROS commands:

  ```bash
  source /opt/ros/jazzy/setup.bash
  source /home/sparkie/sparkie/sparkie_ws/install/setup.bash
  ```

## Deployment

- First-time/full provisioning: `./install.sh`.
- Normal source/config update: `./update.sh` or `./update.sh <package>`.
- `update.sh` builds with regular copied installs, not `--symlink-install`, because the existing workspace layout is incompatible with switching modes.
- Do not run `git pull`, reset submodules, or clean build artifacts unless explicitly requested.

## Verification

For Python or launch changes:

```bash
python3 -m py_compile <changed-python-files>
```

For shell changes:

```bash
bash -n <changed-shell-files>
```

For package deployment:

```bash
./update.sh <package>
sudo journalctl -u sparkie.service -f
```

## Important Invariants

- Motor commands ultimately go to `/sparkie/board/cmd_vel`.
- The board serial device is `/dev/ttyACM0`; the LiDAR is `/dev/ttyUSB0`.
- The USB audio card has stable ALSA ID `Device`; ALSA defaults are defined in `config/alsa/asound.conf`.
- Do not add `pactl` commands to the system service. It runs without a PulseAudio/PipeWire user session.
- Boot speech is cached and played locally. Edge TTS is used only to regenerate assets, never during boot.
- The boot sequence announces readiness only after board, LiDAR, filtered odometry, camera, and LED subscriber readiness.

See `docs/ARCHITECTURE.md` and `docs/OPERATIONS.md` before changing runtime topology or deployment behavior.
