#!/usr/bin/env bash
set -euo pipefail

VERSION="${THEAPP_VERSION:-v1.12.0}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ANDROID_DIR="$ROOT_DIR/apps/android"
IOS_DIR="$ROOT_DIR/apps/ios"
mkdir -p "$ANDROID_DIR" "$IOS_DIR"

APK_URL="https://github.com/appium-pro/TheApp/releases/download/${VERSION}/TheApp.apk"
IOS_URL="https://github.com/appium-pro/TheApp/releases/download/${VERSION}/TheApp.app.zip"

echo "Downloading TheApp ${VERSION} Android APK..."
curl -L "$APK_URL" -o "$ANDROID_DIR/TheApp.apk"

echo "Downloading TheApp ${VERSION} iOS simulator .app zip..."
curl -L "$IOS_URL" -o "$IOS_DIR/TheApp.app.zip"
unzip -oq "$IOS_DIR/TheApp.app.zip" -d "$IOS_DIR"

if [[ ! -d "$IOS_DIR/TheApp.app" ]]; then
  echo "Expected $IOS_DIR/TheApp.app after unzip, but it was not found." >&2
  exit 1
fi

echo "Done."
echo "Android: $ANDROID_DIR/TheApp.apk"
echo "iOS:     $IOS_DIR/TheApp.app"
