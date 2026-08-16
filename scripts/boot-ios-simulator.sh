#!/usr/bin/env bash
set -euo pipefail

echo "Available iOS simulators:"
xcrun simctl list devices available

json_file="$(mktemp)"
trap 'rm -f "$json_file"' EXIT
xcrun simctl list devices available -j > "$json_file"

selection="$(python3 - "$json_file" <<'PY'
import json
import re
import sys

with open(sys.argv[1], encoding="utf-8") as fh:
    payload = json.load(fh)

candidates = []
preferred_names = [
    "iPhone 17",
    "iPhone 17 Pro",
    "iPhone 16",
    "iPhone 16 Pro",
    "iPhone 16e",
    "iPhone SE (3rd generation)",
]
rank = {name: i for i, name in enumerate(preferred_names)}

for runtime, devices in payload.get("devices", {}).items():
    if ".iOS-" not in runtime:
        continue

    match = re.search(r"iOS-(\d+)(?:-(\d+))?(?:-(\d+))?$", runtime)
    version = tuple(int(part or 0) for part in (match.groups() if match else (0, 0, 0)))

    for device in devices:
        name = device.get("name", "")
        if not name.startswith("iPhone") or not device.get("isAvailable", False):
            continue

        candidates.append((version, -rank.get(name, 999), name, device["udid"]))

if not candidates:
    print("No available iPhone simulator was found on this runner.", file=sys.stderr)
    raise SystemExit(1)

# Highest iOS runtime first. Within that runtime, prefer a common iPhone model.
candidates.sort(reverse=True)
version, _, name, udid = candidates[0]
print(f"{udid}|{name}|{'.'.join(map(str, version))}")
PY
)"

IFS='|' read -r simulator_udid simulator_name simulator_runtime <<< "$selection"

echo "Selected simulator: $simulator_name ($simulator_udid), iOS $simulator_runtime"

state="$(xcrun simctl list devices | grep "$simulator_udid" || true)"
if [[ "$state" != *"(Booted)"* ]]; then
  xcrun simctl boot "$simulator_udid"
fi

xcrun simctl bootstatus "$simulator_udid" -b

if [[ -n "${GITHUB_ENV:-}" ]]; then
  {
    echo "IOS_SIMULATOR_UDID=$simulator_udid"
    echo "IOS_SIMULATOR_NAME=$simulator_name"
    echo "IOS_SIMULATOR_RUNTIME=$simulator_runtime"
  } >> "$GITHUB_ENV"
fi

echo "Booted simulator: $simulator_name"
