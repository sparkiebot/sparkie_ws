#!/bin/bash

ros2 run webots_ros2_importer xacro2proto \
  --input=$(ros2 pkg prefix sparkie_description --share)/urdf/sparkiebot.xacro \
  --disable-mesh-optimization \
  --output=protos/sparkiebot.proto