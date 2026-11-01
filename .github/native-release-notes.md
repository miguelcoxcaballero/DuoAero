DuoAero 1.3.3 uses the original Duolingo 6.103.5 runtime with the Aerospace Technology course. This is an A-channel development release; it is not a completed implementation of every requested feature.

The app adapts the original portrait window to taller screens, updates DuoAero branding and introduces Snoopy artwork. Formula slots now appear next to the formula, and incorrect feedback uses the native mathematical renderer. Local lesson completion updates gems and the streak; path chest rewards are included.

Android emulator run 41310946566 verified one full lesson, the visible 10-gem and one-day streak counters, restart and the next lesson at 1440 × 3120. It also verified 18 formula selections, an incorrect formula rendered in LaTeX, synthetic account isolation and the original Google welcome. These checks are not a physical Samsung test or real Google/Drive authentication. The chest-opening UI test remains under investigation; a 25-gem chest claim and restart have not been established by that run.

Still incomplete: emotion- and action-specific Snoopy animation replacements, full course and text-layout audit, real Google/Drive round trip, updater download/install verification, physical sound and vibration, and the matching web interface. Earlier intermittent lesson-end ANRs have not been fully diagnosed.

`build-info.json` identifies the source and signing run; `SHA256SUMS.txt` identifies the signed APK. The `build-1.3.3` unsigned artifact is signing input and cannot be installed.
