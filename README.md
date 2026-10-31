# DuoAero

## Agent continuation handoff

Read [CONTINUE_DUOAERO.txt](CONTINUE_DUOAERO.txt) before continuing. The current original-runtime investigation is on `codex/original-runtime-integration`, under `native-base/`, and is **not a working release**. [Handoff APKs and fixtures](https://github.com/miguelcoxcaballero/DuoAero/releases/tag/handoff-2026-10-31-native-runtime-1) are diagnostic artifacts. The Android 1.2.0 description below refers to the older implementation the user rejected as the final UI architecture.

Aerospace Technology, Midterm 1: 1,200 questions, 400 per difficulty, 81 lessons across 42 named topics. Includes exam provenance, slide reflections, five question types, end-of-lesson retries and persistent mistake review.

## Android 1.2.0

This build retains all eleven compiled DEX files, resources and libraries from the supplied Duolingo 6.103.5 APK. It adds the local course controller and adapts original sign-in, navigation, course header, exercise container, answer cards, loading, mistake review and completion layouts. These instantiate the original compiled Juicy UI classes. Original settings widgets and original haptic presets are used. The Compose statistic counter is replaced with a JuicyTextView to remove its dependency on Duolingo experiments services. The course path, exercise orchestration and Drive adapter are DuoAero code. It does not claim to reuse the complete original online course service or every original screen.

The visible mascot is Snoopy on an ordinary red doghouse, with no wings. Lesson rings turn green only after actual completion. One-lesson topics have an uninterrupted ring.

Google login copies the 21 Inhouse Notes OAuth functions unchanged; `shared/auth/provenance.json` records their origin and hashes. Android uses the registered `com.duoaero` client, PKCE, a persistent refresh token and account-separated local progress. Google Drive synchronization merges answer records and completed lessons; interrupted lessons remain local to each device. Authentication tokens are never uploaded with study progress. Android backups are disabled to exclude tokens.

The canonical Inhouse services updater is vendored at the locked revision without source edits. Its dependencies are relocated during compilation to avoid collisions with the original APK's obfuscated libraries. B is the default channel; new releases are published only in A. Choosing A requires its existing warning, acknowledgement and slide confirmation.

## Build and test

Use JDK 17+, Android SDK platform 36/build-tools 35.0.0 and Kotlin's compiler libraries. Set `JAVA_HOME`, `ANDROID_HOME` and optionally `KOTLIN_LIB`. `scripts/build_original.py` accepts `DUOAERO_DECODED` (apktool resource-only decode of the supplied APK) and `DUOAERO_RESOURCE_CACHE` (aapt2 compiled resource ZIP). The default paths match the owner's local reference workspace. Build dependencies in `.codex/duoaero-build-deps` are AndroidX core 1.13.1, ASM 9.7.1 and ASM Commons 9.7.1 from their official Maven repositories.

```
python scripts/build.py
node --test tests/auth.test.cjs
python scripts/test_android.py
```

The Android test command installs debug APKs on the connected disposable emulator. Do not run it against a personal phone with a release installation. Output: `dist/DuoAero-1.2.0-unsigned.apk`. Release signing uses the existing YouTube Calma GitHub secret, never a local copy of the key. A hash-bound build input and source inventory are verified before the signing step.

Automated OAuth tests simulate token responses; they do not prove a real Google account has completed consent. A real account sign-in and Drive round trip must be checked separately.

## Sources

The bank retains 106 exam exercises and 21 slide reflections with source excerpts and derived-answer labels. The unrecoverable measured angle in 2022 Q13 is not fabricated. Supplied third-party code and assets retain their original ownership. This is not an official Duolingo product.

`web/` still contains the earlier standalone web version. Its matching original UI port and shared Google progress integration are not yet complete.
