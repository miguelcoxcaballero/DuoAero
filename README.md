# DuoAero

DuoAero is an Aerospace Technology course built on the original Duolingo 6.103.5 Android runtime and screens. The active Android implementation is in `native-base/`; the earlier custom interface is retained as history.

[Download DuoAero 1.4.0 APK](https://github.com/miguelcoxcaballero/DuoAero/releases/download/v1.4.0/DuoAero-1.4.0.apk) · [Release notes and limitations](https://github.com/miguelcoxcaballero/DuoAero/releases/tag/v1.4.0)

**1.4.0 is an intermediate development preview, not the completed 2.0 release.** It includes word-first formula practice, named quantities, local course and progress changes, revised questions, seven introductory second-midterm lessons, and additional character artwork. New range, wind and taper teaching sequences remain unconnected research drafts. Some long questions are still clipped, and the requested cast and smooth character animations are not complete.

The production package is `com.duoaero`, version code `10400`, signed with the existing permanent Inhouse certificate. Google sign-in is required. The local Aerospace service retains the original lesson controllers and stores progress per account. The bank contains 1,200 English questions, including 106 retained exam exercises and 21 slide reflections. The latest textbook content cites only its authorized title and pages; the private PDF and Drive metadata are not distributed.

## Verification and limits

The production build checks the original APK, resource identities, source inventory, updater revision and signing certificate. Android diagnostics have exercised original formula controls, hints and retries, as well as a complete range lesson and its saved proof on a seeded synthetic account. The exact signed APK's installation and welcome screen are tested separately; these checks do not establish full course completion or a real-account migration.

Instrumented emulator journeys showed native-memory growth and process closures. The effect on a physical phone is unknown. Google consent and Drive synchronization with a real account, the physical S24 Ultra, all text sizes, sound and haptics, every lesson, and the in-app updater installation remain to be verified. Source hashes and passing model tests do not prove that the full app works.

The canonical updater remains locked and unchanged. Development releases are published to channel A; channel B is not updated by this release. See [development notes](native-base/DEVELOPMENT_2.md), [animation review](native-base/ANIMATION_REVIEW.md) and [status](native-base/status.json) for detailed evidence and unresolved work.

## Build

Start with [CONTINUE_DUOAERO.txt](CONTINUE_DUOAERO.txt) and [AGENTS.md](AGENTS.md). The original APK and fixtures are in the verified [handoff release](https://github.com/miguelcoxcaballero/DuoAero/releases/tag/handoff-2026-10-31-native-runtime-1). Use JDK 17, Android SDK platform 36/build-tools 35.0.0 and apktool 2.12.1.

```sh
python tests/validate_bank.py
node --test tests/auth.test.cjs tests/native-auth-storage.test.cjs
python vendor/inhouse-services-updater/verify.py .
python native-base/build.py
python native-base/test_integrity.py
```

Third-party assets retain their original ownership; this is not an official Duolingo product.
