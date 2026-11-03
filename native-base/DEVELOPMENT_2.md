# DuoAero 2.0 development

The published signed release remains 1.3.7. This branch is work in progress,
not a 2.0 release or evidence that the whole course works. The user requested a
finished 2.0 APK and explicitly authorized signing it with the permanent key
and publishing it to GitHub. The planned publication channel is A; installed
apps default to B, and no B publication was requested. Keep the canonical
updater installer frozen.

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

Four tropospheric lapse-rate questions are integrated as single-operation
temperature-decrease and subtraction steps, preceded by named quantities and
symbols. Run 41391260503 graded all 14 controls with compact tiles and grouped
operators, and tested the Atmosphere lesson with a hint. Historical completion
snapshots are checked synthetically; the rest of the course remains incomplete.

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

A four-slot named ideal-gas exercise is integrated: pressure, density, gas
constant and temperature occupy their positions with the original equality
operator. The native per-slot controller is called with the real index. This
was tested experimentally. Android diagnostic run 41370981586, commit df1af26, passed
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
Android run 41391211227 rendered the launcher drawable without clipping. A
later S24-proportioned startup recording in run 41393049952 showed that the
splash screen clipped the goggles despite the host mask check. A smaller
splash-specific foreground kept the full face, goggles and ears visible in
Android run 41394279283 and is integrated. The physical S24 Ultra remains
unverified.

The original welcome and share-card wordmark resource names now map to the
DuoAero wordmark instead of the generic mascot. Android run 41385372302
showed the correct wordmark in the actual welcome view; share cards and icon
display-name variants need separate UI verification.
Two additional original code literals are now changed in their specific UI
methods: a visible Compose label and the fallback shortcut title. Run
41451903286 built the altered runtime, opened the welcome screen and passed
synthetic accounts. It did not open those two specific screens; other original
visible text and the original provider's legal attribution still need review.

Two original static poses now have distinct transparent Snoopy artwork:
`duo_wave` waves, while `duo_welcome` holds up a phone, matching the original
vector poses. Android run 41396166179 inflated and drew both original resource
IDs; the extracted images were inspected. This checks resource resolution,
not their placement on every original screen or animation coverage.
The original `duo_chest` vector shows the character holding a chest; its new
transparent Snoopy equivalent resolved and drew in Android run 41427170617.
It is a static resource check, not proof of the chest-opening animation.
The original `duo_holding_flame` static vector also has a distinct transparent
Snoopy pose; Android run 41451292908 resolved and drew that resource. The
actual streak screen placement and animated scenes still need examination.
After the chest, payload and catalog changes were combined, Android run
41431692180 passed account checks, the Atmosphere lesson with a hint, wing
geometry controls and static-resource diagnostics. It used synthetic accounts.

The old path check counted source items but missed word and named-formula
expansion: nine lessons therefore exceeded 20 visible exercises. Four nodes
were rebalanced between their existing session IDs. Four more nodes are now
split into three lessons, keeping prior IDs and introducing four new IDs;
four further lessons were added for the staged approach, temperature/lift,
wing-geometry and spar problems; all 88 lessons have 10–20 visible exercises in host validation. For each new ID, path-only credit is derived only from an exact stored historical proof
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
after restarting. The research draft now also includes twenty original
conceptual questions on diverse aircraft and rotorcraft, aligned with the
course outline. All six topics are present only in the diagnostic section,
not the production course. Run 41386234650 graded the first version of those
twenty on Android; the job failed at its final evidence-path check. Their
distractors were subsequently improved, and run 41388130102 graded the revised
twenty. Ten introductory topic-4 questions were added as a research draft and
graded in run 41393093143. All sixty questions remain draft content; coverage
of the syllabus, calculations, rewards, Drive and the complete second-midterm
course still need editorial review and Android acceptance.

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
fallback. A distinct transparent swoon pose sequence was integrated after
forced Android run 41393926752 showed movement without the earlier overlap.
Unforced selection and smoothness on a physical phone remain unverified.
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
screenshot showed an operator stranded at the end of a wrapped line. An initial
grouping change crashed in run 41389101897. After fixing composition flags,
run 41390137453 graded the hydraulic exercise and run 41391260503 graded all
14 lapse controls and completed the offset-hint lesson; the inspected screenshot
keeps the operator with its operand. An initial fast-touch retry timed out
during emulator installation; run 41392738917 subsequently passed the integrated
fast-touch, word-gap, original formula and approach scenarios. Run 41388130102
also graded the revised 20 draft rotorcraft/diverse-aircraft questions, but
they remain research drafts and do not establish a complete second partial.

The first Atmosphere lesson now includes the ISA-offset formula as a word
gap, three named positions, then a symbol before its calculation. Android run
41389283322 used the hint on that calculation, verified its end-of-lesson
retry, claimed XP and reopened the next lesson before and after restart. A
later version with the operator grouping also passed in run 41391260503. This is an
emulated S24-proportioned screen with earlier nodes seeded, not a real-device
or Google/Drive test.

A clipped warm-day approach-speed source is now staged as 18 controls,
with named and symbolic formula prerequisites. Android run 41390434067 graded
all 18 original controls at S24 proportions, dark mode and 1.15 font scale;
run 41390029749 also passed the historical migration with synthetic accounts.
The combined lapse, offset and approach course repeated both checks successfully
in Android run 41391868945, before the later icon and operator patches.
A subsequent Android run 41392188207 graded all 19 exercises after adding an
original matching screen for the four stall-speed quantities; its screenshot
showed all four pairs on the emulated tall display. Run 41393579098 also
passed the combined matching, operator-grouping and account-migration checks. At that point the bank had 85 lessons and six evidence-based path migrations.
Other long problems and actual-device tests remain open.

The drag-polar parser now formats the complete reviewed equations and standalone
lift/drag coefficients, including their powers. Run 41393483218 graded a native
choice and its screenshot showed both squared terms and coefficient subscripts.
This is a targeted improvement, not an audit of every question.

Eight fixed-pressure temperature/lift-coefficient problems now use two short
calculations after named and symbolic formula exercises. Run 41393361188
graded all 22 staged controls and passed account migration on the emulator.
The division sign was left at a line end in an earlier screenshot; run
41394563874 graded all 22 controls with the sign grouped beside its operand.
Android run 41394920139 also passed the combined 85-lesson account,
temperature/lift and 19-step approach diagnostics before the later splash and
character changes. These checks do not cover every numerical problem.

Eight trapezoidal-wing root-chord problems now teach their symbols and formulas
before three short calculations each. Android run 41396895700 graded the 22
introductory and 12 remaining controls, and passed synthetic account checks.
That path had 86 lessons and seven evidence-based migrations; the checked
historical snapshots grant only path credit and do not create rewards. This
does not cover all remaining wing calculations or a real-account migration.

Ten spar strength/deflection problems now teach named quantities and three
formulas before four short calculations. Android run 41452609503 graded all
53 introductory and follow-up controls and passed synthetic account checks.
Dark, larger-text screenshots showed the compact quantity cards fully visible
after a previous layout clipped them. With earlier progress seeded, Android
run 41455195283 completed the fourth session through the original path,
restarted and opened the next node. Nine historical path-credit migrations
are covered by local tests; real Google/Drive migration remains unverified.

One column-capacity example now teaches yield load and capacity factor with
word, named-quantity and symbolic exercises before three short calculations.
Android run 41464615993 graded its 11 controls using the original controller;
its inspected screenshots show the named tiles in the numerator and denominator
of the native fraction. Android run 41467380208 intentionally submitted an
incorrect fraction, observed incorrect feedback only after Check, retried it
at lesson end, corrected it and reached Claim XP. Run 41471235112 also captured
the incorrect feedback; the reviewed screenshot shows the solution as a proper
LaTeX fraction. Other
fraction layouts still need device tests. Android run 41467201483 passed
the fraction, static Linus path and synthetic account scenarios together in
one source snapshot. To honor the source-publication restriction,
the public question bank now retains source category, title and cited pages,
omitting source URLs, file identifiers and other source metadata.

Local browser previews loaded all ten replacement in-lesson Rive rigs and
triggered their original correct and incorrect inputs: each preview visibly
switched between its idle, happy and sad Peanuts poses. This is a preview of
the source rigs, not evidence that every scene, transition or animation is
smooth and reachable in the Android app.

A distinct Swoon pose first appeared motionless in run 41387776940; forcing
its original state machine to start the loop initially exposed overlapping
poses. Android run 41393926752 forced this character for diagnostics and
recorded moving transparent frames without the observed overlap. Only the
artwork and state-machine change are integrated, not the diagnostic selector.
Its appearance on a physical phone, other selectors and all remaining scenes
still need review; this one animation does not establish a complete cast.
The path screenshot from diagnostic run 41452609503 still shows the original
Junior-and-frog illustration. The original Rive file is
`res/raw/math_junior_grid.riv`, but Android run 41458302460 showed that this
path instance actually used `math_junior_grid_static`; replacing the Rive file
alone therefore did not change the visible character. A transparent static
Linus scene is now mapped to that fallback. In Android run 41461040425 the
original seeded Structures path displayed the replacement without clipping.
The separate animated Rive prototype is not integrated or accepted yet.
Five more transparent static replacements target the original math-path
drawable IDs for Zari's toy-horse and protractor scenes, Junior's calculator, and Duo's
ruler and clock. Android run 41468281983 resolved and drew all five distinct
IDs; their actual path placement and corresponding animated scenes have not
yet been verified.

Android run 41395067195 passed the tall-window check on an emulated display
with S24 Ultra proportions, using the course before the later splash and
character additions. It is not a physical-device check.
Run 41395923743 subsequently passed the first Atmosphere lesson with a formula
hint, retry and saved progress, plus the synthetic account checks, after the
splash and Swoon changes. Earlier path nodes were seeded for this diagnostic.
Its question-16 screenshot shows the reported ideal-gas density expression
as the fraction p/(RT); the correct choice is density. This is one rendering
check, not a complete LaTeX audit.
Android run 41454854104 also rendered and graded the reported geometric-altitude
gravity question: all four options showed fractions and exponents, and the
correct inverse-square expression was accepted.
In run 41396302024 the original home displayed a one-day streak both after
completion and after restart. That seeded emulator scenario does not establish
multi-day streak behavior or synchronization with a real account.

The same emulator run measured 2.139 s loading and parsing the current
session catalog inside the durable-completion path, and 2.323 s through its
local refresh. Its 43.78 s final-Continue-to-Claim measurement included adb,
screenshots and OCR overhead. A shared immutable-catalog cache is under test;
neither that diagnostic nor an earlier network-suppression experiment has
established an end-to-end speedup yet.

