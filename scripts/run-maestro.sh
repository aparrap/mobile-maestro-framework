#!/usr/bin/env bash
set -uo pipefail

PLATFORM="${1:-android}"
FLOW_DIR=".maestro/flows/${PLATFORM}"
REPORT_DIR="${MAESTRO_REPORT_DIR:-reports/${PLATFORM}}"
ARTIFACT_DIR="${REPORT_DIR}/artifacts"
JUNIT_FILE="${REPORT_DIR}/junit.xml"
HTML_FILE="${REPORT_DIR}/report.html"
SUMMARY_FILE="${REPORT_DIR}/summary.md"

if [[ "$PLATFORM" != "android" && "$PLATFORM" != "ios" ]]; then
  echo "Unknown platform '$PLATFORM'. Use android or ios." >&2
  exit 1
fi

if [[ ! -d "$FLOW_DIR" ]]; then
  echo "Flow directory not found: $FLOW_DIR" >&2
  exit 1
fi

if ! command -v maestro >/dev/null 2>&1; then
  echo "Maestro CLI is not installed or not available on PATH." >&2
  exit 127
fi

# Keep one deterministic report directory per platform. CI artifacts stay clean,
# while a local developer always knows where the newest report is.
rm -rf "$REPORT_DIR"
mkdir -p "$ARTIFACT_DIR"

set +e
maestro test \
  --format junit \
  --output "$JUNIT_FILE" \
  --test-output-dir "$ARTIFACT_DIR" \
  --debug-output "$ARTIFACT_DIR" \
  "$FLOW_DIR"
TEST_EXIT=$?
set -e

# Reporting should not mask the original Maestro exit code. If Maestro produced
# a malformed/partial JUnit file, surface that but still return TEST_EXIT below.
if command -v python3 >/dev/null 2>&1; then
  python3 scripts/render-maestro-report.py \
    --junit "$JUNIT_FILE" \
    --artifacts "$ARTIFACT_DIR" \
    --html "$HTML_FILE" \
    --markdown "$SUMMARY_FILE" \
    --platform "$PLATFORM" || echo "Warning: HTML/Markdown report rendering failed." >&2
else
  echo "Warning: python3 not found; JUnit and Maestro artifacts were still generated." >&2
fi

echo
echo "Reporting"
echo "  JUnit:    $JUNIT_FILE"
echo "  HTML:     $HTML_FILE"
echo "  Summary:  $SUMMARY_FILE"
echo "  Artifacts:$ARTIFACT_DIR"

exit "$TEST_EXIT"
