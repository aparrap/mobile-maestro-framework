#!/usr/bin/env bash
set -euo pipefail
AVD_NAME="${AVD_NAME:-Pixel_8_API_35}"
emulator -list-avds
emulator -avd "$AVD_NAME" -no-snapshot -no-boot-anim &
adb wait-for-device
adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true
adb shell input keyevent 82 || true
echo "Android emulator ready: $AVD_NAME"
