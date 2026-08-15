# Sparkie Architecture

## Overview

Sparkie is a differential-drive ROS 2 robot running on an NVIDIA Jetson Orin Nano. ROS 2 Jazzy runs inside the Docker-backed `ros-jazzy` Distrobox. The host starts the stack through systemd.

```text
sparkie.service
  -> bin/start-sparkie
     -> ros2 launch sparkie_base sparkie.launch.py
        -> robot description
        -> ESP32 board bridge
        -> perception aggregate
           -> LiDAR
           -> IMU filtering and EKF odometry
           -> RealSense camera
        -> boot sequence
```

## Packages

- `sparkie_base`: top-level launch files and the boot-sequence node.
- `sparkie_board_connect`: serial/Protobuf bridge to the ESP32 control board.
- `sparkie_description`: Xacro/URDF model, meshes, and static robot transforms.
- `sparkie_perception`: aggregate perception launch package.
- `sparkie_lidar`: Slamtec C1 configuration and scan remapping.
- `sllidar_ros2`: upstream Slamtec ROS 2 driver.
- `sparkie_odom`: Madgwick IMU filter and `robot_localization` EKF.
- `sparkie_slam`: Cartographer mapping and localization.
- `sparkie_nav`: Nav2 localization, planning, control, behaviors, and velocity smoothing.
- `sparkie_sim`: incomplete Webots simulation.
- `sparkie_conversation`: incomplete placeholder; excluded from builds.

Several packages are Git submodules. Treat existing submodule modifications as user-owned work.

## Runtime Data Flow

The board bridge publishes:

- `/sparkie/board/imu`
- `/sparkie/board/mag`
- `/sparkie/board/us/{left,front,right}`
- `/sparkie/board/temperature`
- `/sparkie/board/humidity`
- `/sparkie/board/battery`
- `/sparkie/board/wheels/{left,right,odom}`

It subscribes to:

- `/sparkie/board/cmd_vel`
- `/sparkie/board/ledstrip`
- `/sparkie/board/head/tilt`

Perception and navigation use:

- LiDAR: `/sparkie/scan`
- Filtered IMU: `/sparkie/imu`
- EKF odometry: `/sparkie/odom/ekf`
- Nav2 velocity input: `/sparkie/nav/cmd_vel`
- Smoothed motor output: `/sparkie/board/cmd_vel`

## Boot Readiness Sequence

The node `sparkie_base.boot_sequence` waits for real messages from:

- `/sparkie/board/battery`
- `/sparkie/scan`
- `/sparkie/odom/ekf`
- `/sparkie/camera/color/image_raw`

It also waits for discovery of the LED controller subscriber. When ready, it publishes LED effect `11`, plays `boot_success.wav`, pings the configured connectivity host, and plays either `startup_online.mp3` or `startup_offline.mp3`.

Boot feedback configuration is in:

```text
src/sparkie_base/sparkie_base/config/boot_sequence.yaml
```

Speech MP3 files are generated from that configuration by:

```text
src/sparkie_base/sparkie_base/scripts/generate_boot_speech.py
```

Edge TTS is an asset-generation dependency only. Startup playback does not require the Edge TTS service.

## Audio

The USB sound card is `USB PnP Audio Device`, with ALSA card ID `Device`. The persistent default is:

```text
pcm: plughw:CARD=Device,DEV=0
```

The source configuration is `config/alsa/asound.conf`. It is installed on both the host and inside Distrobox. The WAV chime uses `aplay`; MP3 speech uses `mpv` with `alsa/default`.
