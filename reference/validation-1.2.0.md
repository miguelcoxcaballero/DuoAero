# Android 1.2.0 verification

- API 36 emulator: 2,724 assertions covering 1,200 questions, 81 lessons, grading, retry queues, unresolved mistake review, persistence and original layout inflation.
- All six packaged sound files decode through Android MediaPlayer. A tapped answer check produces a MediaPlayer started/stopped event with USAGE_GAME and CONTENT_TYPE_SONIFICATION, without DuoAeroAudio errors.
- Ten original haptic preset variants (five events at L1/L2) parse and create valid Android waveforms. Physical vibration strength was not assessed in the emulator.
- Original eleven DEX hashes remain unchanged; the course controller is added separately.
- Visual inspection using the Windows emulator: path, answer selection and feedback in light mode; settings, mistake review, question library and lesson completion in dark mode. Completion labels are visible, long answers wrap, and controls use original Juicy classes.
- Five mocked OAuth/Drive tests pass. Real Google account consent and a remote Drive round trip were not performed during this UI release.
- No claim of pixel-identical reproduction of every original online screen: course-specific organization, source attribution, multiple selection, matching and progress are integrated with the retained UI components.
