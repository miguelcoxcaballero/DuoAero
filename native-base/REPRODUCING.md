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
`EMITTED <class>` or `ERROR <class>`, then disposes its subscriptions. Only classes and Boolean values are logged, without
account payloads or tokens. It does not replace repository values or
set initialization booleans. Subscription itself can activate cold flows, so this
is an instrumented diagnostic, not a passive trace or proof of normal startup.

`diagnostic_completed=true` means state collection completed only. A nonzero adb
exit status is not the only failure signal: inspect the instrumentation result
and stream. Engine state `do10` fields or a blank screen remain a
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

## Runtime comparison, 2026-11-01 (Europe/Madrid)

[Run 41250570051](https://github.com/miguelcoxcaballero/DuoAero/actions/runs/41250570051)
built and installed the original-runtime diagnostic on an accelerated Android 36
emulator. The three reports are retained in `evidence/2026-11-01/`. Its successful
workflow result means **diagnostic collection succeeded**, not lesson acceptance.

| Synthetic profile course | Course flow | User/streak flows | Session |
| --- | --- | --- | --- |
| Aerospace | `fz8` (unsupported course) | Both emitted | `do10` |
| Original `MATH_BT` ID | No emission during observation | Both emitted | `do10` |
| No course | `ez8` | Both emitted | `do10` |

All three resumed the original SessionActivity and kept all initialization flags
false. The Aerospace screenshot, captured before instrumentation finished, was
visually inspected and is blank. Merely switching the course ID does not fix the
session. For Aerospace, the previous hypothesis that one of the three loader
inputs never emits is disproven by this run. Other initializer operands and the
validity of emitted course state still require investigation.

The unaccelerated local container emulator suffered an Android system ANR and
package-install timeout; no app-runtime acceptance is claimed from that machine.
The CI workflow publishes separate small evidence and full diagnostic artifacts.
Neither is a production release, and neither updates A/B catalogs.

[Extended run 41250852462](https://github.com/miguelcoxcaballero/DuoAero/actions/runs/41250852462)
measured the other operands of the initializer's final Rx zip. For Aerospace,
the combined loader emitted `jn7` and all measured configuration operands emitted
except `session-experiments`. That experiment-treatment stream did not emit for
any of the three profiles. `vm.S1.a` also did not emit, but the final initializer
uses the separate `vm.S1.d` flow, which did emit. Reports are in
`evidence/2026-11-01/initializer-dependencies.txt`.

The optional `-e experiments native-defaults` probe supplies the original
`ExperimentsState()` empty entry map, wrapped in the original per-user `gsd` and
`vir` models, to both legacy and new experiment repositories before launch.
The original client experiment selects the implementation, and the original
code resolves treatment conditions. This tests one dependency; it is not a
production offline adapter. Its measured effect is documented below.


[Default-entry run 41251414547](https://github.com/miguelcoxcaballero/DuoAero/actions/runs/41251414547)
confirmed that the original experiment treatment stream emits when those default
models are supplied. The engine changed from `do10` to `eo10`, whose `e` field is
an original Session model. The screenshot was inspected and remains blank; all
view initialization flags remain false. This resolves one input wait in the
isolated probe but does not establish a rendered or playable lesson.

Correction to earlier shorthand: `ou10.s2` is optional pre-session reward-road
state, and `ou10.l4` is an auxiliary field. Their nullness alone does not establish
whether a Session has loaded. Inspect the engine and actual UI separately.

The next probe observes the original loading/view streams `w2`, `x2`, `i3`,
`o3`, `q3`, preload completion and loading-indicator readiness. Its screen evidence
also includes the accessibility tree for the isolated target package. Neither
readiness values nor view visibility are forced. Screenshots from a previous
variant are deleted before each run to avoid mislabeling stale evidence.

[View-readiness run 41252204375](https://github.com/miguelcoxcaballero/DuoAero/actions/runs/41252204375)
confirmed a loaded original Session with 15 challenges for both Aerospace and
no-course profiles with default experiment entries. `w2` emitted `eo10`, `o3`
emitted false and `i3` emitted `sql`, but the pre-render preparation completion
stream `in10.u` did not emit. Consequently `q3` and `x2` did not emit. The captured
accessibility trees contain 15 nodes with no question text. This is still not a
rendered lesson.

The next comparison measures the inputs of `in10.e` and installs the same
synthetic profile in `Instrumentation.onCreate` (`-e bootstrap early`) versus
`onStart`. The earlier phase tests whether already-created repositories retain
references to the initial empty profile. Both variants keep the original
application lifecycle, session controller, preparation logic and readiness flags.

[Preparation run 41252766236](https://github.com/miguelcoxcaballero/DuoAero/actions/runs/41252766236)
found that early and late profile installation both leave the original pre-lesson
selector `wn10.a` without emission. Other directly measured preparation inputs,
including the native leagues state and experiment records, emit. The complete
recent-login-derived stream was not independently measured. The engine still
loads only the original reference Session; there is no rendered Aerospace lesson.
Reports for both timings are retained in the evidence directory. The next probe
observes the selector's original inputs without supplying a completion signal.

[Pre-lesson input run 41253267825](https://github.com/miguelcoxcaballero/DuoAero/actions/runs/41253267825)
found that `p6d.h` did not emit for either profile timing; the other nine measured
`wn10.a` operands emitted. Static tracing shows `p6d.h` requires a loaded
`CoursePathInfo` through `bp1.j`, which filters out unsupported/no-course states.
The previous `fz8` emission therefore does not satisfy this separate dependency.
The screen remains blank; reports are retained under `before-lesson-*.txt`.

The next diagnostic uses original `MATH_BT` with default experiment entries,
comparing no cache input with `-e course_cache native-minimal`. The latter decodes
original `CoursePathInfo` and an **empty** `CoursePathSection`, then writes them
using original resource descriptors (`tt8`/`qy8`), `nrx.t` and `prx.x0`, awaiting
actual write completion. No flow, readiness flag or view is replaced. The empty
section has no learning-path units and is not the Aerospace course. This test
still opens the original hardcoded math reference session.

[First cache run 41253808775](https://github.com/miguelcoxcaballero/DuoAero/actions/runs/41253808775)
failed the explicit Math `CoursePathInfo` type guard **before any cache write**.
The synthetic course omitted `subject`, whose original serializer defaults to
`language`; the ID `MATH_BT` does not select the serialized model type. The
corrected diagnostic now supplies `subject: math` and required `topic: math` in
both the user's course summary and cached course info. Earlier MATH_BT-only
comparisons must not be interpreted as a valid math-profile test.

The build also packages the handoff's 19-question `aerospace_lesson.json` under
`assets/hardcoded_sessions/duoaero/`. `-e lesson aerospace` selects it with the
original Hardcoded SessionStartParams. The original math asset is unchanged.
Local compilation and original-entry integrity passed; no Aerospace question
has yet been shown or answered. The next CI compares the corrected math profile
with/without native cache input, then the Aerospace asset with that same input.

[Corrected cache run 41254218442](https://github.com/miguelcoxcaballero/DuoAero/actions/runs/41254218442)
completed original native cache writes and **rendered actual native questions**.
Without cache input the screen remains blank. With it, `bp1.j` emits `mt8`,
`p6d.h` emits true, preparation completion emits `xv80`, `q3` emits `vql`, and
`x2` emits `eo10`. Readiness a/b become true through original code; c..i remain
false, demonstrating that all nine flags being true is not a rendering criterion.

The original reference shows its first math matching question. The Aerospace
asset shows its first exam question and four answer options; the inspected
screenshot and 68-node accessibility tree confirm rendering. However the original
AssistFragment prefixes the exam stem with “How do you say ...”, which is wrong
for this course. No answer or session completion has yet been tested. Course
cache data contains an empty section, and profile setup still requires test
instrumentation: this is not a standalone playable app or release acceptance.

The next diagnostic clicks the first assist answer and original submission
button, capturing each visible stage. A second asset uses the original
mathChallengeBlob `selectOne` layout for 12 plain-choice questions plus the bank's
rich-text choices, preserving question text and the original renderer. Both
variants remain diagnostic inputs; grading, LaTeX layout and text overflow need
runtime evidence. Original APK entry integrity and local compilation pass.