The shared session catalog is now cached for the installed app process and
treated as read-only. Android run 41398314531 passed a full Atmosphere lesson,
restart, review and 173 synthetic account checks, including an unchanged
catalog after account operations. In that separate emulator run the catalog
lookup in the completion path took less than one millisecond, with 0.749 s
through local refresh; the automated final-Continue-to-Claim observation was
39.84 s including adb/OCR overhead. Differences between emulator runs do not
establish the actual improvement on a phone or account for the full delay.

The first payload-mass calculation teaches named and symbolic quantities
before two subtractions, with a reviewed formula hint. Android run
41397802231 graded all six controls; the resulting lesson remains within the
existing 20-exercise limit. Other mass and range problems still need review.

The isolated second-partial preview now links six draft topics. In Android run
41396433753 the section picker opened, all ten questions of the first topic
were graded, and the second topic opened after completion and restart. A
separate scenario seeded the first five topics, opened the final rotorcraft
topic and graded its first question. These are diagnostic drafts, not the
completed production course or a real-account/Drive progression test.

Android run 41392335036 repeated three integrated scenarios before the later
icon and formula patches: a seeded original chest showed +25 gems and retained
the balance after restart; a wrong answer was reviewed and its correction
persisted after restart; the original settings opened the updater settings and
its provider read test bytes. The latter did not install an update. Android run
41392120069 graded the night/large-font sample and observed 21 SoundPool starts
and 20 haptic completions in emulator services. These observations do not prove
audibility, physical vibration, real Drive sync or an installed update.

Separately, Android run 41464902704 installed the published signed 1.3.0 APK,
opened its updater activity directly on a rooted emulator, accepted the A
warning and slide, and displayed the actual 1.3.7 update offer. This checks
the released 1.3.0 catalog flow, not entry through the signed-in settings.
Run 41465735190 then downloaded 1.3.7 and displayed Android's update
confirmation; its detector missed that window, so the update was not accepted
or installed. With the detector corrected, run 41468559822 accepted Android's
installer, observed package versionCode 10307 and verified a synthetic private
file survived. This is an emulator upgrade to the published 1.3.7, not a test
of a 2.0 APK or real-account data. B remains empty and is the app default.
The manually dispatched `released-updater-e2e.yml` diagnostic can repeat this
check for an expected channel-A version and code; it uses a rooted emulator,
automates the A warning and Android confirmation, and checks only a synthetic
private-file marker, not a real profile or a physical device.
Run 41469978603 reported a post-update launch as successful, but its capture
still shows Android's installer success dialog: a successful intent and process
ID were insufficient evidence. The diagnostic now closes the installer, starts
a fresh app process and requires a resumed DuoAero foreground activity; that
stricter check must pass before claiming the updated app actually opens.
Run 41512696327 ran the strict script: after the installation it cold-started
the updated app and its inspected screenshot shows the Google welcome screen.
This remains an emulator test with a synthetic file, not a real Google account
or an update to the unfinished 2.0.

The taper and fuel-fraction equations now also use two native word slots in a
fraction, with a preceding verbal introduction. Android run 41469220414 graded
both exercises and its screenshots show the fraction bars. The later clearer
``fraction left`` label was also inspected in Android run 41472025112. The lesson
size and path migration checks pass locally; they do not establish full course
acceptance.

In a separate Rive prototype, run 41470392850 showed Linus blinking and the
original frog moving without the earlier double-eye artifact in the sampled
frames. Its recording captured only 22 frames in 8.5 seconds on the emulator,
so smoothness cannot be established. This prototype is not integrated.

## Acceptance still required

The current authored bank has 44 symbolic formula exercises with a word-first
introduction; 10 still lack the separate exercise with all named quantities
in the equation. This count covers authored formula blocks only, not every
formula that may be needed by the rest of the course. Some existing named
equations express a fraction with division symbols or put an exponent into a
word tile; they still require layout work to preserve the original operators
and exponents in place as requested.

Flight time, Mach number and static temperature now have full named-quantity
equations in addition to their verbal and symbolic exercises. Three conceptual
questions were moved to the next existing lesson in their same topics to keep
all lessons within 10–20 exercises; lesson IDs and the migration rules remain
unchanged. Historical snapshots confirm those questions were present in the
earlier lesson in each reviewed release. Android run 41520306939 graded all
12 controls with short taps; inspected screenshots show the compact temperature
labels and the flight-time and Mach fractions. Run 41518676490 graded the two
thrust formulas and their inspected screenshots show the operators and tiles.
A third thrust lesson holds ten
questions formerly in the second, with path credit limited to exact historical
coverage and no new completion rewards; Android migration remains unverified.
The speed-of-sound equation additionally has an experimental named base with
a fixed squared exponent, using the original exponentiation figure. Adapter
and ordering checks pass, and the modified Java helpers compile against the
Android SDK with a stub course bridge. The diagnostic APK also compiles;
acceptable Android rendering remains required. Android run
41519217015 graded the four controls but its screenshot showed an oversized
exponent and a single-column word bank cutting off options. The exponent and
labels were subsequently compacted. Run 41526660877 graded the revised power
and aspect-ratio exercises with short taps; inspected screenshots show a
readable fixed superscript and all options fitting on the S24-proportioned
emulator. This does not establish physical Samsung behavior or every font size.
The aspect-ratio equation now has an experimental squared numerator in the
original fraction figure. Its inspected screenshot and short-tap grading pass
in that same diagnostic run.
The two axial-extension formulas and axial stiffness now use named factors
inside an experimental original fraction figure; the spar stress equation
uses the same fraction rather than a division glyph. A new structural lesson
has exact historical path-only credit. All 93 lessons pass the local size and
migration checks, but the new fraction layout and Android migration still need
device diagnostics.
Run 41523145284 crashed when opening the first product fraction because the
original Sequence expects SequenceTokenUiState entries, not raw figures. The
prototype now wraps each factor as a native sequence token and compiles with
the Android SDK stub; another Android run is required to establish that the
crash is fixed and the fraction and touches fit.
The pressure ratio and three dynamic-pressure formulas now also have named
equations. Run 41520281226 graded the pressure ratio and one dynamic-pressure
sequence; the inspected ratio fits, but its dynamic-pressure screenshot showed
an oversized exponent and a multiplication sign stranded at a line end. A
subsequent fix requires Android review. The atmosphere lesson split retains
exact historical source proof; Android migration remains unverified.

Run 41517680035 graded all ten unsplit cabin-pressure problems and rendered
the exponential as a power and fraction. Inspected screenshots show long
stems clipped, and a separate p11 was not subscripted. These exercises still
needed to be broken into short, taught calculation steps. They now have three
prior formulas and three or four short questions each, with original answers
independently recalculated. Their split uses exact historical path-only
migration and passes local validation. The new questions, p11 token fix,
and the migrated path still need Android UI and persistence validation.
Run 41522448593 graded the 19 controls of the first two staged problems and
passed synthetic account projection. The inspected short question screens
fit, but the gamma symbol was missing from one prompt. A subsequent authored
text fix was visually checked in run 41524834250, which graded the same 19
controls and showed gamma correctly. Its exponent was too small; run
41526660877 subsequently verified the revised size on the separate power and
aspect questions. No real account or path
migration was exercised in these diagnostic sessions.

Run 41527035707 exercised the direct axial-extension hint with the original
controller. Its inspected captures show ΔL and the hint as mathematical text,
then the question as a previous mistake at the end; the correct retry reached
Claim XP. This used a diagnostic session and does not establish real-account
persistence. The first attempt 41525477334 clicked before the feedback panel
closed; the driver was changed to wait for actual answer controls.

The original APK contains 67 Rive resources named after the ten mapped
supporting characters, including the ten in-lesson rigs. The other 57 names
are a review inventory: a resource name alone does not establish that its
scene is reachable in the Aerospace path or that it still needs replacement.

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

Seven kinetic-heating source questions now have four shorter calculation steps each, with previously taught formulas and independently checked original answers. Two new lesson IDs use exact historical source-question proofs; local checks cover 95 lessons and sixteen path-only migrations. Android rendering, touch and real-account migration remain to be verified. Run 41526287112 graded the lift sequence and 41527904567 the mean-chord sequence; the latter shows a proper interactive fraction in inspected screenshots. Run 41527421053 graded total thrust but its bank was clipped at the right edge, so shorter quantity tiles require a new Android review.

The kinetic-temperature formula now has all three named quantities, a fixed squared numerator and fixed factor two in its denominator. Its new native composition and one-tap operation need Android visual and interaction tests; the historical first lesson question moved to its existing next lesson with snapshot checks.

Run 41528348194 uncovered a second product-fraction crash: a Compose intrinsic measurement of a SubcomposeLayout inside the original sequence. To avoid exposing that crash, named product equations now use explicit parentheses and division while keeping their operations fixed; kinetic temperature likewise uses a parenthesized denominator. The equivalent layout and one-tap interaction need fresh Android validation. The experimental vertical product-fraction code remains unreachable by these course exercises pending a proper fix.

The Breguet exponent has a named-quantity exercise preserving multiplication and denominator grouping, placed after its word introduction and before its symbolic expression. Local sequencing and lesson-size checks pass; Android layout and one-tap grading are pending.

Both induced-drag exercises now teach the named quantities with fixed square, pi and denominator grouping before the existing symbolic exercise. Local order and size checks pass; Android rendering and touch remain to be checked.

Run 41529226548 graded the four additional wind steps, with short prompts and hint controls inspected. Cantilever stiffness, two buckling and two Breguet range exercises now include named quantities and fixed operations before symbols; all five need Android layout and one-tap review. The first cantilever lesson moves one historical source question to its existing next lesson, verified against all four saved versions.

The last inventoried formula, isothermal pressure, now has a candidate native exponent with fixed e and minus and a named exponent slot. All 44 authored formula exercises thus have full named candidates, but the negative-exponent composition is experimental and must pass Android without crashes, with usable touch and inspected placement before acceptance. Its lesson rebalancing is checked against all four historical snapshots; real-account migration remains unverified.

Run 41530291309 graded eight short kinetic-heating steps and passed synthetic accounts; inspected prompts, choices and hint buttons fit on the S24-proportioned emulator. Run 41529919628 graded the compact total-thrust sequence; its inspected quantity bank no longer clips. These runs do not establish physical-device or real-account behavior.

A full-bank prerequisite audit caught ISA-PRESSURE-RATIO moving after two questions during the latest lesson rebalance. The introducing source has been moved before both within the new lesson, and its exact historical migration proof updated; full-bank, sequencing and lesson-size validation now pass. The thrust labels now say momentum part and pressure part to distinguish thrust contributions from momentum and static pressure; that wording needs a new Android layout check.

Run 41530759898 graded the three parenthesized product equations and the kinetic-temperature sequence. Inspected captures show all quantity slots, exponent and Check in the S24-proportioned emulator. This verifies the inline-division fallback, not a vertical product fraction: the original nested vertical layout still needs a crash-free solution.

