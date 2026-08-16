# Maestro reporting

The framework deliberately executes each platform suite only once. The run produces a machine-readable JUnit report and the raw Maestro artifacts, then a small local renderer turns those results into a human-readable HTML dashboard and a GitHub Actions Markdown summary.

## Output structure

After `make test-ios`:

```text
reports/ios/
├── junit.xml
├── report.html
├── summary.md
└── artifacts/
    ├── ... Maestro screenshots ...
    ├── ... command metadata ...
    └── ... debug logs ...
```

Android uses the equivalent `reports/android/` directory.

## Local commands

```bash
make test-ios
make report-ios

make test-android
make report-android
```

The test target returns Maestro's original exit code. A failing suite therefore still fails locally and in CI, even though the report renderer runs after Maestro finishes.

## JUnit

The JUnit file is the canonical machine-readable result:

```bash
maestro test \
  --format junit \
  --output reports/ios/junit.xml \
  --test-output-dir reports/ios/artifacts \
  --debug-output reports/ios/artifacts \
  .maestro/flows/ios
```

Each executable scenario also declares metadata:

```yaml
properties:
  testCaseId: "MOB-AUTH-001"
  feature: "Authentication"
  priority: "P0"
  platform: "iOS"
```

This keeps the report ready for future test-management integrations.

## HTML dashboard

`scripts/render-maestro-report.py` parses the JUnit XML and discovers artifacts recursively. It generates:

- Overall pass/fail state.
- Test count, pass rate and total duration.
- One row per flow with duration and failure details.
- JUnit custom properties when present.
- Screenshot thumbnails when PNG/JPEG/WebP files are present.
- Download links for every file in the Maestro artifact directory.

It uses only the Python standard library; no pip installation is required.

## GitHub Actions

Both workflows run the tests with `continue-on-error: true` only for the execution step. This is intentional so reporting steps still run after a test failure.

The workflow then:

1. Appends `summary.md` to `$GITHUB_STEP_SUMMARY`.
2. Uploads the complete `reports/<platform>/` folder as a GitHub Actions artifact.
3. Explicitly fails the job when the Maestro execution step failed.

This gives developers a readable summary without accidentally turning failing mobile tests into a green build.

## Native Maestro HTML

Maestro also supports its own HTML report format:

```bash
maestro test --format html --output reports/ios/maestro-native.html .maestro/flows/ios
```

The framework does not run this by default because it would require a second execution to also obtain JUnit. The custom HTML dashboard is therefore rendered from the same single JUnit + artifact run used by CI.
