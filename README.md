# Mobile Maestro Framework — Android + iOS E2E Testing

A scalable Maestro test automation framework for a cross-platform sample app (`TheApp`) with Android and iOS flows, reusable screen-object subflows, local setup scripts, and GitHub Actions examples.

`TheApp` is an open-source React Native test app by Appium Pro. It publishes Android `.apk` and iOS simulator `.app.zip` assets in GitHub Releases. The tested app id is `com.appiumpro.the_app` on both Android and iOS.

## What this framework demonstrates

- Cross-platform Maestro flow structure.
- POM-style screen objects using reusable `runFlow` subflows.
- Stable identifiers using React Native `testID` / accessibility labels.
- Local execution on Android Emulator and iOS Simulator.
- CI-ready workflows for GitHub Actions.
- Four-plus maintainable scenarios per platform:
  - Home smoke/menu visibility.
  - Echo message saved to local storage.
  - Valid user login.
  - Clipboard round trip.
  - Long-list item selection.

## Prerequisites

### All platforms

```bash
curl -Ls "https://get.maestro.mobile.dev" | bash
export PATH="$HOME/.maestro/bin:$PATH"
maestro --version
```

### Android

Install Android Studio, then create an AVD from **Device Manager** or via CLI. Ensure these tools are on your path:

```bash
sdkmanager --list
avdmanager list avd
emulator -list-avds
adb devices
```

### iOS

Install Xcode from the Mac App Store, open it once, and install at least one iOS Simulator runtime. Then validate:

```bash
xcode-select -p
xcrun simctl list devices available
open -a Simulator
```

## Download the demo app binaries

```bash
make download
```

This downloads:

```text
apps/android/TheApp.apk
apps/ios/TheApp.app
```

You can override the release:

```bash
THEAPP_VERSION=v1.12.0 make download
```


## Maestro flow file requirement

Every YAML file executed directly or through `runFlow` is a complete Maestro Flow. It therefore needs a configuration section and the `---` separator, including reusable page/POM subflows. For this sample app, reusable page files start with:

```yaml
appId: com.appiumpro.the_app
---
```

Run `make validate` to catch a missing flow header before launching the suite.

## Run locally on Android

```bash
make android-device       # or manually start an existing AVD
make install-android
make test-android
```

Manual equivalent:

```bash
emulator -avd Pixel_8_API_35 -no-snapshot -no-boot-anim &
adb wait-for-device
adb install -r apps/android/TheApp.apk
maestro test .maestro/flows/android
```

## Run locally on iOS

```bash
make ios-device           # boots default iPhone 15 simulator
make install-ios
make test-ios
```

Manual equivalent:

```bash
xcrun simctl boot "iPhone 15" || true
open -a Simulator
xcrun simctl install booted apps/ios/TheApp.app
maestro test .maestro/flows/ios
```

## Use Maestro Studio to inspect identifiers

```bash
maestro studio
```

Studio gives you a visual inspector and generates YAML steps while you interact with the device. For CLI inspection:

```bash
maestro hierarchy
```

For this sample app, identifiers come from React Native `testProps`, which maps each locator to both `testID` and `accessibilityLabel`. Examples in the source app include `Echo Box`, `Login Screen`, `messageInput`, `username`, `password`, `loginBtn`, `setClipboardText`, and `refreshClipboardText`.

## Folder structure

```text
.mobile-maestro-framework/
├── .github/workflows/        # Android + iOS CI examples
├── .maestro/
│   ├── config.yaml           # global config placeholder
│   ├── data/                 # test data notes
│   ├── flows/                # executable specs by platform
│   │   ├── android/
│   │   └── ios/
│   ├── pages/                # POM-style screen object subflows
│   │   ├── home/
│   │   ├── echo/
│   │   ├── login/
│   │   ├── clipboard/
│   │   └── list/
│   └── common/               # shared helpers
├── apps/                     # downloaded app binaries, gitignored
├── docs/                     # locator and framework notes
├── scripts/                  # device, install, and run helpers
├── Makefile
└── README.md
```

## POM model in Maestro

Maestro does not use classes like Appium/WebdriverIO. The equivalent maintainable pattern is a **Screen Object Model**:

- A test flow represents one scenario.
- A page subflow represents one reusable screen action or assertion.
- Parameters are passed using `env` values.
- Stable element identifiers are hidden inside page subflows where possible.

Example:

```yaml
# Scenario
- runFlow: ../../pages/home/open-login.yaml
- runFlow:
    file: ../../pages/login/login-success.yaml
    env:
      USERNAME: "alice"
      PASSWORD: "mypassword"
```

## Run one scenario

```bash
maestro test .maestro/flows/android/03_login_success.yaml
maestro test .maestro/flows/ios/03_login_success.yaml
```

## CI

This repository includes two starter workflows:

```text
.github/workflows/maestro-android.yml
.github/workflows/maestro-ios.yml
```

Android runs on Ubuntu with an emulator. iOS runs on a macOS runner with an iOS Simulator.

## Notes for real projects

- Ask mobile developers for stable `testID` / accessibility identifiers during feature development.
- Add IDs to all controls used in release-critical flows: onboarding, login, checkout, payment, account, settings.
- Keep visible-text assertions for user-visible copy, but avoid relying on copy for every action.
- Use real devices for camera, biometrics, push notification, performance, network, and hardware integration coverage.
- Keep Maestro as the fast functional-smoke layer. Use Appium when you need complex protocol-level control, custom gestures, cloud grid breadth, or deeper native hooks.

## Reporting

Every normal test command now generates reports automatically:

```bash
make test-ios
make test-android
```

The output is written to:

```text
reports/
├── ios/
│   ├── junit.xml      # CI / test-management friendly result
│   ├── report.html    # human-readable dashboard
│   ├── summary.md     # GitHub Actions job summary
│   └── artifacts/     # screenshots, logs, command metadata
└── android/
    └── ... same structure ...
```

Open the latest local report with:

```bash
make report-ios
make report-android
```

Clean generated output with:

```bash
make clean-reports
```

The suite is executed **once**. Maestro writes JUnit plus its test/debug artifacts, and `scripts/render-maestro-report.py` converts that same result into HTML and Markdown. This avoids running expensive simulator/emulator tests twice just to obtain two report formats.

Each executable flow contains report metadata such as:

```yaml
properties:
  testCaseId: "MOB-AUTH-001"
  feature: "Authentication"
  priority: "P0"
  platform: "iOS"
```

See [`docs/reporting.md`](docs/reporting.md) for the full reporting architecture.

### GitHub Actions reporting

Both included workflows now:

1. Run Maestro and preserve the real test exit code.
2. Generate JUnit, HTML, Markdown, screenshots and debug artifacts.
3. Publish `summary.md` into the GitHub Actions **Job Summary**.
4. Upload the complete platform report as a downloadable Actions artifact.
5. Fail the job after publishing the evidence when the Maestro suite fails.

This gives you a red/green CI signal without losing the failure evidence needed to diagnose the run.