A separate second-midterm ideal-rocket draft now contains ten native-model exercises: word and named-quantity introductions, symbolic equations, then two independently checked calculations with earlier formula hints. It is not in the production path and still requires Android, editorial, full-curriculum and progression acceptance. Runs 41530945821, 41531120853 and 41531467765 graded the Breguet exponent, induced-drag and range word/named/symbol sequences; inspected S24-proportioned screenshots fit, with inline division for product fractions.

The structural job of run 41531467765 additionally graded cantilever and both buckling named sequences. Inspected captures show the cubed length, squared effective length and pi squared, with choices and Check visible in the S24-proportioned emulator.

An additional isolated ten-exercise circular-orbit draft introduces circumference and period in words, named quantities and symbols before checked calculations with hints. It remains outside the production path pending syllabus review, Android and progression tests.

Run 41532833785 graded the experimental negative-exponent sequence, but its inspected screen shows the exponent slot too low and the preceding multiplication stranded at a line break. A taller invisible base metric and operator grouping are now implemented; they require a new Android rendering and touch test. The earlier run is not visual acceptance.

Inverse powers such as 1/L² and Pcr/Pcr_new/Pcr_old now render as fractions and critical-load subscripts, while ordinary units remain prose in local tests. The halved-column calculation is now placed after its Euler formula and offers that formula as a hint; its answer 4 is independently checked. Android rendering and hint behavior for this specific exercise require review.

Simple logarithms of symbolic ratios such as ln(Wi/Wf) are now converted as a single mathematical logarithm with subscripted numerator and denominator; unmarked ordinary words remain text. Local notation and bank checks pass; Android display remains to be verified.

Synthetic emulator logs showed repeated 503 retries to the original zombie site-availability endpoint during lessons. The original converter defines a single boolean field enforce_offline; the local bridge now answers only that exact host, GET and numeric android.json route with false, scoped to the local course. Android must still verify real converter parsing, narrow routing, successful lesson progression, absence of repeated requests and timing before any performance claim. Other batch requests remain unchanged because they may carry stateful actions.

Run 41534612371 graded the grouped negative exponent, but its screenshot shows the original math renderer rejects vphantom and clips the resulting text. That command was removed. A larger plain e base is under test; the exponent layout is still not accepted.

Runs 41533886456 and 41534411607 graded all ten rocket and ten orbit draft controls, respectively; inspected screenshots show fixed operations, subscripts and native fraction slots. Run 41534135505 showed the rocket formula hint, waited for Check, retried the question at lesson end and reached Claim XP. These sessions were isolated diagnostics, not an integrated or reviewed second-midterm course. Run 41532498346 passed synthetic accounts and the clarified total-thrust labels; its inspected screenshot fits.

An extended second-section diagnostic now places the rocket and orbit drafts after the existing launch-vehicle concepts within the original path level. Its isolated progression test must still verify the saved first session, restart and opening of the next session; the feature is disabled in production builds.

Reviewed numeric assignments for OEM, MTOM, TAS, specific impulse and cruise speed now render as math with appropriate subscripts or upright acronyms. Local tests cover them without changing ordinary units; Android screenshots are still required.

Eight payload-limit source problems now have six short calculations each, two preceding word/named/symbol formula sequences, and independently checked takeoff, landing and structural limits. Three additional lesson IDs use exact historical source coverage; 98 lessons and nineteen path-only migrations pass local validation. Android display, touch, hint behavior and migration are pending. The prior 44-formula inventory is now 46 and all have named candidates; the negative exponent still needs visual acceptance.

Run 41536150799 passed synthetic accounts and the real original availability converter read both true and false values. Its timing job never reached the path because the new diagnostic scenario omitted standalone bootstrap; that scenario has been corrected and must be rerun. No timing conclusion is established.

Run 41536425579 removed the renderer error but its inspected exponent box was still at baseline, with an oversized e. The adapter had dropped the original exponent modifier. It now preserves that modifier and applies a scoped upward offset with normal-sized e; this requires Android validation and must not be considered accepted from compilation. Payload questions now also introduce the minimum-of-limits formula before the final comparison, which has its own hint; all 47 authored formulas have named candidates.

Run 41536798351 completed the first extended second-section diagnostic lesson and returned to a blue, partially completed 3.1 node. Its test timed out because it required a green node; the color predicate now recognizes the observed active blue and must be rerun through restart and the rocket session.

Seven Reynolds-similarity source questions now each use three short calculations with taught Reynolds, scale and model-chord formulas; checked source answers remain unchanged. Two new lesson IDs require exact historical coverage of the original source lesson; all 100 lessons and twenty-one path-only migrations pass local checks. Android rendering, taps, hints and migration are pending.

Run 41538999647 graded the isothermal negative-exponent sequence. The original exponent modifier is now retained and a scoped offset and row spacing keep the exponent slot above the baseline without overlapping the preceding line in the inspected S24-proportioned screenshot. This is an emulator result for that formula, not acceptance of every equation or a physical Samsung test.

Nine previously long Breguet range-ratio questions have an isolated arithmetic draft with four short steps. The underlying relation assumes the stated equal pressure, Mach, weight, wing area, drag polar and mass ratio; the original answer is retained as the closest option, with the calculated value explicitly distinguished from the rounded option. The standalone arithmetic checks pass, but the draft is not integrated: its prerequisite word/named/symbol exercises, path sizing and exact migration, Android interaction and editorial review remain necessary.

Run 41538615954 graded all 18 native payload controls. An inspected screenshot of the minimum-of-limits equation shows all four selected quantities and the fixed min/commas without clipping; the single explanatory exercise and user-facing hint behavior are covered by separate ongoing diagnostics. The labels for structural limit, Reynolds number and viscosity ratio have subsequently been spelled out in source; their longer Android rendering is not yet verified.
Run 41539328726 also opened the minimum-of-limits formula hint on the original controller, allowed the question to be answered, and returned it as a previous mistake at the end; inspected screenshots show both the rendered formula and the retry. This is one synthetic diagnostic lesson, not all calculation families.
Run 41539188236 completed the first isolated second-midterm concept lesson, claimed XP, restarted, observed the partially completed original 3.1 node and opened and graded the first rocket question. Inspected captures show the saved one-of-three path ring and word question. This is a synthetic diagnostic configuration, not production second-midterm coverage or a real Drive migration.
Run 41540085306 graded 18 Reynolds controls, including the three word/named/symbol sequences and short calculations. Inspected screenshots show the selected blocks and explicit multiplication and division; this run predates the expanded labels and uses inline division rather than a vertical fraction. Separate diagnostics for the longer labels and synthetic accounts remain in progress.
Run 41538070307 passed the complete synthetic Atmosphere path and restart after the scoped availability response; the original converter received local `enforce_offline=false` and the next lesson opened. The diagnostic measured 35.24 seconds from initiating final Continue to detecting Claim XP, but that includes adb, UI dumps and OCR; the measurement does not establish the actual visible loading duration or a speed improvement. Other original requests, including batch and messaging, still returned 503 and must not be suppressed without understanding their state effects.
Compound coefficient aliases Cm_ac/cm_ac, ce_md, CLmax_clean and CLmax_deployed now use properly grouped subscripts in local notation tests. A diagnostic using shortened prompts derived from source questions is running; host string assertions alone do not establish Android visual rendering or full question readability. Run 41539872706 passed synthetic account checks after the Reynolds migration changes; actual Google/Drive remains unverified.
Seven coupled stall/Mach/pressure-limit questions also have an isolated eight-step arithmetic draft. The maximum mass from the limiting dynamic pressure matches the original answer in each case, with rounding and closest options checked. This draft is not in the production course: its word/named/symbol formula prerequisites, review, historical migration, lesson sizes and Android interactions remain to be completed.
The isolated speed-limits draft now also has five word, all-named, single-named and symbolic prerequisite sequences, and every staged calculation links to an earlier formula. Native models and arithmetic tests pass, including grouped symbolic subscripts; it is a 28-exercise combined diagnostic draft and cannot enter the path until safely split, migrated and checked visually and interactively on Android.
Run 41540759489 graded the payload and Reynolds controls with expanded labels; inspected captures show structural limit, Reynolds number and viscosity ratio fully visible. The captured Reynolds equations left an opening parenthesis at a line end; the wrapping adapter now groups an opening parenthesis, and division followed by an opening parenthesis, with the next slot. The adapter compiles locally; the revised wrapping needs Android interaction and screenshot review.
An isolated vertical product-fraction prototype now composes its two-factor numerator/denominator with a native row instead of the original nested Sequence that triggered an unsupported intrinsic measurement. The implementation compiles against the Android SDK but remains unused by production formulas until a separate Android diagnostic verifies crash-free layout, all factor taps, grading and complete labels. The inline-division fallback remains in the path and is not considered vertical-fraction acceptance.
Ten approach-speed source questions have an isolated nine-step arithmetic draft. For the requested true speed the measured pressure and temperature directly determine density; the original ISA inversion is unnecessary for that particular result. The draft checks the original closest answer using both displayed rounded intermediates and an independent unrounded calculation. Formula prerequisites, lesson distribution, historical migration and Android validation are still outstanding; the draft is not in production.
The spar-deflection named equation now uses a length slot with a fixed cubic exponent rather than treating “length cubed” as one quantity. The ordering and model checks pass; its wrapped layout and touch behavior require Android review before visual acceptance.
Run 41542553006 graded the eight isolated speed-limit calculations from the first source case in the original controller; an inspected prompt fits with its formula-hint control. That run exposed redundant trailing zeros, now removed in the draft with host checks. The prerequisite-formula diagnostic and a new visual check of the shortened numbers are still pending, and no course integration is claimed.
Run 41541980211 rendered and graded two shortened diagnostic prompts with the new aerodynamic coefficient aliases. Inspected screenshots show grouped subscripts; this does not establish that the original long questions fit without being split.
The long-name probe 41542208390 graded the induced-drag controls but its inspected screenshot showed part of the choice bank cut off; the range control could not finish because the long formula overlapped the bank. These are layout failures despite some positive grading. A diagnostic of compact original token widths and intrinsic sizing is running; no abbreviated labels will be restored as a workaround.
A recording from 41541748128 shows a prolonged blank/loading transition before the original lesson-completion summary in the emulator. The recording begins around the final interaction, so it does not provide a precise button-to-summary timing; it does show the latency remains a real issue to investigate. A strictly opt-in synthetic diagnostic now counts only broad batch route categories, without logging bodies, URLs, queries or identifiers, and does not change any batched response. Its Android verification is pending.
Run 41542751352 graded the grouped-parenthesis Reynolds, payload and negative-exponent controls. An inspected Reynolds capture keeps the division and opening parenthesis with the denominator slot and fits the short labels; this does not resolve overflow with the longer multi-factor formulas.
The speed-limits formula probe 41542553006 graded 20 controls, but its inspected maximum-weight equation cuts off the bank at large text. The draft remains isolated, and its “maximum lift coefficient” label has been expanded; the same compact-layout work is required before integration.
The approach draft has three isolated word/named/symbol prerequisite sequences for density, the approach factor and unit conversion. The stall formula and its fully named interactive radical are not yet authored, so the draft cannot be placed before its calculations or treated as a finished lesson. Host model checks cover these three only; no Android acceptance is claimed.
Run 41543348905 graded twelve original controls using the native-row product-fraction prototype. Inspected captures show two interactive factors above a fraction bar, both two-factor and single-factor denominators, fixed multiplication signs, visible options and Check at emulated S24 proportions with enlarged text. The axial-stiffness, axial-extension and spar-stress named equations now use that tested vertical composition. Other product-fraction patterns, longer labels, wrong feedback and physical-device behavior remain to be verified separately.
The experimental squared-numerator fraction with fixed factor two in the denominator also now uses a native row instead of a nested Sequence. It compiles but is not yet connected to production exercises; its superscript, fraction placement, factor-two position and touch grading require Android validation.
Run 41543708609 graded the four spar-deflection word/named/symbol controls with the fixed cubic exponent. The inspected S24-proportioned capture shows the length tile, its superscript and all remaining options; that equation still uses the inline-division fallback and needs a true vertical multi-factor fraction.
A 140 dp uniform-width probe (41544213811) kept the induced-drag bank reachable but clipped the full quantity labels, so it is rejected despite passing grading. A separate probe using the original intrinsic-width branch is running; it has not been merged. Exact full-name cabin captures also show choice-bank overflow at the enlarged font, so positive grading alone is not acceptance.
Three partial Breguet prerequisite sequences now cover temperature, consumption and range ratios in words, named quantities and symbols. The speed-ratio square-root formula remains missing, as do curriculum ordering, layout acceptance and migration; this draft is not integrated into the production path.
The intrinsic-width probe (41544252012) is also rejected: although the original controller graded the range exercise, inspected screenshots showed the answer tiles disappearing. No sizing probe is accepted solely from grading; a separate multiline-label experiment is now running.
An additional isolated ten-question space-environment draft covers orbital gravity, thermal control, pressure, power, propellant and crew life support. It contains no private document links or identifiers. Model checks pass, but it has not been editorially accepted, integrated into the second-midterm path, or exercised on Android.
A second isolated ten-question spacecraft-subsystem draft addresses structure, energy, attitude, communications, thermal control and payloads. Its models pass local validation; editorial, Android and production-path acceptance are pending. It contains no private document identifiers or links.
Run 41545485465 graded the kinetic-temperature formula with a native vertical fraction, squared airspeed slot and fixed factor two in its denominator. The inspected S24-proportioned capture shows all selected quantities, the superscript, the complete bank and Check; that tested composition is now in the production course. Other multi-factor fractions and physical-device behavior remain open.
The opt-in extended second-section diagnostic now also attaches the two additional concept drafts as second sessions under 3.2 and 3.3. Production builds still exclude the research bank. Runtime navigation, saving and restart for those newly attached sessions are not yet established.
Run 41544751029 completed the synthetic Atmosphere path with batch-category observation enabled. Its batch retries contained user-route requests, but the coarse count did not distinguish their purpose; no batch response was changed. The diagnostic now distinguishes only fixed route categories and HTTP methods, without URLs, IDs, queries or bodies, and requires another Android run before identifying safe behavior.
Run 41546678011 graded ten isolated spacecraft-subsystem questions; an inspected S24-proportioned screenshot shows the longer payload/bus answer and all controls fitting. The draft was later reordered to vary correct-answer positions; real second-section progression and editorial coverage remain unverified.
Run 41546537764 graded the ten isolated space-environment questions. The inspected capture showed a curly apostrophe missing in the original math renderer; the new concept drafts were reworded to avoid that punctuation. A separate diagnostic compares straight and curly apostrophes before any global conversion is attempted; other source-bank punctuation remains to be reviewed.
Run 41546817431 tried the full-name Breguet range as a vertical two-by-two fraction. It did not crash, but the inspected capture clips the long lift-to-drag label and the bank; the controller could not complete the selection. That composition is not integrated or accepted. A narrow-width-only probe also clipped text, and the current multiline experiment must show readable labels and real taps before use.

