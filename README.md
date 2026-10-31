# DuoAero

Offline native Android study app for **Aerospace Technology — Midterm 1**.

- 1,200 questions: 400 each at one, two and three stars.
- Historical exam attribution and original excerpts, slide reflections, and practice.
- Choice, multiple selection, ordering, matching and one-word completion.
- 42 named path points, 81 lessons of 10–20 questions; 1–3 lessons per point.
- Whole grey/green lesson arcs; a single lesson uses an unbroken ring.
- Automatic private-device storage using Android AtomicFile. Sessions resume after restart; unresolved mistakes remain in review until corrected.
- Offline sounds, haptics and reduced-motion support.

## Build

Install JDK 17+ and Android SDK (platform 36, build-tools 35+). Set `JAVA_HOME` and `ANDROID_HOME`, then run:

```
python scripts/build.py
```

Output: `dist/DuoAero-1.0.0-unsigned.apk`. Release signing takes place in the owner's YouTube Calma GitHub Actions runner with the existing secret; no signing key is in this repository.

With an Android emulator/device connected, `python scripts/test_android.py` builds a disposable debug version and runs instrumentation tests of all canonical answers, lesson assignment, restart persistence, retries and completion. It installs test APKs; use a test device.

## Sources and implementation

`app/assets/questions.json` contains question-level source URLs, original excerpts and answer-basis fields. Retained material includes 106 exam exercises and 21 slide reflections. Derived solutions are identified rather than claimed as official answer keys. The unrecoverable measured angle in 2022 Q13 is not fabricated; that exercise is adapted and its original excerpt retained.

The course engine and native screens are implemented for this app. Selected XML layout hierarchy, fonts, icons, sounds and transitions were adapted from the user-supplied Duolingo APK and previously retrieved Duolingo audio. `reference/` documents supplied layout resources and asset provenance. This is not the complete original Duolingo application or an official Duolingo product. Third-party assets retain their original ownership; no license to those assets is asserted here.

`web/` preserves the existing standalone web app and its question-bank build sources. Android progress is stored separately; uninstalling the app or clearing its storage can remove it. The app does not request Internet permission.
