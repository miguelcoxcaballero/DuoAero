# Original-runtime diagnostics

These commands build diagnostic APKs, not a playable course or a production release.
Read `CONTINUE_DUOAERO.txt` before continuing. The original application and session
controllers remain in use; the installer vendor is unchanged.

## Portable build

Requires JDK, Android platform 36, build-tools 35.0.0, platform-tools, apktool
2.12.1 and Python FontTools. The scripts use `JAVA_HOME` or Java on PATH.
Set the following environment variables to local paths (Windows defaults remain
available in `runtime_config.py`):

- `ANDROID_HOME`: SDK directory (`ANDROID_SDK_ROOT` also accepted).
- `DUOAERO_APK`: supplied original 6.103.5 APK.
- `DUOAERO_DECODED`: resource decode containing AndroidManifest.xml.
- `DUOAERO_SMALI`: full apktool decode containing smali_classes4.
- `DUOAERO_APKTOOL`: apktool JAR.
- `DUOAERO_WORK`: generated build directory outside the source tree.

The full decode can also serve as the resource decode. Download handoff assets
from release `handoff-2026-10-31-native-runtime-1` and verify against
`handoff-artifacts.json`. Extract the two JSON fixtures under
`native-base/tests/fixtures/`. Never add account data or credentials there.

If `build/debug.p12` is absent, create a **local test key**:

```sh
mkdir -p build
keytool -genkeypair -keystore build/debug.p12 -storetype PKCS12 \
  -storepass android -keypass android -alias androiddebugkey \
  -dname 'CN=DuoAero Local Diagnostic' -keyalg RSA -keysize 2048 -validity 3650
python native-base/build.py
python native-base/test_integrity.py
python native-base/test_models.py --build-only
```

Install both generated APKs on a disposable emulator with the same test signer.
Do not overwrite or uninstall a user's production application. Omit
`--build-only` to install instrumentation through the configured SDK's adb.

## Session dependency observation

```sh
adb install -r "$DUOAERO_WORK/DuoAero-native-base-test.apk"
adb install -r "$DUOAERO_WORK/tests-signed.apk"
adb shell am instrument -w \
  com.duoaero.nativebase.tests/com.duoaero.nativebase.UserSessionProbe
```

`SessionDependencies` observes the actual `ou10.j` loader's course, user and
streak inputs using the original Flow-to-Rx bridge. It reports `NO_EMISSION`,
`EMITTED <class>` or `ERROR <class>`, then disposes its subscriptions. No values,
account payloads or tokens are logged. It does not replace repository values or
set initialization booleans. Subscription itself can activate cold flows, so this
is an instrumented diagnostic, not a passive trace or proof of normal startup.

`diagnostic_completed=true` means state collection completed only. A nonzero adb
exit status is not the only failure signal: inspect the instrumentation result
and stream. Engine state `do10`, null session fields or a blank screen remain a
failure to initialize a playable lesson, even when diagnostic collection succeeds.

## Source findings

For original APK SHA-256
`1468b090287a33810bcd2e856ac5fbb6e1d9ec241e3d1ee8f5ed42f8fd66a966`:

- `nnk.a` combines `bp1.h(null, true)`, `rs1.f()` and `xa90.a()` when
  `PathLevelSessionEndInfo` is absent, as in the probe.
- Course output is `gz8`, a course/path state. It is not a `CourseProgressSummary`
  or simply a deserialized full course. `gz8.b()` accesses `CoursePathInfo` and
  `gz8.a()` accesses the active `CoursePathSection` when present.
- The optional string accepted by `bp1.h` is compared to
  `CoursePathSection.a` by `vm1`; treating it as a course ID is incorrect.
- `rs1.f()` reads lazy `u` (the probe supplies `wd90(User)`).
- `xa90.a()` reads lazy `n`; its upstream includes user state, local streak state
  and debug overrides. It can consult the persistent streak repository.
- `c4x` combines these into `jn7`. A flow emitting does not prove its state is
  suitable for a lesson, nor that subsequent initialization completes.

These are static findings. Runtime observations and UI acceptance must be recorded
separately; none of them proves rendering, grading, persistence or session end.