The extended second-section progress diagnostic now requires an observed original positive feedback banner and enabled Continue for every graded 3.2 answer and the first 3.3 answer; Continue alone is explicitly insufficient. It also rejects the historically observed technical error and skip messages. Host tests cover positive, Continue-only, incorrect, error and skip cases. The existing saved-submission and restart assertions remain in place. Earlier runs using only Continue are not evidence of correct grading; a fresh Android run with the stricter assertion is pending.

The 160 dp multiline-label probe (41547841363) scored its controls, but visual inspection of both range and induced-drag selected states shows only the first line of long names (for example “fuel” and “lift-to-drag”). It is rejected; scoring does not establish readability, and full names must not be shortened. The stricter feedback checks also now test against preserved original native success and technical-skip accessibility dumps, not only synthetic examples.

Run 41548096072 reached the saved 3.2 session, restart and 3.3 question. Its original assertion was weak; a later audit found positive banners in ten of eleven captured UI dumps, while the remaining dump contained only Continue and its subsequent screenshot showed the green Amazing banner. The screenshot and XML were captured at different moments, revealing an accessibility transition race. The stricter driver now waits for a positive banner plus enabled Continue or a terminal error, rather than immediately accepting or rejecting transitional Continue. Host checks cover this distinction; a fresh Android run remains necessary.

An isolated ten-control draft splits one original thrust-specific fuel-consumption unit conversion into grams-to-kilograms and kilonewtons-to-newtons steps, preceded by word, named-quantity and symbolic introductions. Decimal arithmetic and model conversion pass locally. It is not in the course: full lesson ordering, exact historical progression migration, Android formula/touch review and editorial acceptance remain open.

The source-bank jet Breguet range uses mass-based thrust-specific fuel consumption c_T in kg/(N s); the jet exponent questions use c_e with the same units and equation. Propeller questions elsewhere use c_e for power-specific consumption in kg/J, so the jet labels must not be generalized to every occurrence of that symbol. The two jet equation introductions now say thrust-specific fuel consumption. Flexure, buckling and spar I labels now identify the second moment of area, including stress- and deflection-limit variants. Local source-model checks pass, but these longer labels still need Android readability, touch and grading tests; the currently known clipping problem remains open.

Synthetic batch diagnostic 41547577460 observed 340 PATCH batches in the broad other-user category and six batches combining GET other-user with POST shop. The diagnostic did not log paths, identifiers or payloads and did not alter responses. These may be stateful; the observed categories do not justify suppressing them or claim a completion-delay fix.

Strict progress run 41549206915 exposed the same final-answer accessibility limitation: its dump contained only Continue, while the subsequent inspected screenshot visibly showed the native green Excellent banner. The driver now waits for accessible success or a terminal error, and for this canvas-rendered case additionally requires a green native banner plus high-confidence OCR of an observed success phrase. Error/skip feedback still fails and Continue alone cannot pass. Local tests use preserved original correct and wrong screenshots; Android revalidation is pending.

The spar equation operands now explicitly say bending moment, outer-fibre distance, allowable stress, tip force, spar length and allowable deflection; thrust contributions are named momentum thrust and pressure thrust. This removes ambiguous shorthand, but increases layout pressure: these labels require the same full-name Android review and must not be treated as fitting from the host checks.

The air-gas and sound-speed introductions now name the specific gas constant for air and their absolute/static temperatures; kinetic temperature identifies heat capacity at constant pressure, and the jet formulas name gravitational acceleration. The source states air, R=287 J/(kg K) and cp=1004.5 J/(kg K). Full-length rendering is still unaccepted pending Android; the longer strings must not be truncated or abbreviated.

The TeX multiline token probe 41549545641 is rejected: the original renderer displays “Invalid command” for the substack expression and the range choice bank extends below the viewport. The branch is diagnostic only and was not merged. Full labels and touch accessibility remain unresolved.

An isolated native-card probe keeps the original token card and input callback, but overlays full multiline names on long local-course text tokens. It also tests bounded token width; both adjustments are diagnostic only and are not integrated. The probe compiles against the Android SDK, but success requires inspected Android captures, full labels, accessible Check, one-tap grading and verification of unaffected original/symbol tokens.

Run 41549776734 confirmed that waiting for accessibility alone still times out on the final celebration. Its preserved screenshot shows “Good job!” on green, which the initial OCR confidence rule missed due to the original italic font. The visual verifier now requires an exact two-word positive phrase at individually calibrated confidence plus the green panel; its regression uses that synthetic Android screenshot and an original wrong-answer screenshot. A new full progression run is pending.

Run 41550308539 tested the precise area-moment and thrust-specific-consumption labels on the existing layout. Range, structural and product-fraction jobs failed; the Breguet-exponent job graded its controls but its inspected screen cuts off the choice bank. The inspected spar fraction clips a numerator factor, and the range screen hides choices. These are explicit visual failures, including the graded Breguet case, and do not satisfy long-label or vertical-fraction acceptance.

The cold-start full-lesson driver also previously treated Continue without GOT IT as a correct grade. It now requires the current answer plus native positive feedback or the verified green celebration banner, and rejects original errors and skips. Existing progress, reward and restart assertions remain; historical runs using the weaker test must not be cited as proof of every correct grade. The strengthened driver requires another Android run.

Run 41550878175 passed the strengthened extended-section Android driver on a synthetic account: ten 3.2 answers received original positive feedback, the diagnostic submission was saved, the app restarted, and the first 3.3 answer received positive feedback. Nine 3.2 banners and the 3.3 banner are in accessibility dumps; the final 3.2 green Great banner was recognized from the captured screen and visually inspected. No Continue-only result was accepted. This covers only the diagnostic draft, not production second-midterm completeness, physical S24 or real account/Drive migration.

In the native-card multiline experiment 41551551206, the range job failed: its inspected screenshot shows long names still vertically clipped and the bank requires scrolling; Check stayed disabled with one slot unfilled. Accessibility bounds revealed that the original card adds substantial internal padding around the overlaid text. A separate diagnostic reduces that padding for long local-course labels; this is not merged and must be checked for complete text, tap behavior, scrolling and grading.

Synthetic diagnostic 41550563477 refined the prior batch observation: 338 batches were PATCH operations on the user root and six combined a user-root GET with shop POSTs. No IDs, paths, bodies or queries were logged. Since user-root PATCH may persist account state, this evidence does not justify discarding or fabricating responses; the visible completion delay remains unresolved.

In run 41551551206 the product-fraction controller did grade all sixteen controls, but the job mistakenly checked for twelve and failed its own grep; the range controller also failed. Visual inspection independently rejects the candidate: the fraction fits horizontally, but the full names are vertically clipped. The count in the padding follow-up is corrected; a graded result alone will not establish visual acceptance.

