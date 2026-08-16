#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

case "${1:-}" in
  android)
    adb install -r "$ROOT_DIR/apps/android/TheApp.apk"
    ;;
  ios)
    xcrun simctl install booted "$ROOT_DIR/apps/ios/TheApp.app"
    ;;
  *)
    echo "Usage: $0 android|ios" >&2
    exit 1
    ;;
esac
