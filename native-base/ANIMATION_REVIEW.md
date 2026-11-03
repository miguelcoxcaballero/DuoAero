# Completion animation investigation

Forced-foam Android run 41347950406 shows the desired transparent Snoopy pose
and successful lesson completion. Its short 7-fps recording shows only small
scene movement; it does not establish that the pose sequence is playing.

When the patched foam artboard is isolated in the Rive runtime, explicitly
playing `FoamFingerDuo_Loop_animation` displays distinct poses. Starting its
state machine using `duo_start_trig` can display overlapping poses during a
transition. Do not claim smooth animation or enable that trigger globally
until the original transitions and rendering are fixed and verified on Android.
The forced-selection build is diagnostic, not the signed release.

An experimental patch changes the foam sprite rig's 800 ms intro-to-loop
cross-fade to a direct transition at its matching pose boundary. Isolated Rive
playback after manually firing the trigger no longer showed the same overlapping
poses in the sampled frames. This has not been verified through the completion
screen on Android, and the samples do not establish smoothness. The original
screen may choose a static state, which is a separate issue.

## Lottie scenes still using a single swaying bitmap

The generic replacement in `mascot_assets.lottie` replaces every matching
JSON scene except `duo_flying_up` with one image and vertical movement. That is
not an accepted character animation. Static inspection of the original APK
identified these named call sites; a resource reference alone does not prove
that a particular course/account can reach the screen:

- `duo_waving`: `MidLessonAnimationView` and the session showcase renderer.
- `duo_normal_mid_lesson`, `duo_in_lesson_reaching_crown`: session showcase selection.
- `duo_funboarding_wave`, `duo_funboarding_selection`,
  `duo_funboarding_pencil_raise`, `duo_funboarding_celebration`,
  `duo_funboarding_final`, `duo_funboarding_splash`: onboarding views.
- `path_duo_ball`, `path_duo_books`, `path_duo_butterfly`, `path_duo_cheer`,
  `path_duo_gem`, `path_duo_globe`, `path_duo_headphones`,
  `path_duo_jumpflap`, `path_duo_potion`, `path_duo_sunglasses`,
  `path_duo_twirl`, `path_duo_whistling`: original path-animation enum.
- `session_complete_bea_duo`, `session_complete_eddy_duo`,
  `session_complete_junior_duo`, `session_complete_lily_duo`,
  `session_complete_lin_duo`, `session_complete_lucy_duo`,
  `session_complete_oscar_duo`, `session_complete_vikram_duo`,
  `session_complete_zari_duo`: original lesson-completion animation enum.
  Several original scenes contain multiple characters and effects, so replacing
  the whole composition with one Snoopy also loses those roles and effects.
- `duo_books`, `duo_hop`, `duo_hover`, `duo_super_jumping`,
  `daily_refresh_duo_cheer`, `loading_state_duo_ball`,
  `milestone_calendar_icon_duo`, `resurrected_duo_animation`,
  `super_duo_bell`, `super_welcome_duo`, and the four `longscroll_*duo*`
  assets have original code references in their respective features.
- `duo_holding_det_certificate` and its dark variant are referenced by the
  original certificate-promotion fragment; accessibility in DuoAero is unknown.

Resources without an identified direct call must not be called unreachable:
resource lookup can be indirect. Real screen reachability, original callbacks
and motion remain to be tested. `research/lottie_wave.py` is an unintegrated
prototype for `duo_waving`, using the existing transparent wave atlas as
sixteen clipped Lottie compositions. Its host test checks that one pose is
active and original timing/markers survive. It does not prove that Android
clips the atlas correctly, that the real mid-lesson view plays or finishes, or
that the wave is smooth and free from halos.

Wave run 41568910162 rendered a replacement pose but failed its original
`onAnimationEnd` expectation. Static inspection shows the expectation was
wrong for this scene: the original hole entrance uses a 500 ms translation,
then its callback calls `LottieAnimationView.u()`, which resets progress to
zero past 98.5% and loops. The same entrance callback also starts the original
message-card animation; the looping wave does not signal scene completion by
`onAnimationEnd`. The probe now follows that entrance/start contract and
checks progress, rather than expecting a terminal callback. A control with the
unchanged original Lottie and the replacement on the same view is still
required; neither one has passed this revised probe yet.

The paired control in 41572357663 established why both earlier attempts were
static: the original performance manager reported LOWEST and motion disabled
in both the original and replacement view, while Android animator scale was
1.0 and both views were attached and shown. This does not establish an atlas
regression or smooth playback. The next paired diagnostic gives the emulator
4.5 GiB RAM so the original device classification can select its normal mode;
it does not override the app's performance manager or motion preference. The
real mid-lesson scene and its message-card callback remain to be verified.

In 41574272357 the 4.5 GiB emulator reported NORMAL, motion enabled, animator
scale 1.0, and attached/shown views for both original and replacement. Both
still failed the progress check; the low-memory setting alone is not the
explanation. The next comparison records the original drawable's composition,
frame, progress and animator-running state without starting or modifying it
outside the original entrance callback. Neither resource is accepted as smooth
or as a real-scene integration on this evidence.

Main-thread observer run 41577674317 found the composition already loaded at
both original entrance callbacks, with NORMAL performance mode and motion
enabled. The unchanged original remained at frame 0 and reported its animator
stopped throughout the sampled interval, so the paired job failed. The atlas
candidate did advance and loop (frames 81, 174, 260, 27 among the first
samples) with its animator running; inspected frames show different transparent
Snoopy poses. This isolated harness does not explain the stopped original,
prove smooth motion, or validate the real mid-lesson message-card scene. Its
standalone view also places the lower body at the bottom edge, so the screenshot
is not acceptance of final scene composition.