Run 41551766495 repeated the strict second-section progression with the improved two-word OCR: the final 3.2 screenshot shows the green Good job banner and the first 3.3 accessibility dump shows Correct; saving and restart passed. This remains a synthetic diagnostic path, not whole-course or real-account acceptance.

A separate experimental native fraction composes the cantilever stiffness numerator with its fixed factor 3 and two interactive quantities over a cubed interactive length. Its Java compiles and the model preserves the source equation and lesson sizes; the diagnostic branch is not integrated. It still requires Android grading, a visible fraction bar, fixed coefficient and superscript, readable full names and touch review before any vertical-fraction acceptance.

Follow-up diagnostic branches are `codex/full-name-card-padding-verify`, `codex/full-name-bank-touch-probe`, `codex/cantilever-vertical-probe`, `codex/full-lesson-positive-feedback` and `codex/completion-foam-motion-review`. They are isolated probes, not release candidates; their workflow artifacts and screenshots must be reviewed before applying any implementation to the working branch.

The follow-up font-padding-only probe 41552394084 still clips multi-line text inside native cards in the inspected spar fraction; it is rejected. Reducing only the overlay's own padding is insufficient because the original card's padding also constrains the content. The separate card-padding experiment remains under test.

Additional named operands now distinguish dynamic viscosity, flow speed and chord length, load capacity and applied force, mass flow rate, efficiency factor, and axial/cross-sectional quantities. These retain the source equations; model and lesson-size checks pass. Their full-length Android layout and touch behavior remain unverified.

Run 41552279674 passed the strengthened cold-start Android lesson: all nineteen answers required original positive feedback, followed by Claim XP, a persisted submission, ten gems and one-day streak visible after process restart, and opening the next lesson. The final green Good job banner and restored home screenshot were visually inspected. This used a synthetic local account; it does not establish the complete curriculum, a physical device or Google/Drive synchronization.

Forced-scene Android run 41552352410 completed the strict full lesson and recorded the original foam celebration with Snoopy. The forced selector was confirmed by its diagnostic trace. Its screenrecord contains only five encoded frames over 5.18 seconds; inspected frames show little visible pose change. This neither proves smooth motion nor that the production selector reaches the scene. The motion requirement remains open; the forced selector and recording hooks are diagnostic only.

An isolated foam-loop diagnostic inserts an initial transition to the existing FoamFingerDuo_Loop animation state, whose index and animation mapping were verified in both original artboards. The local Rive model checks pass, but the branch has not been integrated. A forced-scene Android recording must establish actual motion, no duplicate/overlap, and adequate frame sampling before deciding whether this state-machine change is acceptable.

Visual inspection of the sixteen source hero poses found abrupt scarf visibility/shape changes between adjacent frames. Transparent assets and a valid Rive loop alone do not satisfy the requested smooth animation; this source sequence needs correction and playback review before acceptance.

Run 41553322145 graded the long-label controls after targeting the scrollable bank, but inspected range and spar captures still cut the quantity names. Run 41553694369 graded the experimental vertical cantilever controls; its screenshot shows the fixed 3 and cubic exponent, but cuts the second-moment name and places the exponent too close to the bar. Neither result is visual acceptance or integration. The taller-card variant is still being tested.

A newly generated transparent hero sprite-sheet concept keeps the scarf visible, but the output canvas is not a divisible 4-by-4 grid and the poses have not been aligned or reviewed as a timed loop. It remains an unintegrated visual reference, not an accepted animation asset.

An isolated ten-question rotorcraft draft covers collective and cyclic control, reaction torque, flapping, forward flight, autorotation and swashplate roles. Its source-model checks pass and it contains no private Drive identifiers or links. Editorial review, original-controller Android interaction, production ordering and progression acceptance are pending; it is not yet in the course.

The 80 dp card probe 41554344300 graded the product-fraction controls and its inspected spar capture displays the full second-moment, bending-moment and outer-fibre names with a visible fraction and Check. Its range job failed to reach a bank choice; the large formula leaves a small scrollable bank. This is not yet accepted or integrated. A follow-up injects an actual bank swipe before one-tap selection to test whether the remaining options can be reached; readable full names and grading must both pass.

An additional isolated ten-question aircraft draft covers STOL/VTOL, tiltrotors, tiltwing, thrust direction, ground effect, air cushions and hydrofoils. It contains no private source identifiers or links; model checks pass. Editorial review, Android rendering and production-path progression are still required.

Forced foam-loop run 41554735865 exercised the experimental entry transition. The recorded video contains only six frames over 5.32 seconds, and visual inspection shows a doubled/overlapping head in one frame. The transition is rejected as an accepted animation change; no smoothness or clean rendering is established and the production branch is unchanged.

A follow-up foam probe confines the replacement sprite-pose tracks to the existing loop animation, so the intro and idle layers do not independently drive those poses. Structural Rive checks confirm the entry targets the original loop and no replacement sprite tracks are attached to the intro; the original scene effects remain. This is only a hypothesis until Android playback is inspected for overlap, continuity and smooth frame sampling.

Run 41555256162 increased the experimental cantilever fraction padding and still showed the cubic exponent touching the bar; the long name was also clipped. Although the controller graded the exercise, this spacing change is rejected and the fallback remains unaccepted as a vertical fraction.

A further isolated cantilever probe identifies the original fraction padding as horizontal and applies scoped vertical padding to the marked denominator instead. The helper compiles against the Android SDK; the original renderer hook and scaled-marker preservation must be exercised on Android. Neither exponent spacing nor full-label layout is accepted yet.

Run 41555884296 completed all ten isolated rotorcraft draft controls with the earlier mixed driver; inspected cyclic-control and swashplate screenshots show readable prompts, options and controls at the diagnostic text size. That driver accepted Continue as a success proxy, so the run does not by itself prove that every answer was graded correctly. This is not a production-path, full-curriculum or real-account test; the draft remains isolated pending a strict grading rerun, editorial and progression acceptance.

Further review of run 41554344300 shows the three-line deflection-limit second-moment label is still cut at the bottom even though the shorter stress-limit label fits. The 80 dp result is therefore rejected for full-name acceptance. A new isolated probe allows adaptive type sizing inside those cards, with Android readability and touch tests still required.

In swipe run 41556044451 the range scenario first failed because the driver could not find the lift-to-drag-ratio bank token; that observation alone does not establish whether the bank or the driver prevented access. In the product-fraction scenario the selected screenshot instead shows temperature, stiffness, pressure and Young modulus in the slots, followed by original incorrect feedback. The center-of-bank gesture could have selected cards accidentally; this is a selection/driver problem to investigate, not evidence that the native grader is wrong. The next isolated diagnostic moves the swipe to the bank margin, records before/after screenshots, and logs actual font scale, rendered sp, text bounds and line geometry for the longest structural and Breguet labels. Correct selection, one-tap interaction, readable text, accessible Check and explicit native grading remain separate acceptance criteria.

Run 41556512529 exercised ten isolated diverse-aircraft questions; the inspected vertical-flight transition screen shows the full prompt and choices, and original positive feedback. The automated mixed-question driver at that revision allowed Continue as a proxy for correctness, so the run alone does not establish native grading for every answer. The driver now requires the original math controller's CORRECT state and rejects error/skip feedback; matching questions require an explicit positive signal. This strengthening is locally compiled but still needs Android execution. The aircraft draft remains outside the production course.

In isolated progression run 41556913393, a synthetic account with explicitly seeded prior lesson proofs completed the additional 5.1 lesson with the stricter positive-feedback checks, restarted, and opened 5.2. The inspected restart screenshot shows the 5.1 and 5.2 path nodes; the inspected first 5.2 question shows the correct collective-control option and original green positive feedback. This demonstrates that diagnostic transition only: it does not establish production availability, migration of real progress, or full second-midterm acceptance.

Forced-scene run 41556743953 exercised the single-layer foam-loop hypothesis. Six encoded frames over 3.09 seconds show changing Snoopy poses without the doubled head observed in the preceding probe. The frame spacing is too sparse to establish smoothness, the source sequence still has visible scarf discontinuities, and the forced selector does not demonstrate normal scene reachability. The change remains isolated and unaccepted.

Scoped denominator-padding run 41557311620 reached the cantilever named-fraction exercise. Its inspected selected screenshot shows the fixed numerator 3, a vertical fraction and a cubic denominator exponent separated from the bar, but the second-moment-of-area label remains visibly clipped. The old mixed driver also did not independently require the native CORRECT state for every answer. This isolated spacing change is therefore not full fraction acceptance; it still needs the long-label solution, strict grading and combined Android validation.

The product job in measured-margin run 41558014173 did not reach app execution: Android SDK installation failed with an invalid system-image ZIP. This is an infrastructure failure, not evidence about card selection or layout; the range job and separate stricter diagnostics continue independently.

In margin-swipe run 41557736846, the older driver completed the eight range controls, but visual review of the selected full Breguet equation shows a separate layout failure: the very tall formula overlaps the options bank and some fixed operators are obscured. This is not accepted as a usable exercise, and the older driver did not require native CORRECT for each answer. The measured 12–18 sp range diagnostic 41558253920 failed earlier because its driver could not reach lift-to-drag ratio. Its provisional logs at system font scale 1.15 reported 15.90 sp for thrust-specific fuel consumption, two lines and a 168 px-high text region, but those lines do not establish that the full exercise fits or that scrolling is safe. A follow-up explicitly checks that swiping does not alter visible prompt/slot labels and preserves before/after images; layout must still be redesigned and inspected with all operands and Check visible or accessible.

An isolated long-equation probe wraps the original BuildSpace modifier in a bounded scroll region only for a local course and lists of at least seven elements. The helper and modified build script compile locally, and the smali insertion anchor was verified once in the original BuildSpace method. This broad diagnostic condition is not yet suitable for production: Android must establish usable access to every slot, visible fixed operators, a separate usable option bank, one-touch selection and native grading, including shorter and non-local exercises before any scoped integration.

Run 41558253920 completed all sixteen product-fraction controls with the updated mixed driver requiring original CORRECT and rejecting error/skip. At font scale 1.15 the instrumented label measured approximately 14.91 sp for stress-limit second moment of area and 11.93 sp for deflection-limit second moment of area, each in a 538-by-168 px text region; the measured last line bottoms were 142 and 114 px respectively. The inspected images show both full labels and Check, but the deflection label is markedly smaller and the equation abuts/overlaps the bank; its fraction is still inline division. This does not satisfy the requested legibility and vertical-fraction acceptance, despite the successful strict grade. Swipe before/after images were not exported by that workflow, so that run also does not establish that the swipe itself leaves selections untouched.

