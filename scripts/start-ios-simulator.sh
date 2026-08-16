#!/usr/bin/env bash
set -euo pipefail
DEVICE_NAME="${IOS_DEVICE_NAME:-iPhone 15}"
RUNTIME="${IOS_RUNTIME:-}" # optional, e.g. com.apple.CoreSimulator.SimRuntime.iOS-18-2

if [[ -n "$RUNTIME" ]]; then
  UDID=$(xcrun simctl list devices available --json | ruby -rjson -e "data=JSON.parse(STDIN.read); dev=data['devices'].values.flatten.find{|d| d['name']=='${DEVICE_NAME}' && d['isAvailable']}; puts dev && dev['udid']")
else
  UDID=$(xcrun simctl list devices available --json | ruby -rjson -e "data=JSON.parse(STDIN.read); dev=data['devices'].values.flatten.find{|d| d['name']=='${DEVICE_NAME}' && d['isAvailable']}; puts dev && dev['udid']")
fi

if [[ -z "${UDID:-}" ]]; then
  echo "Could not find available simulator named '$DEVICE_NAME'. Try: xcrun simctl list devices available" >&2
  exit 1
fi

xcrun simctl boot "$UDID" || true
open -a Simulator --args -CurrentDeviceUDID "$UDID"
xcrun simctl bootstatus "$UDID" -b
echo "iOS simulator ready: $DEVICE_NAME ($UDID)"
