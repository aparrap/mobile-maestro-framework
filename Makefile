.PHONY: download android-device ios-device install-android install-ios validate \
        test-android test-ios test-all report-android report-ios clean-reports studio

download:
	./scripts/download-theapp-assets.sh

android-device:
	./scripts/start-android-emulator.sh

ios-device:
	./scripts/start-ios-simulator.sh

install-android:
	./scripts/install-apps.sh android

install-ios:
	./scripts/install-apps.sh ios

validate:
	./scripts/validate-maestro-flows.sh

test-android: validate
	./scripts/run-maestro.sh android

test-ios: validate
	./scripts/run-maestro.sh ios

test-all: test-android test-ios

report-android:
	@echo "Android HTML report: $$(pwd)/reports/android/report.html"
	@if [ -f reports/android/report.html ]; then open reports/android/report.html 2>/dev/null || xdg-open reports/android/report.html 2>/dev/null || true; else echo "Run 'make test-android' first."; exit 1; fi

report-ios:
	@echo "iOS HTML report: $$(pwd)/reports/ios/report.html"
	@if [ -f reports/ios/report.html ]; then open reports/ios/report.html 2>/dev/null || xdg-open reports/ios/report.html 2>/dev/null || true; else echo "Run 'make test-ios' first."; exit 1; fi

clean-reports:
	rm -rf reports

studio:
	maestro studio