Strict mixed-driver Android runs 41558339740 and 41558345997 each exercised ten isolated aircraft and rotorcraft draft questions, with ten native CORRECT logs and explicit rejection of error/skip feedback. The inspected aircraft transition question remains readable and displays original positive feedback. These results do not yet establish complete editorial coverage, production availability or real-account progression.

The 80 dp card's text view measured only 168 px tall in the 1440 px-wide emulator capture, leaving the longest name at roughly 12 sp despite the larger outer card. A separate experimental branch tests 96 dp cards with a 14 sp minimum, the bounded long-equation region, and additional host-size/padding logs. The interaction between taller cards, scrolling and the bank is unverified; screenshots and native grading, not the configured minimum alone, determine acceptance.

Static inspection of the original user update path found that its PATCH serializes `UserOptions`, whose model can include streak data, XP gains, course and language settings as well as other account options. Its batching factory conditionally adds additional requests when course or source-language fields are present, and its batch response converter dispatches individual responses to their respective operations. These findings identify possible stateful work, not the contents or purpose of the repeated synthetic requests; counts alone cannot justify suppressing or fabricating them. Local completion currently validates the submitted lesson, atomically writes and reads back its proof and study days, and derives the local streak and lesson gems from durable records. Chest gems have a separate store. Any eventual latency correction must preserve those operations and restart checks.

An isolated synthetic completion-timing build observes the real session activity's touch-up event and the original session-complete view's first visible CTA pre-draw using the same Android monotonic clock. It delegates all input unchanged and does not force completion or alter responses. The standalone driver retains native feedback, saved-progress, gems, streak and restart assertions. Its exported log is restricted to timing events; raw app logs and ANR traces are excluded. The view-created and pre-draw events are lifecycle proxies, so their relation to the visible Claim XP screen still requires screenshot review, and no timing result or latency improvement is asserted yet.

Combined diagnostic 41558914581 exercised the experimental vertical cantilever fraction with the adaptive full-name card and strict native grading. The inspected selected screen shows the full second-moment-of-area label, fixed 3, multiplication signs, vertical fraction, separated cubic exponent and accessible Check; the measured label was about 16.89 sp at font scale 1.15. This is encouraging evidence for that one formula, not acceptance of the smaller deflection-limit label, the larger Breguet layout, all product fractions, production scoping or swipe safety. The changes remain isolated.

The first swipe-selection assertions in runs 41559810299 and 41560105034 reported that pressure had appeared above the old bank boundary. The preserved before/after images show the equation slots still empty: the scrolled bank exposes accessibility children outside its own visible bounds, so a screen-coordinate cutoff misclassified a bank label as a selected slot. This was a diagnostic false positive, not proof of an accidental selection. The follow-up excludes the entire original bank accessibility subtree when comparing surrounding labels, retains the screenshots and requires native grading; it has not yet established swipe safety.

Forced-scene run 41559082734 tested a constant scale across the differently sized foam pose images. Its seven encoded frames over 4.32 seconds show varying poses without the earlier doubled head, but the recording is too sparse to judge continuity; the source artwork still needs frame-by-frame repair. This scale experiment is not integrated or accepted as a smooth animation.

The long-equation screenshots from the first bounded BuildSpace probe show that the Breguet row still occupies most of the screen. Inspection explains why: multi-slot inline equations compose their own wrapping row and call the original per-slot renderer, bypassing the full BuildSpace method that was bounded. A new isolated probe applies the bound to that actual row only for inline equations with at least four holes. This remains a hypothesis: the diagnostic must verify scrolling the equation itself as well as selecting all bank items and grading, without hiding operators or Check.

The original queued user-update factory builds a user-options PATCH and can add a course request when a course is specified and a shop-items request when a source language is specified. It does not establish which options occurred in the earlier retries. A separate synthetic timing branch aggregates only pre-approved field categories (streak, XP, course or other, plus unparsed/empty) and counts; it exports no field values, user identifiers, URLs, request bodies or query strings. Its new observer compiles locally. It does not discard a request, fabricate a batch response or establish any latency cause until the Android run is reviewed.

The initial isothermal-rendering run 41558981482 drove raw source answers against an expanded staged session and failed on the wrong control; it was not a valid rendering result. The fixture now disables expansion for this isolated original-question probe, and run 41560441553 reached original CORRECT for all ten. The inspected first and last prompts render the atmospheric exponential as a raised e with the negative fraction and subscripted base pressure. Both original unsplit prompts are visibly cut at the bottom of the prompt area, however, and the exponent is small. Those screenshots do not accept the original long questions or the full course; the separately staged shorter production exercises still need their own UI and migration coverage.

The swipe comparison now has an isolated read-only probe of the original inline controller's ordered slot objects: it copies each slot's original type and token identity before and after the gesture, without changing the controller or exporting the identities. A real token tap must also change that observed state, so a stale observer cannot silently pass. This applies only to named inline equations; screenshot and geometry evidence remain complementary. The code compiles locally and Android execution is pending. Changes in visible text alone are not treated as proof of selection.

A contact-sheet review of the existing Sally sad source poses shows expressive artwork but irregular open/closed eye changes across adjacent frames. Distinct transparent PNGs and the Rive timeline test are insufficient to establish smooth character animation; the sequence and real playback still need correction and review, in addition to the Snoopy scene work.

In range diagnostic 41561438237, bounding the actual inline equation row kept the initial bank and Check visible; the native controller reported CORRECT for all eight controls. The selected Breguet screenshot shows the long fuel-consumption and gravity labels, with the former measured around 16.15 sp at font scale 1.15 in a 538-by-224 px text region. The lower mass-ratio slots are outside the initial viewport, and that driver did not scroll the equation or compare original slot state, so this is not accessibility or gesture acceptance. An isolated follow-up adds a concise scroll instruction, performs a real swipe on the equation, captures the lower region and checks that the original selected slots and Check remain intact. Its code compiles locally; the result is pending.

Timing run 41561841435 failed during compilation because the visibility probe incorrectly initialized a ViewParent with a View; the traversal has been corrected and the helper compiles locally. Run 41561867733 failed earlier downloading a locked build dependency with HTTP 404, before compiling the instrumented APK. All locked dependencies subsequently answered HEAD successfully from the local environment, so their identity was not established by that failure. The build helper now retries bounded transient download errors, verifies the existing pinned checksum before atomic publication, and removes partial files; local tests cover transient, persistent and checksum failures. Frozen updater sources still pass their lock verifier. A full Android diagnostic build and execution remain necessary; neither failure was a latency or app-function result.

Earlier synthetic full-build timing runs 41560966704 and 41561595125 did run the real nineteen-answer first lesson and passed the existing saved-progress, ten-gem, one-day streak, restart and next-lesson checks. Their same-clock observer reported summary view creation 8.32/7.42 seconds after the last touch and the first CTA pre-draw 16.53/15.96 seconds after it. Inspected captures show the original Claim XP screen and the restored path with rewards. These are emulator observations, not physical-device timings; the earlier pre-draw observer did not check ancestor alpha, so the refined visible-CTA version still needs its own full run.

The synthetic category observer in run 41561595125 counted repeated user PATCHes containing at least one pre-approved streak-category field and at least one other field; it did not export names outside the allowlist or any values. The patch category includes both streak data and timezone, so this result does not identify the exact field. Repetition continued after the summary appeared; it does not by itself prove that retries caused the transition delay. No batch operation has been discarded or acknowledged artificially.

In the product job of run 41561438237, the original controller returned CORRECT for all sixteen controls. At font scale 1.15, both the actual stress-limit and deflection-limit names measured about 15.15 sp in three lines within 538-by-224 px text regions; the last line bottom was 216 px. Inspected captures show the full names and Check, but the deflection expression still uses inline division instead of the required vertical multi-factor fraction. The independent original-slot gesture check and the vertical fraction therefore remain open.

Static inspection of the original expression controller shows that bank options are constructed as `qp3` objects using their option-list index and figure, and the fill operation copies the selected `qp3` into the first empty `pp3` slot. Thus `qp3.getId()` represents the selected bank item in this path, while list order identifies the hole; it is not merely the hole index. A new isolated Android check nevertheless removes a placed token with a real touch, fills the same hole with a different bank token, compares the two filled snapshots, then removes it and restores the original through real touches before normal grading. No token identities are exported or state assigned. The check compiles locally and has not yet run to completion.

The product job of Android run 41562172614 completed sixteen exercises with native CORRECT checks while comparing the original named-equation slot state across bank swipes; it also required each real token tap to change that observed state. The evidence contains 72 before/after swipe screenshot pairs; one inspected pair shows the bank moving while the formula remains empty. This is evidence for those synthetic named-equation gestures on that emulator, not the requested filled-to-filled replacement check, all screens or the physical phone. The full-to-full replacement probe remains pending.

An isolated deflection-fraction prototype represents the named equation as a native vertical fraction with tip force times a cubed spar-length slot over fixed 3 times Young modulus times allowable deflection. It retains four interactive original slots and the same mathematical formula. Its Python and Java sources compile locally; no Android rendering, touch, grading, layout or production integration is claimed until the full diagnostic runs and screenshots are inspected.

The range job of run 41562172614 likewise returned native CORRECT for all eight controls, with 49 preserved before/after bank-swipe image pairs and unchanged observed slot state through each named-equation swipe; each token touch changed the observed state. It did not yet prove filled-to-filled replacement or that the initially hidden bottom of the equation is reachable. The dedicated replacement and equation-scroll checks remain pending.

The corrected timing candidate in run 41563162860 has now passed the complete diagnostic APK build and assembly step, rather than only separate Java compilation or anchor checks; its Android lesson and visibility measurement are still running. The isolated vertical-deflection source fixture also passed a local check that its original named answers remain in order and its fixed fraction marker is present; that check does not establish native rendering or grading.

In the range job of run 41562719696, the user-facing instruction indicates that the formula can scroll. A real swipe of the original equation region preserved the observed native slot state and left Check accessible; the inspected post-swipe selected screenshot shows the lower initial-mass/final-mass fraction and logarithm, and the original controller returned CORRECT for the eight controls. The dedicated bottom-image filenames were not exported because their pull command was placed under the wrong workflow condition, but the already exported post-swipe selected screenshot provides the visual evidence. This remains an isolated emulator result; filled-to-filled replacement, other formula families and production scoping remain pending.

An additional diagnostic replaces the global card-height and width changes with a named-equation-only sizing hypothesis: it scopes placeholder sizing to the inline equation composition and recognizes named bank tokens by their existing local figure marker. It compiles with the corresponding experimental scroll helper. Compose lifecycle, named versus symbolic sizing, real touch, accessibility and cross-challenge isolation all still require Android verification; this is not a production change.

The synthetic completion probe now also records monotonic timing immediately before and after the existing durable-submission operation, including its unchanged local reward refresh. It logs only fixed stage categories and durations, never submissions or account data, and does not acknowledge anything differently. This should help distinguish persistence cost from subsequent view creation and drawing; whether submission precedes the final touch must be established from the event ordering in the completed run.

