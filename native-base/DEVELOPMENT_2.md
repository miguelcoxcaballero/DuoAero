# DuoAero 2.0 development

The published signed release remains 1.3.7. This branch is work in progress,
not a 2.0 release or evidence that the whole course works. The user requested a
finished 2.0 APK and explicitly authorized signing it with the permanent key
and publishing it to GitHub. The default policy remains development channel A;
no B publication was requested. Keep the canonical updater installer frozen.

## Progress and data compatibility

`session-history/1.3.7.json` was extracted from the signed public 1.3.7 APK
after checking its SHA-256 against the release. It preserves the exact question
IDs of all 79 sessions. Synthetic Android account tests should verify the
snapshot is loaded for older completion proofs. It does not prove real Google
login, Drive synchronization, or a populated user migration.

The first Atmosphere lesson teaches the isothermal pressure formula in words,
then in an equation, then as a symbolic block before the short numerical
question. The sample answer is 10 kPa. A reviewed hint is also attached to the
first step of the previously split pressure-ratio question. One radiation
question moves to the radiation/visibility node to keep the source lesson
within its existing size limit. Historical completion snapshots preserve old
lesson proofs, though actual migration must still be tested on Android.
Run 41371193797 reached the isothermal formula with LaTeX options visible,
then the driver failed because its adb instrumentation argument was not shell
quoted. The driver now quotes formula labels; this does not by itself prove
completion or rule out other problems. Android run 41372728007 subsequently
completed the first Atmosphere lesson, claimed XP, observed durable completion
and opened the next lesson before and after restart; earlier nodes were seeded.
This is synthetic local progress, not a Google or Drive roundtrip. A second
pressure-ratio question has also been divided into reviewed steps and graded
in a standalone Android diagnostic. Run 41373085468 also passed the complete
Atmosphere lesson after showing a formula hint: it verified the extra retry,
claimed XP, persisted completion and opened the next lesson after restart.
After that run, the pressure-ratio prerequisite was moved before the first
ratio calculation and another long ISA problem was split into two short
steps with formula hints. Local tests check their order and rounded results;
Android run 41377210380 graded the revised nine-exercise diagnostic. Five
further ratio problems are now split into two calculations; run 41381978642
graded all ten in Android and verified synthetic account migration. Its full
Atmosphere progression test also passed, with earlier nodes seeded.

Seven further pressure/density questions now teach density and dynamic
pressure with word slots and named-quantity equations before symbolic recall,
then split each calculation into two steps with reviewed hints. The displayed
rounded values and original answers are checked by `test_dynamic_steps.py`.
Run 41383369989 graded the 20-step sample on Android and passed synthetic
account checks. This sample does not establish full-course acceptance.

The separate `codex/lapse-study` branch stages four tropospheric lapse-rate
questions as single-operation temperature-decrease and subtraction steps,
preceded by named-quantity and symbol practice. It rebalances lessons and
tests the old completion snapshots. Run 41387274344 graded all 14 original
controls and passed synthetic accounts for an earlier version of the tiles;
more compact tiles and whole `Δh`/`ΔT` symbols are under Android retest and
are not yet integrated. None of this establishes the rest of the course.

The notation converter now recognizes balanced square roots, nested simple
fractions and several lift/drag subscripts without converting ordinary prose
or simple unit paths. A source-bank audit found 125 previously plain `sqrt`
occurrences converted; this is not a complete LaTeX audit. The `sqrt-mixed`
Android diagnostic must render and grade a representative original question
before device acceptance is claimed. The later denominator case such as
`1/sqrt(CLmax)` is covered by a host assertion, not yet Android UI evidence.
Reviewed aliases for approach speed, stall speed, minimum-drag speed and
maximum lift coefficient now render with subscripts, including an assignment
such as `Vapp=1.3Vs`. Local comparisons found 189 source stem/explanation
fields with changed notation; the corresponding Android diagnostic remains
pending and this does not establish a complete notation audit.

A four-slot named ideal-gas exercise is under test: pressure, density, gas
constant and temperature occupy their positions with the original equality
operator. The native per-slot controller is called with the real index. This
is experimental. Android diagnostic run 41370981586, commit df1af26, passed
13 actual exercises including four word slots and rapid touch at emulated S24
Ultra proportions, dark mode and 1.15 font scale. Its screenshot showed a
two-line product with no explicit multiplication signs; the next source
revision adds signs for clarity. Android run 41372273142 graded all 13
exercises and its screenshot showed the four tiles and both multiplication
signs on an S24-proportioned emulated screen with larger text. Drag/drop,
wrong-answer feedback and all supported font scales are still unverified. It
also covers reviewed hydraulic-power and wind/time equations; it does not
cover all formula families.
The gas sequence is now ordered as a word sentence, the full named-quantity
equation, the one-quantity symbolic equation and finally the symbolic blocks;
the revised order passed Android run 41380455084. The hydraulic sequence
passed four original controls in run 41381254897. The wind sequence passed
14 native touch-driven challenges in run 41380642719.

