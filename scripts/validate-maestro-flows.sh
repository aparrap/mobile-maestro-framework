#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILED=0

while IFS= read -r -d '' file; do
  # config.yaml and data files are not executable Maestro flows.
  case "$file" in
    */.maestro/config.yaml|*/.maestro/data/*) continue ;;
  esac

  if ! grep -q '^appId:' "$file"; then
    echo "Missing appId configuration: ${file#$ROOT_DIR/}" >&2
    FAILED=1
  fi

  if ! grep -q '^---$' "$file"; then
    echo "Missing --- separator: ${file#$ROOT_DIR/}" >&2
    FAILED=1
  fi
done < <(find "$ROOT_DIR/.maestro" -type f -name '*.yaml' -print0)

if [[ "$FAILED" -ne 0 ]]; then
  exit 1
fi

echo "Maestro flow structure looks valid."
