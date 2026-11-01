# DuoAero

Aerospace Technology, Midterm 1, using the **original Duolingo 6.103.5 Android runtime and screens**. The active implementation is `native-base/`. The earlier custom-controller implementation in `app/src/` is retained as history and is not the current Android builder.

[Download DuoAero 1.3.0](https://github.com/miguelcoxcaballero/DuoAero/releases/download/v1.3.0/DuoAero-1.3.0.apk) · [Release notes and limitations](https://github.com/miguelcoxcaballero/DuoAero/releases/tag/v1.3.0)

**Development release; not every requested feature is finished.** Runs 41281331062 showed intermittent ANRs at the final lesson summary. Both standalone/resume pass run 41282225042 with the same runtime; the earlier failures remain unresolved, so this is not a fully stable release. Google sign-in is required. The production APK uses `com.duoaero`, versionCode `10300` and the existing permanent Inhouse signing key. Do not install the diagnostic `com.duoaero.nativebase` APK as the final app.

## Course and original runtime

The bank contains 1,200 English questions (400 per difficulty), 106 retained exam exercises and 21 slide reflections, organized into 43 named topics and 79 lessons. Exercises include choice, multiple selection, matching, ordering, word gaps, and formulas with one or several missing components. The latest textbook practice cites only its authorized title and pages; the private PDF and Drive metadata are not distributed.

The Android builder preserves the original `DuoApp`, `LaunchActivity`, `SessionActivity`, path widgets, animations and exercise controllers. The local Aerospace service supplies original course/session models and saves progress per Google account. Native LaTeX uses the original math renderer with repaired missing glyphs. Source hashes and structural checks alone are not evidence that a lesson works.

## Verified behavior and limits

See [native-base/status.json](native-base/status.json) and [device evidence](native-base/REPRODUCING.md) for run IDs and precise scope. Actual tests cover complete native lessons, process restart/resume, original in-lesson retries, separate saved-mistake review, formula blocks, mixed exercise types and representative night-mode layouts. Run 41282627153 verifies the exact signed production APK: fresh install, upgrade from 1.2.0, version 1.3.0/10300 and Google welcome across process restarts. These checks do not authenticate a real account.

Not yet established: real Google consent and Drive synchronization/account switching, every course lesson and text size, physical sound/haptic quality, and canonical updater download/cancel/retry/installation. The launcher has Snoopy on an ordinary red doghouse without wings; **in-app original birds and animations have not yet been replaced**. The corresponding original-style web version is incomplete. Do not describe this release as fulfilling all requested acceptance criteria.

Google authentication reuses the 21 Notes OAuth functions tracked in `shared/auth/provenance.json`; Android stores allowed authentication values encrypted with Android Keystore. Unit tests and synthetic identities do not prove real sign-in. Existing device progress is isolated by account; interrupted sessions remain local.

The canonical updater is locked and its installer sources remain unchanged. B is the default client channel. Development releases go to A; selecting A requires the canonical warning, acknowledgement and slide confirmation. This release does not publish to B.

## Build and evidence

Start with [CONTINUE_DUOAERO.txt](CONTINUE_DUOAERO.txt) and [AGENTS.md](AGENTS.md). Use JDK 17, Android SDK platform 36/build-tools 35.0.0, apktool 2.12.1 and the verified [handoff APK/fixtures](https://github.com/miguelcoxcaballero/DuoAero/releases/tag/handoff-2026-10-31-native-runtime-1). See [reproduction instructions](native-base/REPRODUCING.md) for environment variables.

```sh
python tests/validate_bank.py
node --test tests/auth.test.cjs tests/native-auth-storage.test.cjs
python vendor/inhouse-services-updater/verify.py .
python native-base/build.py
python native-base/test_integrity.py
```

`native-candidate.yml` builds the non-debuggable production package and a source-bound receipt. The permanent signer runs only in the authorized GitHub signing repository; its key is never exported. `native-diagnostic.yml` runs actual interactions on a disposable Android emulator. `native-release-device.yml` checks exact signed production bytes separately. The old `scripts/build_original.py` builds the retired interface.

`web/` contains the previous standalone web version. Third-party assets retain their original ownership; this is not an official Duolingo product.
