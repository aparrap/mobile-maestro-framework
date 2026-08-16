#!/usr/bin/env bash
set -euo pipefail
PLATFORM="${1:-android}"
FLOW_DIR=".maestro/flows/${PLATFORM}"

if [[ ! -d "$FLOW_DIR" ]]; then
  echo "Unknown platform '$PLATFORM'. Use android or ios." >&2
  exit 1
fi

maestro test "$FLOW_DIR"