A front-facing Peanuts-style aviator launcher replaces the earlier generic dog.
Android run 41391211227 rendered the original launcher drawable without clipping
the face, ears or goggles. The host check also verifies a padded splash mask;
the actual splash on the user's S24 Ultra remains unverified.

The original welcome and share-card wordmark resource names now map to the
DuoAero wordmark instead of the generic mascot. Android run 41385372302
showed the correct wordmark in the actual welcome view; share cards and icon
display-name variants need separate UI verification.

The old path check counted source items but missed word and named-formula
expansion: nine lessons therefore exceeded 20 visible exercises. Four nodes
were rebalanced between their existing session IDs. Four more nodes are now
split into three lessons, keeping prior IDs and introducing four new IDs;
a fifth lesson was later added for the staged approach problem; all 84 lessons
have 10–20 visible exercises in host validation. For each new ID, path-only credit is derived only from an exact stored historical proof
that includes every question moved there. No synthetic completion, XP or gem
award is created. A replay or Drive import retains the historical proof when
it covers questions omitted from the new shorter source lesson. Local tests
verify mapping coverage in every published 1.3.x snapshot and the pure
projection boundaries. A submitted in-flight older lesson is now checked
against exact historical snapshots as well; current-version submissions use
a fast path without loading those snapshots. Android run 41380252027 passed
150 synthetic account checks, including replay, in-flight completion, import
and export. Run 41379312441 passed the original chest and first Atmosphere
path tests; run 41381978642 passed the further split's account, path and
question diagnostics. No real Google or Drive migration has been established.

Two static, transparent Snoopy illustrations target explicitly identified
reading and gem-holding resources. A diagnostic drew the reading resource IDs;
that is not evidence of the actual screen or of animation. The gem pose and the
original screens still need inspection. Many generic mascot scenes and the
articulation and smoothness of animations remain unfinished.

An experimental 16-frame transparent wave exists but the original
`duo_happy` ImageView currently uses a static fallback. The wave uses
drawn arm poses rather than translating one still image. This needs real
Android inflation, screen placement and smooth playback checks; a generated
sprite sheet alone is not an animation acceptance test.
Run 41372032864 failed to load the drawable because its intrinsic bounds or
atlas could not be read. The attribute IDs supplied to `obtainAttributes`
were unsorted; the follow-up orders height before width and reports failures
separately. Run 41374041351 then loaded the original drawable and confirmed
different frames. Inflating the complete fragment from an instrumentation
application context failed on an unrelated themed text widget; the revised
probe inflates the original image element in isolation and passed in run
41374984771. That run exposed visible pixels on the source atlas cell seams;
the source image was replaced and host assertions now check transparent seams.
The replacement atlas must be retested on Android. Neither the old test nor
the frame check proves the attached screen or smooth playback works.

An additional transparent 16-frame sad expression was initially bound to
the original `duo_sad` in-app resource, including the lesson quit sheet. Its
atlas seams and Java compilation pass locally. Android run 41376134295
successfully loaded both animations and observed distinct frames, but the
quit-screen driver returned straight to the path without seeing a dialog when
it tried to exit an untouched lesson. A revised test answers a question first.
Run 41377932982 revealed that opening the real quit sheet crashed: Android's
framework drawable inflater could not see the application class from the XML.
The original resource is now a safe static drawable and a hook installs the
sad animation after the original quit state binds its image. Android run
41382612045 opened the real sheet and returned to the lesson; the actual
recording showed 18 distinct frames when checked locally. The hosted video
check lacked ffmpeg; after pinning a decoder, run 41383606787 passed and found
22 distinct frames in its attached-screen recording. Other feedback remains
static and visual smoothness remains unverified.

The separate two-section diagnostic shows both section cards in the original
picker. Its first test tapped the second card only once, expanding it rather
than opening the inner row. Android run 41374119769 tapped the inner row and
actually showed the second section's diagnostic path; the test failed only
because it expected a topic title where the original header showed Midterm 2.
The follow-up on the separate research branch passed Android run 41375262771:
the second topic title appeared and its synthetic lesson opened. Run
41380416094 graded ten draft questions, saved their lesson and graded the
first question of the next topic after restarting. Run 41382266509 repeated
the route with a third draft topic present, and run 41383706755 graded its ten
draft questions. The combined branch passed synthetic accounts and the first
Atmosphere progression test in run 41384151374; its second-section test first
opened the welcome screen because the diagnostic bootstrap was not enabled.
After the setup correction, run 41385232869 graded the ten first-topic
questions, claimed XP, observed the next node and graded its first question
after restarting. The latest merged build is being checked separately. The research draft now
also includes twenty original conceptual questions on diverse aircraft and
rotorcraft, aligned with the course outline; these are not in the diagnostic
section or production. Run 41386234650 graded the first version of those
twenty on Android; the job failed at its final evidence-path check. Their
distractors were subsequently improved, and that revision needs a fresh UI
test. All fifty draft questions, the missing topics and
calculations, rewards, Drive and the complete second-midterm course still need
editorial review and Android acceptance.