After correcting the build failures, full diagnostic runs 41563162860 and 41563330977 both passed the standalone lesson, original feedback, local completion, rewards, restart and next-lesson checks. Their refined observer required a globally visible CTA and nontransparent ancestors: summary view creation occurred 4.47/6.07 seconds after the last touch and CTA pre-draw at 15.27/12.62 seconds in these emulators. A reviewed screenshot shows Claim XP. The second run's allowed field categories identify timezone plus another unclassified non-null field in the repeated synthetic PATCHes; no streak-data field was reported in that run. These observations do not establish which component causes the delay, and no request has been suppressed or fabricated.

The vertical-deflection prototype completed sixteen controls with native CORRECT in run 41563867546. The inspected selected screenshot shows the cubed spar length above a vertical bar and fixed 3 times the two denominator quantities, but the full deflection-limit name measured only about 11.93 sp. This is not legibility acceptance. A distinct combined probe now tests the same vertical layout with the 96 dp, 14 sp-minimum cards and read-only slot checks; its rendering, substitution, one-touch and grading outcomes remain pending.

An image-generation attempt produced a transparent Sally sad sprite-sheet reference with an intermediate blink. The 1247-by-1261 canvas is not divisible into an exact 4-by-4 grid and the outlines show colored edge artifacts. It has not been integrated or verified as a smooth, clean animation; it is a reference for further repair, not an accepted replacement.

In the product job of run 41563521655, the original controller exercised the targeted named axial-stiffness question and the driver completed all sixteen controls with native CORRECT. Its read-only slot assertions compared a first filled state against a different filled state after real remove/select touches, then required the original state after real restoration. The targeted question was present and the complete driver passed, so the state comparison ran; however, this version of the workflow did not export the three dedicated substitution screenshots because their pull loop was under the wrong condition. A corrected evidence-preserving run is still required before treating the visual interaction as fully reviewed.

The two isolated 5.1 and 5.2 extra-question drafts now replace their obviously unrelated distractors with competing aircraft/rotorcraft concepts, while keeping the question IDs and correct-answer positions. Their host model and privacy checks pass. The earlier Android runs exercised the previous wording, not these revised options; source-by-source editorial verification, an Android rerun, production ordering and historical progression migration are still required before connecting these drafts.

The extended second-section diagnostic now orders the revised aircraft and rotorcraft drafts as the second session under 5.1 and 5.2 respectively. Only the opt-in non-production fixture changes: there is no historical release proof for these draft sessions, so no migration or rewards are granted. The final-topic diagnostic seeds every actual earlier fixture session and requires original positive feedback instead of accepting Continue alone. The revised lessons and this ordering still require an integrated Android run and course-source editorial review; no production section is enabled by this change.

The named-only sizing probe 41564668057 passed its eight Breguet controls but failed during the deflection lesson with `Native answer bank has no usable scroll area`. The inspected prompt shows very wide empty placeholders while a filled card is much smaller and taller; Breguet success does not establish correct recomposition or reachability. The native replacement observation passed, but the workflow still nested the corresponding screenshot pulls under the formula condition, so those images were not exported. A separate candidate scopes sizing within the deferred row and fraction callbacks and captures the empty-after-removal state; its Java helpers compile, but its full Android build and visual/touch checks are pending. It is not integrated.

Synthetic completion run 41564816912 observed 91 ms across the original local persistence and reward-refresh call, with summary creation at 3.503 s and the visible, enabled summary CTA at 9.982 s after the last touch. Run 41564975893 measured 147 ms across the same persistence boundary, with summary creation at 3.384 s and visible CTA at 14.098 s; the restricted patch classifier recorded only the categories timezone and account metadata in its sampled synthetic requests. This narrows the investigation but neither isolates the cause nor proves physical-device latency. Both full Android runs retained the completion, restart, reward and next-lesson checks.

Further inspection of the preserved failure hierarchy for 41564668057 distinguishes the test failure from the layout defect: the answer bank had a visible scrollable region from y=1614 to y=2742, but the driver's depth-first `lastScrollable` selected a nested 78 px region and rejected it as unusable. The driver must select a usable bank ancestor instead. The screenshot still independently shows the inconsistent empty and filled slot geometry; neither the driver error nor the earlier Breguet pass settles its cause or acceptance.

Vertical-deflection run 41565472095 graded all sixteen controls with native CORRECT. In its inspected selected screenshot the complete deflection-limit second moment of area label is legible, the spar-length exponent and numerator/denominator factors remain in a vertical fraction, and Check is visible; the measured label is 15.155 sp at font scale 1.15, with three lines inside a 538-by-224 px text region. This diagnostic still uses globally enlarged cards and does not establish unchanged symbolic/non-local sizing or clean transition through empty states. Its replacement captures were also not exported, so the prototype remains isolated.

Synthetic animation-callback run 41565240859 observed summary creation at 6.061 s after the last recorded touch, animation-loaded callbacks at 7.755 and 7.864 s, the original CTA-animation callback at 13.973 s and its enabled visible predraw at 14.769 s. These are observational emulator timestamps, not a cause or S24 measurement. The recorded persistence call occurred later in that particular run, so it must not be treated as proof of a mandatory ordering before the summary. Original card animations are sequential; no network response or state transition has been bypassed.

Editorial comparison with the authorized course material supports the revised concepts of collective/cyclic pitch, reaction torque, flapping and retreating-side stall, autorotation, V/STOL, ground effect, air cushions and hydrofoils. The near-surface question now asks specifically about unexpected loss of clearance. This comparison does not establish exhaustive syllabus coverage or replace native lesson validation. Android attempt 41566619516 opened the locked rotorcraft popup because the test matched a background header; 41567902115 then left the app while trying stale path coordinates and encountered an emulator Play Services ANR. Neither run graded the revised aircraft lesson. The driver now locates the intended node under its exact section header and requires its own title and enabled button; its new run is pending.

Synthetic extended-path run 41569108065 graded all ten revised 5.1 extra questions with native positive feedback, saved the completion, restarted and graded the first original 5.2 question. The inspected near-surface question and green feedback show all four options and the corrected answer. Prior sessions were seeded for this diagnostic; this is not proof of an end-to-end production curriculum, real-account migration or the revised 5.2 extra lesson. A separate strict diagnostic now exercises that rotorcraft lesson and its saved completion after restart.

The scoped summary-pause candidate passed full synthetic run 41568625858: 19 original correct answers, Claim XP, saved completion, ten gems and one-day streak after restart, and the next lesson. Its measured summary creation, animation load and visible CTA were 2.358 s, 4.341–4.445 s and 11.723 s after the last recorded touch. This separate-emulator run is not evidence of improvement; a base-versus-candidate run on the same emulator with the same driver and clock stages is pending. Static inspection identifies the two changed 600 ms constants as an animator start delay and a separate empty delayed AnimatorSet; transition durations and the original callback are retained.

Run 41570552686 completed the revised 5.2 rotorcraft draft through the original controller, required positive feedback on all ten answers, and verified its saved completion after a restart on the synthetic path. An inspected advancing-blade prompt fits its four options and Check. The diagnostic seeds earlier fixture progress and does not establish production availability, exhaustive syllabus coverage, or real-account migration. The companion 5.1 draft was similarly exercised in run 41569108065; both remain outside the production course until ordering and course coverage are accepted.

The isolated space-environment draft now uses concept-related alternatives in place of unrelated distractors; its gravity-assist question explicitly specifies an ideal unpowered flyby and heliocentric motion. IDs and correct-answer positions remain unchanged, and the host model check passes. The revised wording has not yet been checked against all course sources or exercised in Android; the earlier run used different wording and does not validate this revision.

Paired run 41570405615 exercised the baseline and scoped pause candidate sequentially on the same emulator, including original grading, Claim XP, gems, streak, saved progress, restart and the next lesson. Baseline times from the last touch were 4.591 s for summary creation, 5.923 s for the later animation load, 10.235 s for the CTA animation and 10.938 s for the enabled button predraw; candidate times were 5.750 s, 7.103 s, 10.978 s and 11.632 s. The later-load-to-CTA interval was 4.312 s versus 3.875 s, but the total was longer for the candidate and a single pair cannot establish an end-to-end improvement. The candidate's visible summary was inspected and its controls fit; the delay issue remains open. The candidate run also observed many account-metadata/timezone PATCH retries, a category count rather than evidence of their cause or permission to change them.

The tested pause adjustment is now in development: only the two original 600 ms start waits in the stat-card sequence are capped at 200 ms for an installed local course. The original 300 ms transition, animator sequence, callbacks, persistence and rewards are unchanged; nonlocal courses retain the original wait. This is an adjustment to a measured presentation interval, not proof that overall completion is faster. The earlier delay before the summary remains under investigation.

The spacecraft-subsystem draft also now uses alternatives about actual subsystem roles and operating constraints, preserving IDs and correct-answer positions. Its host model check passes; these revised choices still require source review and Android grading. Earlier Android results used the previous wording and do not validate this revision.

The ten introductory launch-vehicle draft questions retain their IDs and answer positions, with distractors revised toward competing launch and propulsion concepts. The 60-item draft validator passes. The new wording still requires course-source editorial review and a fresh native-controller test before acceptance; the previous Android runs used the earlier wording.

The product job of 41571860608 built and verified the diagnostic APK after preserving source ZIP metadata. Its native controller graded all 17 local exercises correctly, and the reuse probe restored the original card padding; the correct, removed, replacement and restored slot states were captured. Nevertheless the job failed when the separate synthetic nonlocal control crashed in an OkHttp dispatcher before it opened the exercise. No nonlocal rendering isolation is established. The inspected long deflection fraction is also cropped at both the equation viewport and the bank edge after selection, despite correct grading and an accessible Check. This is not visual acceptance; the bank and equation geometry still need correction and a fresh combined run.

The independently verified ZIP metadata repair is now in development without the unaccepted interface changes. Both archive-copy loops write copies of source ZipInfo objects, leaving source offsets intact. The build rereads the original math lesson after copying and compares its bytes in the unsigned, aligned and signed test APKs. A host regression also confirmed source offsets and destination integrity; the combined product job above built and signed an APK with the same repair. The newly integrated tree still requires its own complete build and acceptance run.

Static investigation of the remaining batch retries found that the original batch converter expects a `responses` list, each response containing a string `body`, integer `status` and string-keyed `headers`; the original controller pairs responses with requests and applies each outcome separately. The local fallback currently returns 503 for this batch rather than persisting its operations. This partial envelope is not enough to implement a truthful response: the concrete account-metadata update and its account-scoped durable representation, the inner response bodies and unsupported operations still need to be established. No batch success has been fabricated or requests discarded. The relationship between these retries and the pre-summary delay remains unproven.

