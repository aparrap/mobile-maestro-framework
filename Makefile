.PHONY: download android-device ios-device install-android install-ios test-android test-ios studio

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

test-android:
	./scripts/run-maestro.sh android

test-ios:
	./scripts/run-maestro.sh ios

studio:
	maestro studio
