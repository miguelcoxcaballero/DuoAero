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