The next isolated named-equation candidate adds trailing space inside the named formula's scroll content, so the last fraction operand can move fully above the answer bank. Its Android check now captures the long deflection and range equations before and after real scroll gestures and still rejects changes to the original selected-slot state. The nonlocal crash observer records only exception types and code locations, preserving the original handler and not recording messages, requests or identifiers. Both changes are diagnostic candidates pending the new run; correct scrolling, legibility and nonlocal isolation are not yet established.

Run 41573009148 exercised the revised 3.2 and 3.3 extra lessons in one synthetic diagnostic build: each received ten strictly observed native positive outcomes and its completion was saved after restart. The 3.2 run also opened and graded the first next-topic question; the 3.3 run seeded prior diagnostic proofs separately. Inspected solar-panel and electronics-temperature prompts and all four options fit. This is not a continuous unseeded course traversal, source-by-source editorial acceptance, production availability or a real-account test.

Run 41573512447 exercised the revised 3.1 launch questions without seeded earlier lesson progress: all ten required original positive feedback, the lesson was saved, and the next rocket session opened and received positive feedback on its first exercise after restart. An inspected ascent-loss question and its options fit. This is the opt-in synthetic second-section fixture, not production availability, complete second-midterm coverage or real-account progression.

The base 3.2 space-environment and 3.3 spacecraft drafts now also replace unrelated distractors with alternatives drawn from the same mission concepts, preserving IDs and correct-answer positions. The draft validator passes. A strict synthetic-path driver for both revised lessons is prepared and compiles; its Android grading, restart and visual results and further course-source review remain pending. The extra-lesson run above seeded these base lessons and therefore does not validate their revised wording.

The ten topic-4 concept draft items likewise retain their IDs and answer positions while using alternatives about guidance, sensors, forces and propulsion. The source-bank validator passes; course-source review, strict native grading and progression are still pending. No production path has been enabled by this editorial work.

Both jobs in 41574394523 crashed before grading: the new scroll helper replaced a three-argument method still called from the original hooked `fz0` code, producing `NoSuchMethodError`. The next candidate restores that original signature and delegates it to the unchanged behavior, while the four-argument named-only call adds trailing space. Both signatures compile and are present in the Java class; only a full Android run can verify the integrated DEX and geometry. Its nonlocal rendering fixture keeps the offline interceptor active and switches only the local-course rendering gate immediately before opening an original expression; this is an isolated render control, not a remote-course or account test.

The integrated ZIP/progression attempt 41574814072 failed before compilation because SDK Manager received an invalid system-image archive. It is not evidence about the APK. The diagnostic workflow now retries SDK installation once using the same packages, with a separate temporary directory per attempt and explicit emulator/system-image checks; failure on the second attempt remains a failure. The integrated APK build and progression check must still be rerun.

An additional read-only factory observer in 41574686668 recorded the original summary-fragment factory at 3.874 s and its view creation at 3.926 s after the last touch, followed by the enabled button predraw at 9.911 s. The full synthetic progression, rewards and restart checks passed. In that run, only 52 ms separated factory invocation from view creation; the earlier interval precedes that factory, but this single observation does not identify a cause or establish that the batch retries caused it. The observer changes neither navigation nor persistence.

The release-shaped development build now includes the reviewed 3.1–3.3 foundations: seven stable session IDs contain 10–11 controls each, and no published history or migration credits any of them. A diagnostic mode constructs that same limited path without publishing it; the updated driver inspects its packaged section/catalog/migrations before testing real completion, restart and the next session. This integrated build and continuous traversal are still unverified on Android, and the later second-midterm blocks remain diagnostic until accepted. `MIDTERM2_COVERAGE.md` records the remaining outline. Topic-4 questions on guidance, navigation, control and aerodynamic surfaces were subsequently clarified against the course concepts; the earlier topic-4 Android pass used the previous wording and cannot validate these revisions.

The ideal-rocket lesson now explicitly teaches its constant effective exhaust-speed and no-external-force assumptions before the equation, and its named tiles consistently say “effective exhaust speed”. This adds one question without changing the session ID or granting historical credit. The updated wording and long tile need fresh Android layout and grading checks; the earlier ten-control run used shorter labels.

In 41575566733 the overload prevented the prior `NoSuchMethodError`, but product selection failed because the formula disappeared; the range job then found no scrollable equation. Inspection traced this to using the original Compose size-constraint modifier as if it were padding, setting the maximum width to zero. The next candidate uses the original four-edge padding modifier instead. Before Android it verifies the final APK DEX references and definitions for both scroll-helper descriptors; the verifier passed on the earlier working APK and rejected the actual APK missing the three-argument method. Geometry, slot replacement and the separate nonlocal render control still require the new Android run.

The integrated first-midterm APK run 41575694914 passed assembly, signing with the diagnostic key, cold start, 19 native correct answers, Claim XP, ten gems and one-day streak, restart, and opening the next lesson. The revised base 3.2 and 3.3 concept lessons also passed ten strict original-feedback checks each and retained their own completion after restart in run 41575180477; each used seeded prior diagnostic proofs. Inspected prompts and choices fit. Their course concepts were subsequently compared with the supplied outline and source material. This evidence does not substitute for a continuous unseeded run or real-account migration.

The integrated section attempt 41577933272 failed during APK construction, before Android: the rocket fixture still asserted ten questions after the explicit assumptions question increased the lesson to eleven. Its result establishes neither navigation nor grading. The fixture now requires exactly eleven, and the existing rocket, orbit and concept validators pass. The earlier workflow also set the packaged-course test switch only in its build step; the next diagnostic passes it directly to the observation driver and requires an explicit packaged-section/catalog/migration success marker. A separate unseeded seven-session journey driver has been prepared with original-controller CORRECT checks, real Claim XP and completion records; it is not accepted until its Android run and restart check succeed. It includes diagnostic answers only in the non-production APK.

The regenerated first-midterm heuristic reports 278 unstaged source stems over 300 characters and 535 possible calculations without authored hints; the latter fell from 536 after staging one conversion and still includes conceptual prompts. Review of TA1-0244, TA1-0409, TA1-0812, TA1-0869, TA1-0937 and TA1-0765 found definitions, layer behavior or ISA labels rather than calculations needing a formula hint. EX-2025-11-06-4 asks for an approximate temperature but gives neither temperature nor Mach, so it cannot support an unambiguous calculation hint without adding assumptions; it remains for editorial review. TA1-0832-D3 is a real coupled range calculation and remains pending its square-root teaching and staged path.

The original TA1-0173-F1 TSFC conversion is now staged into one-operation grams-to-kilograms and per-kilonewton-to-per-newton calculations. Three preceding word, full-quantity and symbol sequences teach the actual relations; the last hint shows the consumption conversion instead of the related thrust conversion. The original question ID, options and answer remain intact. Its 14 exercises form a new fourth session in the adjacent node of the same subtopic, keeping every node within four sessions and every lesson within 10–20 controls. The new session has no migration or historical completion credit. Historical snapshots establish that the source belonged to the former lesson, while its old exact proof remains recognized by the existing history validator; no extra rewards are written. Host arithmetic, path, ID, migration and original completion-boundary checks pass. Touch, long quantity labels, hint retry, old-account transition and UI rendering still need Android verification.

Run 41578714323 explicitly inspected the packaged seven-session section, catalog, diagnostic answer ordering and absence of historical credits. In Android it then completed the first 3.1 session, verified its saved completion and path after restart, and received original positive feedback on the first rocket word exercise; the inspected capture fits. It did not complete the remaining six sessions or test a real account.

A further source-reviewed 3.3 mission-typology draft distinguishes flyby,
orbiter, atmospheric probe and balloon, penetrator, rover and station roles;
it also covers solar/Earth occultation and rover communications delay. Ten
unique native-model questions pass their host checks. They remain an isolated
draft: the current seven-session path and historical rewards are untouched,
and Android grading, layout, lesson placement and complete course coverage
remain pending.

The unseeded journey attempt 41580217194 built its diagnostic APK and started
Android, but stopped before any lesson when the picker label rejected an
accessibility click. Its passive mid-lesson observer saw no scene before that
failure. This does not invalidate the earlier independently successful picker
and first-session test or prove a product navigation defect. The journey
operator now uses a touchscreen tap at the exact visible row bounds, as the
successful picker driver did, and retains picker captures; all seven-session,
real-scene and restart claims remain unverified until rerun.

TSFC run 41580628330 reached the hint, retained the calculation until Check,
and displayed incorrect feedback. Its later failure screenshot shows the
same-looking conversion screen with the original “Previous mistake” banner;
the accessibility tree does not expose the rich prompt as a continuous string,
so the old text predicate could not recognize it. That image supports, but does
not by itself prove by identity, that the original question was requeued. The
next probe reads the original session visual state's challenge index and resolves
its exact challenge ID, checks it before and after the hint and again on retry,
then still requires native CORRECT on the retry. The screenshot also exposed
scientific notation rendered as plain text; the authored options now carry
explicit LaTeX for the multiplication sign, exponent and units, and the hint
uses upright unit subscripts. These changes still require fresh Android review.

In 41579795660 the equation-specific touch gesture enabled the range job to
pass all eight native answers; after three swipes its inspected final mass
fraction is fully visible above the bank and Check remains available. Product
passed all 17 local answers, with the filled-to-empty, replacement and restored
native slot evidence retained; the inspected deflection denominator becomes
visible after scrolling, while part of the bank remains outside its viewport.
The job then failed its separate purported nonlocal check because that test
turned off `localCourseInstalled`, which also turns off the local profile/course
service and led to the original welcome flow. This does not establish either a
remote rendering regression or successful nonlocal rendering. A revised
isolated control keeps the offline local service and authentication intact,
uses an unchanged original unmarked expression, and reports only that limited
rendering scope; it also checks unmarked original token sizing and reuse on the
original model. This control and visual layout still await Android validation.

In unseeded attempt 41581428051 the touchscreen picker correction opened the
original lesson activity, but the driver immediately searched for an answer
card while the inspected screen still showed its loading animation. No answer
or completion was recorded, and the natural mid-lesson scene was not observed.
The next driver waits for the first original exercise control after each real
session opens, without altering lesson state; the journey itself remains
unverified.

A narrow notation audit found 44 source fields containing explicit
`number × 10^integer` notation. The shared text converter now emits each such
expression as one LaTeX number with a multiplication sign and exponent; ordinary
prose remains text and explicitly authored rich text still takes precedence.
A bank-wide host regression checks all 44 occurrences. A one-question Android
fixture using an original scientific-notation question is prepared, but its
rendering, selection and layout have not yet been observed on Android.

A further ten-item 3.2 environment-systems draft now covers additional
microgravity, vacuum, radiation, thermal, electrical, life-support and
relativistic-clock concepts. Its host model and answer checks pass against the
selected course material, but it is not in the course and does not grant
progress. Detailed editorial and original-controller Android checks remain
pending.
