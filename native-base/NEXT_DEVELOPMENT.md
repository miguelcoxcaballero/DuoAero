# Development after the 1.3.5 preview

This branch is experimental and is not represented by the 1.3.5 release APK.
Do not publish it as a finished product. It has 69 authored hints, including
TA1-0148; the rest of the calculations still need reviewed hints and
prerequisite formula-block questions. Only the TA1-0148 hint has been verified
in the actual course on Android. Many long problems and math expressions still
require review.

## Evidence

* The independent hint prototype passed a native emulator session, including
  the original retry interstitial and Claim XP (Actions run 41339078448).
* The first actual Atmosphere lesson passed a hint/retry/completion/restart
  scenario in run 41340357867. Earlier path nodes were seeded, so this does not
  demonstrate an uninterrupted course or Google/Drive persistence. Evidence is
  in `original-runtime-evidence-atmosphere-hint`, including
  `atmosphere-result.txt` and `atmosphere-hint-open.png`.
* The four reviewed Mach steps passed actual native answer selection and
  grading in run 41340936049. The images `lesson-answer-4.png` through
  `lesson-answer-7.png` show the individual steps. This is a diagnostic lesson,
  not a full course test.
* Four formula-block prerequisites and corresponding hints have since been
  inserted before those Mach calculations. Run 41343794820 graded all four
  blocks correctly, and run 41343977624 graded a diagnostic mixed sequence
  including the alternating Mach formula/calculation steps. A hint/retry
  diagnostic reached the repeated question but its locator failed; a corrected
  driver has been queued. Real-account progress migration remains unverified.
* TA1-0078-D2 has been split into two short calculations, each preceded by a
  formula-block exercise. Its arithmetic, prerequisites, stable lesson ID and
  maximum lesson size pass host checks. Android interaction and the migration
  of a real account are not yet verified.
* Device run 41339958992 completed its normal progression test, but its
  `standalone-celebration-00.png` through `-05.png` show the generic doghouse
  Snoopy, despite the new buff-character Rive artboard preview working in
  isolation. Therefore the actual completion screen replacement is **not**
  verified. Do not claim that every scene has a matched animated character.
* Character sprite tests establish alpha and valid native tracks only. They do
  not establish visual smoothness or that every character scene uses the new
  asset on Android.

The separate `codex/peanuts-cast` branch adds capture of the actual installed
completion Rive file and build reports for investigating the doghouse. Other
branch experiments may be newer than this integration branch.

The published 1.3.5 was signed with the existing permanent certificate and
passed a fresh-install and 1.3.4-to-1.3.5 Android upgrade smoke test. The update
channel A points to it; channel B was not changed. Real Google sign-in, Drive,
physical S24 Ultra behavior and update installation through the app remain
unverified.
