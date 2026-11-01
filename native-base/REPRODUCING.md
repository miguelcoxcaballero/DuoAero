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

[Interaction run 41254902679](https://github.com/miguelcoxcaballero/DuoAero/actions/runs/41254902679)
shows actual native correct-answer feedback after tapping “Low delivery times.”:
the option becomes green and the graded Continue button appears. The automation
then failed its old `submitButton` locator: the graded footer is Compose and its
Continue node has no resource ID. No successful advancement is claimed from this
run. The revised locator uses the native button's exact visible text, restricted
to the isolated target package.

The original Math `selectOne` renderer also displays the first exam question
without the language translation prefix, with the complete stem and all four
choices visible. This validates that initial layout, not native Math grading or
formula rendering. The next probe selects correct and wrong answers through
native Math cards, clicks Check/Continue, and captures the next formula question.
Screenshots and accessibility evidence are retained alongside these reports:
`first-aerospace-native.png`, `first-native-correct-answer.png`, `native-selectone.png`.


[Grading diagnostic 41255504181](https://github.com/miguelcoxcaballero/DuoAero/actions/runs/41255504181)
advanced the Assist fixture to its second question. However **both Math answer
attempts failed native grading**: screenshots show “Oops! Something went wrong”
and “Let’s skip this exercise for now”. Continue skips to the next formula;
the collection marker and next-option presence do not establish successful grading.
The Breguet stem and four fractional answer choices visibly render, with layout
and font-scale QA still pending. The interaction probe now rejects this error UI.

Source trace: `s4p.a` (MathSessionCoordinator) waits for the original loaded Session
and initializes `g5l.b` for the SESSION execution context only if `Session.Type.F1()`
returns a skill ID. `GLOBAL_PRACTICE` returns null. The next fixture uses the
original `MATH_LESSON` type, metadata and skillId, matching the original reference.
The probe also reports native sandbox presence and registered execution contexts.
This is an input correction, not an injected grader or forced readiness state.

`path_adapter.py` maps the existing 42 topic nodes and 81 lessons into native Math
path data, validates that all 1200 IDs appear exactly once, and preserves source
lesson grouping. `course_cache=native-full` writes those original decoded models
through the same cache descriptors. `capture_home=true` finishes the diagnostic
SessionActivity and captures the resumed original activity. Native path decoding,
home rendering and node navigation are separate outcomes, all pending this test.


[Typed Math run 41256513404](https://github.com/miguelcoxcaballero/DuoAero/actions/runs/41256513404)
initializes the original JavaScript sandbox and SESSION context. Native correct
feedback is green (“Excellent!”), and Continue advances to the Breguet question.
A wrong answer shows red incorrect feedback and the complete Aerospace explanation.
The wrong-answer automation fails only at the next locator: that native footer
says **GOT IT**, not CONTINUE. Screenshots were inspected; CI's failed diagnostic
must not be reported as a passing suite or a successful wrong-answer advancement.

The original serializers also accept the full 42-unit course section, and both
native cache writes complete. Finishing the test SessionActivity returns to the
original LaunchActivity, which remains on its green splash (14 accessibility
nodes). No path UI, node navigation, progress or standalone bootstrap is verified.
Evidence: `typed-math-correct.png`, `typed-math-wrong.png`, `typed-home-splash.png`
and the corresponding `typed-*.txt`/JSON files.

The next probe reads the visible original MathBlobSelectOneFragment's E0 result
and its original CorrectnessState, asserting CORRECT or INCORRECT without writing
it. The all-answer sequence uses expected answers from the source bank, exercises
all 15 original controls, and captures each graded state plus the screen after
last Continue. Passing all answers alone is not session completion or persistence.
Separate subscriptions observe original launch/check dependencies without forcing
routing or readiness. Expected selections are packaged in instrumentation only.


[Full-answer run 41257088819](https://github.com/miguelcoxcaballero/DuoAero/actions/runs/41257088819)
asserts **15 consecutive CORRECT results from the original visible fragments**,
including all three rich questions. A separate wrong answer asserts INCORRECT,
and the native GOT IT control advances. Screenshots and original-state assertions
support these grading results; the diagnostic CI passed.

After final Continue and eight seconds, the screen shows loading dots only.
**This is not a completed lesson**, saved progress or restart/resume acceptance.
Rich screenshots also reveal fractions extending beyond answer card borders in
the long lift-coefficient question. Preserve this as an unresolved layout defect.
Evidence is stored as `full-*`, including after-last-answer and rich-question PNGs.

The home remains on splash. Its bridge d/f/j, launch K/L/S and synthetic user emit;
N/V do not. LaunchCheckViewModel.g deliberately returns an empty observable, so
its missing emission is not sufficient evidence of a dependency failure.
Source tracing identifies `xsl` waiting on `fm1.u` (Config) before login routing.
Next comparison writes original default Config (`{}`, using its original defaults)
through `fm1.j.a()` / `w58`, using the native cache. Provider is original mm9.w0.
No readiness or routing flags are forced. The full-answer probe also seeds that
Config before launch, then reports the original final engine class/field types
and bounded whitelisted synthetic endpoint counts (no query strings, headers,
bodies or credentials). The baseline splash variant runs first to preserve its
before/after comparison. Timed-out probes retain evidence and still fail markers.

The bank adapter now uses native selectOne for ordinary choices as well as rich
choices, and wraps sessions as MATH_LESSON with a skill ID. Five gap/order items
remain explicit unsupported errors. CI regenerates 1195 fixtures and checks them
with the original serializer; that model check remains distinct from UI grading.
ModelProbe blocks network before original Application.onCreate for isolation.


## Config comparison and completion dependency tracing (2026-11-01)

Run 41258147892 (ce5db0207d601c8e33b022c9e311b8356cd96303) passed the
regenerated 1195 Math-typed model fixtures and the 15 original CORRECT states.
Default Config was already emitting before the explicit native cache write.
Writing Config did not unblock the splash or final loading dots. The final
accessibility tree contains sessionEndViewPager: SessionEndFragment is present,
but no completed summary is visible. No progress persistence is established.

The next probes observe original SessionEndConfigureArgs, sequence state,
existing repository flows, onboarding completion and saved accounts. A separate
comparison also writes the synthetic User through the original FIRST_PERSON
resource (f990 -> py8 -> native cache), feeding existing cache observers.
This does not implement real authentication or a standalone app bootstrap.

The opt-in named-flow hook in g9q records bounded references to original qdf
inputs, only when localOnly and captureNativeFlows are both true. It never
changes emissions or grades. The added hook intentionally changes classes.dex;
classes4.dex still contains the original OkHttp bridge hook. All other original
DEX files and screens remain covered by integrity verification. Observing cold
flows may activate them; this is diagnostic collection, not a passive trace.

REA (https://github.com/morluto/rea), suggested by the user, is being evaluated
locally for Android reference tracing. It uses JADX; static reference results
are not runtime acceptance. No external REA service receives the APK.


Run 41259465021 confirms the final fragment has no SessionEndConfigureArgs,
sequence state d110, no saved config, and ui-ready=false. Onboarding completion
and SavedAccounts both emit, so their non-emission is not the splash cause.
Static source identifies a concrete end guard: c4x.A changes an all-null
UserStreak to null, and gr10.b exits before configuring the summary when
eo10.d is null. The new diagnostic seeds an explicit zero-length lifetime
streak through original ex50/kji cache before launch. It does not set completion
flags, award XP or invent learned days. Runtime effect is pending.

Choice/multi/matching adapters now carry difficulty stars; missing U+2605/U+2606
font outlines are added from the existing OFL donor. All previous font mappings
remain intact. Build/integrity and 48 JS grading cases pass; visible stars and
end behavior must still be checked on the emulator.

The next startup comparison also feeds synthetic qwn identity through the
original ygc case-0 pure reducer, wrapped by d490/b490 into the native cache.
This updates existing observers of chc.a as well as the diagnostic lazy holder;
it is not real authentication. Source inspection distinguishes this reducer
from ygc case 1, which performs login/logout side effects. The probe reports
launch navigation state and enum names, and captures the final screen again
after observing session-end inputs. Runtime result remains pending.


Run 41260263363 verifies the zero-day UserStreak fix: engine.d is non-null,
SessionEndConfigureArgs emits and is saved. The 15 original CORRECT results
still pass. The final summary remains blocked: named inputs goalsSchema,
dailyQuests, preSessionState, userFollowState and resurrectedLoginRewardsState
(and their derived composites) do not emit. The native source shows goalsSchema
is also an input to the pre-session snapshot. No completion or persistence is
claimed. The first-question screenshot still does not show difficulty stars.

The next comparison supplies the original empty GoalsSchemaResponse through
hji/mji/lji before answers, using the actual emitted uhi scope. At session end
it supplies an original UserSocialProfile with zero followers/following and an
empty list through sb90/ga90/u12. These represent unconfigured optional features
of the isolated account. They do not award progress or replace readiness.
The social write is an explicit diagnostic input before end-flow observation;
it is not passive instrumentation. Runtime effect is pending.

Run 41260735970 failed with a real process crash after native login cache input:
PackageManager.NameNotFoundException: com.duolingo, from h4t -> gnv. This
original update-time lookup had retained the old installed package name. The
build now changes only that exact getPackageInfo constant to its manifest
package, with a single-anchor assertion and restoration of original smali.
It does not suppress the exception or falsify PackageInfo. Revalidation pending.

The next rich-text comparison uses MTMath's supported \star command (U+22C6,
now included in the font overlay) instead of raw U+2605 inside text. Options
use native \textstyle to reduce fraction height. These preserve mathematical
content and original controls; screenshots must verify stars and card bounds.
All 48 JS grading combinations, build and original-entry integrity pass locally.
Instrumentation locators allow that presentation prefix while expected answers
still come independently from the source bank.

Run 41261324886 stopped in instrumentation: LocalCourseCache.first requested
mao.b(qdf,rn8), but the actual declared parameter is pn8 (the dispatcher base
class). This was a reflection binding error, not an app acceptance result.
The binding now matches original smali and the existing dependency observer.

Native course/goals/social input now occurs before LaunchActivity, using original
component providers mm9.O2 (bp1), v6 (hji) and J4 (sb90), each with a class guard.
The goals resource uses its actual emitted uhi context; the social profile and
both follower/following lists are empty. No feature cache writes occur inside
the end observer. This tests the initialization order needed by a normal app
bootstrap; it does not itself implement the standalone bootstrap.

### Early native inputs and visible stars (2026-11-01)

Run `41261900086` at `e9cb9bd4` resolves all previously missing named end flows; `c110`, UI-ready true and original Claim XP button are visible. Its Rive animation/stats area remains blank. Fifteen native correct grades and separate incorrect/Got It still pass. Native star macro visibly renders difficulty; inline fractions shrink, but the long stem overlaps the first card after grading. Full-path probe fails because WelcomeFlowActivity opens over the session, not a process crash. Next patch routes an already installed local course through original home initialization at zero XP, without inventing progress; captures pre-answer layouts and renderer diagnostics. Runtime acceptance pending.

The next diagnostic compares ANGLE/SwiftShader GLES (`-gpu swangle`) against the
previous emulator's GLES 3.0 SwiftShader renderer, keeping the APK's original Rive
runtime and assets. Attached renderer state is read without forcing playback. It
also clicks the actual Claim XP button and tests native profile cache writes with
repository flow holders untouched. These are pending checks, not release claims.

A local-course-only modifier now bounds native text prompts to 30% of screen height (120–240 dp) and uses the original Compose vertical scroll/remembered scroll state. Text and font size are preserved, scroll position is keyed by prompt, answer cards and grading remain original. Instrumentation requires a real scroll action on the long rich prompt and captures before/after. Local assembly/integrity passes (18,245 unchanged entries); device layout acceptance is pending.

Run `41262635825` (`686f5520`) passes diagnostic collection and still grades all 15 answers. The original session-end sequence contains `SessionComplete` and Claim XP; its Rive content is blank. Renderer reports “no interlock mode supports this frame”, then depth/stencil fallback. The before-answer long-formula screenshot fits all options; after grading the feedback footer squeezes the prompt/cards. Startup still opens the native Math Student/Adult learner survey. Original `vza0` independently requests it whenever the current Math course XP is zero. The next scoped enrollment change returns its original empty welcome request only after installing the local course, retaining zero XP.

Run `41262902147` (`e4816751`) visibly renders the original Lesson complete summary: character, 15 XP, 100% and 0:57. ANGLE/SwiftShader emulator graphics resolves the previously blank Rive views; app animation code/assets unchanged. Claim XP action succeeds and LaunchActivity resumes, but the captured screen still shows the summary, so return-to-path and persistence are not established. Native profile cache alone (no replacements of rs1/bxn flow holders) renders the first question. Experiment defaults are still supplied by the diagnostic helper. Next full lesson uses this profile mode and all 42 path units.

Standalone startup diagnostic (not a product release): build with
`DUOAERO_STANDALONE=1 python native-base/build.py`. The original DuoApp initializes
its local profile, configuration and full course repositories before returning
from onCreate; optional goals/social caches initialize on a worker. This uses the
same original real-cache path as the successful instrumentation setup, without
replacing the launcher or any screen. It still uses the isolated local test
identity and does not implement Google authentication or persistent progress.

`python native-base/test_standalone.py` clears only the diagnostic package's data,
starts its original LaunchActivity through adb and taps the original path node
and lesson button. It captures home/popup/question and crash/ANR evidence, without
instrumenting or injecting app state. The standalone matrix build is enabled
explicitly; other diagnostic variants retain their prior initialization. A local
build is not evidence that standalone initialization succeeds at runtime.

Cold-start finding: run 41266619470 initialized caches but showed Welcome. The
initializer now seeds only the native identity before DuoApp.onCreate, then seeds
course/configuration after original startup. The first-node instrumentation probe
now attempts all questions and Claim XP through original controls, rather than
asserting only that a first question appeared. This is not yet a passing result.

Session submission storage: the local original-session route now acknowledges a
known catalog lesson's PUT only after an AtomicFile write and read-back of the
native submission in the diagnostic account namespace. This preserves the actual
native result. It does not yet interpret course completion, update path responses,
restore a partially answered session, or provide Google account isolation; none
of those requirements is claimed by merely saving the request.

Run 41266796994's path probe visibly opens its first Aerospace question through
the original node and POST loader. The models process crashed in that path job;
new immediate model/crash logs retain its cause before subsequent app launches.

### Native path completion and rendering follow-up (2026-11-01)

Run 41267475095 decodes all 1,200 native question models. Its path probe opens
the first real node through the original session POST and grades all 19
questions CORRECT. After the final Continue the original loading dots remain;
Claim XP is absent. No PUT submission or saved completion is established.
The next probe observes original SessionEnd dependencies for this path session
and preserves bounded endpoint counts even on assertion failure.

Original JS grading occasionally returns null. The bridge now logs the original
swallowed exception and retries only explicitly marked pure choice functions
against the original SESSION JavaScript context, at most six times. A missing
result still fails normally; no answer, grade or readiness state is fabricated.
Native LaTeX figures now bind semantic labels to their actual MathFigureView
and mathCard parent. Both changes compile; their runtime acceptance is pending.

Cold-start evidence previously stopped at a transient null UiAutomator root
before the home timeout. The driver now preserves that observation and keeps
waiting within its deadline, including when the dump file does not exist.
Screenshot collection likewise retries null bitmap capture without treating it
as a pass. Lesson/formula probes now use native profile caches, the full course
and the local service together, matching standalone repository inputs.

Local checks: original 18,244 unchanged APK entries, 48 generated JS choice
grading cases and 18 symbolic Java grading cases pass. These are not evidence
of standalone usability, completion, persistence or production release readiness.
