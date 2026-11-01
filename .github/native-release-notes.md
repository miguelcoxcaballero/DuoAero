DuoAero 1.3.0 runs the original Duolingo 6.103.5 application, path, lesson controller and native exercise screens with the Aerospace Technology course. Package: `com.duoaero`; versionCode: `10300`; permanent Inhouse signing certificate retained.

This is an **A-channel development release**, not a finished implementation of every requested feature. Earlier runs 41281331062 (standalone/resume) showed intermittent Android ANRs at the final summary. Both scenarios pass the subsequent run 41282225042 with unchanged runtime code; the earlier failures are not considered fixed or disproved. Google sign-in is required. There is no guest bypass in the production APK.

Course content: 1,200 English questions, 400 at each difficulty, 43 named topics and 79 lessons. The 106 exam items and 21 slide reflections are retained. New textbook practice includes single-slot and multiple-slot formula blocks and matching. Public textbook references contain only the authorized title and pages.

Measured Android evidence:

- Exact permanently signed production bytes: run 41282627153 passes fresh installation, update over 1.2.0, version confirmation and the original Google welcome before/after process restart. No crash or ANR occurred in this installation/welcome check.

- Original launcher, path and lesson screens; complete lesson, Claim XP, saved completion, process restart and next lesson: run 41282225042 (standalone and resumed lesson).
- Separate mistake review: run 41280541777 enters through the original profile/settings, answers the saved mistake, completes review and retains correction after process restart without falsely completing the course lesson.
- All 18 formula exercises receive actual native correct grades; a separate wrong selection receives incorrect feedback. All eight mixed exercise probes pass (multi-selection, matching, gaps and ordering).
- Night mode and 130% font scale have passed representative rich questions; audio/haptic service events were observed in the emulator. Physical sound and vibration quality remain untested.
- Original Google-only welcome, synthetic account routing, sign-out and encrypted authentication storage across restart pass. This is **not** real Google consent or a Drive network round trip.
- Original settings opens the canonical updater with default B, actual package version and the app's own frozen installer provider. Download/cancel/retry/install through that updater remains unverified.

Still incomplete or unverified: real Google/Drive and account switching; traversal of all 79 lessons; complete content/layout audit; in-app Snoopy animation replacement (only the launcher icon uses Snoopy); matching web UI; physical-device QA and full updater installation acceptance. The original birds still appear inside the app.

`build-info.json` binds the APK to its source commit and signing run. `SHA256SUMS.txt` identifies the exact signed download. The `build-1.3.0` unsigned release is signing input and cannot be installed.
