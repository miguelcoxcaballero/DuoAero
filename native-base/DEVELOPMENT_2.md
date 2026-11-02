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
the revised nine-exercise Android diagnostic and changed lesson migrations
must run before this later change is accepted.

The notation converter now recognizes balanced square roots, nested simple
fractions and several lift/drag subscripts without converting ordinary prose
or simple unit paths. A source-bank audit found 125 previously plain `sqrt`
occurrences converted; this is not a complete LaTeX audit. The `sqrt-mixed`
Android diagnostic must render and grade a representative original question
before device acceptance is claimed. The later denominator case such as
`1/sqrt(CLmax)` is covered by a host assertion, not yet Android UI evidence.

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
currently covers only the ideal-gas equation, not all formula families.
The gas sequence is now ordered as a word sentence, the full named-quantity
equation, the one-quantity symbolic equation and finally the symbolic blocks;
the revised order still needs Android interaction testing.

The old path check counted source items but missed word and named-formula
expansion: nine lessons therefore exceeded 20 visible exercises. Four nodes
were rebalanced between their existing session IDs. Three more nodes are now
split into three lessons, keeping prior IDs and introducing three new IDs;
all 82 lessons have 10–20 visible exercises in host validation. For each new
ID, path-only credit is derived only from an exact stored historical proof
that includes every question moved there. No synthetic completion, XP or gem
award is created. A replay or Drive import retains the historical proof when
it covers questions omitted from the new shorter source lesson. Local tests
verify mapping coverage in every published 1.3.x snapshot and the pure
projection boundaries. The Android account, chest, replay, export/import and
real path tests for this split are still required; no real Google or Drive
migration has been established.

Two static, transparent Snoopy illustrations target explicitly identified
reading and gem-holding resources. A diagnostic drew the reading resource IDs;
that is not evidence of the actual screen or of animation. The gem pose and the
original screens still need inspection. Many generic mascot scenes and the
articulation and smoothness of animations remain unfinished.

An experimental 16-frame transparent wave is bound to the original
`duo_happy` ImageView without modifying notification RemoteViews. It uses
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
animated drawable after the original quit layout inflates. This fix requires
another Android run and a screen recording; feedback remains static.

The separate two-section diagnostic shows both section cards in the original
picker. Its first test tapped the second card only once, expanding it rather
than opening the inner row. Android run 41374119769 tapped the inner row and
actually showed the second section's diagnostic path; the test failed only
because it expected a topic title where the original header showed Midterm 2.
The follow-up on the separate research branch passed Android run 41375262771:
the second topic title appeared and its synthetic lesson opened. There is no
production second-midterm content, nor evidence yet for grading, persistence,
rewards or a real course there. Twenty conceptual questions exist only as an
isolated draft on that research branch.

Android run 41372273142 also graded the five-step isothermal pressure-ratio
diagnostic. Its screenshot shows the final ratio question and the hint button;
this is a sample, not complete lesson or course verification. A subsequent
full-lesson timing run was interrupted by an unrelated Pixel Launcher ANR
dialog in the emulator; the test now dismisses only that external dialog.

The original energy-rewards request returned repeated local 503 responses
during lesson completion. An experimental empty response uses the original
model's required `inLessonRewards` field for this unlimited-energy course;
gem chests use a separate store. Model decoding, end-to-end timing and native
chest rewards must be checked on Android before claiming any speed improvement.

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