Android run 41372273142 also graded the five-step isothermal pressure-ratio
diagnostic. Its screenshot shows the final ratio question and the hint button;
this is a sample, not complete lesson or course verification. A subsequent
full-lesson timing run was interrupted by an unrelated Pixel Launcher ANR
dialog in the emulator; the test now dismisses only that external dialog.

The original energy-rewards request returned repeated local 503 responses
during lesson completion. An experimental empty response uses the original
model's required `inLessonRewards` field for this unlimited-energy course;
gem chests use a separate store. Android decoded the response and a native
chest still awarded 25 gems, but the elapsed time remains too variable to
claim an improvement. Run 41382465891 tested a full-energy local response for
`energy-info`: the native model decoded, that endpoint stopped returning 503,
and an entire first Atmosphere lesson plus restart completed with the infinity
indicator visible throughout. Its 26.66 s emulator timing versus 28.84 s in a
different run is insufficient to establish a speedup. A completion recording
shows a visible wait on the emulator and the fallback Snoopy standing still on
the final screen; physical-device behaviour remains unverified.
Diagnostic run 41385394122 observed the original completion selector choosing
both `LOVEY_DOVEY_DUO` and `SWOON_DUO`. The latter previously had a generic
fallback. A distinct transparent swoon pose sequence is being tried on a
separate `codex/swoon-animation` branch, but its real-screen playback and
smoothness are not accepted.
Run 41384336207 tried schema-checked empty offline social responses and still
completed and reopened the lesson. Its 40.34 s measurement includes emulator
and screenshot overhead and does not show a speedup; this experiment has not
been enabled in the integrated production path.
An additional diagnostic skipped 111 original promotion-video prefetches. Its
first OCR process timed out. After the OCR retry fix, Android run 41390278261
completed the lesson, claimed XP and reopened the next lesson, but its 36.57 s
emulator observation does not establish a speedup over the prior 26.66 s run.
This network experiment remains separate and is not enabled in production.

The latest lapse-rate sequence is integrated in this development branch. Run
41388461549 graded all 14 staged controls with the original Android screen;
the four source answers also match the independent numerical checks. Its
screenshot still shows an operator stranded at the end of a wrapped line. An
experimental grouping change crashed a hydraulic formula screen in run
41389101897 and is not integrated; a correction is under test. Run 41388130102
also graded the revised 20 draft rotorcraft/diverse-aircraft questions, but
they remain research drafts and do not establish a complete second partial.

The first Atmosphere lesson now includes the ISA-offset formula as a word
gap, three named positions, then a symbol before its calculation. Android run
41389283322 used the hint on that calculation, verified its end-of-lesson
retry, claimed XP and reopened the next lesson before and after restart. Its
screenshot still shows a plus sign stranded before a line break. This is an
emulated S24-proportioned screen with earlier nodes seeded, not a real-device
or Google/Drive test.

A clipped warm-day approach-speed source is now staged as 18 controls,
with named and symbolic formula prerequisites. Android run 41390434067 graded
all 18 original controls at S24 proportions, dark mode and 1.15 font scale;
run 41390029749 also passed the historical migration with synthetic accounts.
Its operator still wraps at the end of a line; a separate fix is under test.
The integrated bank has 84 lessons and five evidence-based path migrations.
Other long problems and actual-device tests remain open.

A distinct Swoon pose appeared on a completion screen in run 41387776940,
but the recording showed it practically motionless. A revised state-machine
entry starts the sprite loop in a browser preview; Android playback and smoothness
are being checked separately and the animation is not integrated.

## Acceptance still required

* Review all calculation families, simplify long questions, author correct
  prerequisite formulas and word/symbol block exercises, and verify ordering.
* Complete the course/partial coverage from available source material without
  publishing private Drive files or non-authorized metadata.
* Replace original character poses and animations with matching Peanuts cast,
  expressive states and genuinely smooth transparent animation; test scenes.
* Verify progress migration, rewards, streaks, mistake review, sections,
  settings and the updater installation flow with actual UI interactions.
* Verify real OAuth and Drive roundtrip and S24 Ultra layout, audio and haptics.
  An emulator or a synthetic account cannot establish these real-device facts.
* Only after acceptance, build 2.0.0 with a globally newer versionCode, bind
  the exact source and APK digest, sign using the authorized permanent signer,
  test the signed APK, publish immutable bytes and then update channel A.
