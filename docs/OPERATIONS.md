# Sparkie Operations

## Installation and Updates

Run full provisioning only for a fresh machine or changed system dependencies:

```bash
cd /home/sparkie/sparkie/sparkie_ws
./install.sh
```

For normal code and configuration changes:

```bash
./update.sh
```

To build a package and its dependencies:

```bash
./update.sh sparkie_base
```

The updater restarts `sparkie.service` only after a successful build.

## Service Management

```bash
sudo systemctl status sparkie.service --no-pager -l
sudo systemctl restart sparkie.service
sudo systemctl stop sparkie.service
sudo journalctl -u sparkie.service -f
sudo journalctl -u sparkie.service -b --no-pager -n 200
```

The checked-in unit is `systemd/sparkie.service`; the installed unit is `/etc/systemd/system/sparkie.service`.

## Hardware Checks

```bash
ls -l /dev/ttyACM0 /dev/ttyUSB0
cat /proc/asound/cards
distrobox enter -n ros-jazzy --no-tty -- aplay -l
```

Useful ROS checks inside Distrobox:

```bash
distrobox enter -n ros-jazzy
source /opt/ros/jazzy/setup.bash
source /home/sparkie/sparkie/sparkie_ws/install/setup.bash
ros2 node list
ros2 topic list
ros2 topic echo --once /sparkie/board/battery
ros2 topic echo --once /sparkie/scan
ros2 topic echo --once /sparkie/odom/ekf
```

## Boot Feedback Configuration

Edit:

```text
src/sparkie_base/sparkie_base/config/boot_sequence.yaml
```

Configurable values include:

- Online and offline phrases.
- Edge TTS voice, rate, volume, and pitch used during asset generation.
- Connectivity ping host and timeout.
- Chime enablement.
- LED effect code.

After editing, run:

```bash
./update.sh sparkie_base
```

The updater regenerates MP3 files only when the YAML file is newer than the cached files or an asset is missing.

To force regeneration:

```bash
touch src/sparkie_base/sparkie_base/config/boot_sequence.yaml
./update.sh sparkie_base
```

## Known Issues

- Webots simulation contains incomplete code and should not be assumed operational.
- `sparkie_nav/launch/loc.launch.py` references an `amcl.yaml` file that may be absent.
- Some package manifests do not declare every runtime dependency used by their launch files.
- The checked-in Docker Compose and development-container files include older Humble-era assumptions and are not the production startup path.
