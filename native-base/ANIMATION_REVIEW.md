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

The real view's `oxm` branch is selected by the original
`LessonCoachViewModel.H0` for the Duo timed-session character theme. Its
callers include the original bonus-gem dialogue and character-sidequest
dialogue, whose respective original state converter supplies the theme. This
static route does not show that either dialogue is reachable in the local
math course. The unseeded course journey now passively observes the real
`MidLessonAnimationView`, saves frames if it becomes visible, and leaves its
original navigation and callbacks untouched. An observed different coach
scene or the absence of this view would not establish wave-scene acceptance.
The paired isolated probe additionally samples immediately after the original
entrance callback: its prior first sample occurred more than one original
5.149-second animation duration after that callback, so early playback is a
specific unresolved hypothesis rather than evidence that it never started.

Run 41580680880 sampled from immediately after entrance. Both compositions
were already loaded and both original and atlas started with their animators
running. The original advanced from frame 0 to 21, 46 and 229 before it was
observed stopped at frame 0; the atlas continued across multiple loops. This
resolves the earlier question of whether the unchanged resource started, but
does not establish a continuously smooth atlas or acceptance of the actual
message-card scene. The later stopped state and difference in looping remain
observable limitations of the isolated comparison.

A static size inventory of the ten completion artboards sums their 160 RGBA
frame dimensions to 59.94 MiB if each image is decoded once. Two artboards
use the same sixteen `overjoyed` files; sharing those bytes would make that
sum 53.94 MiB without dropping poses. These are theoretical uncompressed
sizes, not measured Rive allocations, and do not explain the emulator memory
growth on their own. The ongoing journey samples native/Dalvik PSS, native
heap, screenshots and flow-count over time; check those measurements and Rive
lifecycle evidence before selecting a memory correction.

Run 41591755993 compared the same ten-question synthetic session in separate
processes on one emulator. With intermediate evidence captures *and their
accessibility-tree dumps* suppressed, native allocated heap rose from roughly
81 MB to 715 MB by the eighth new prompt, while flow count stayed 195. With
full evidence it rose from roughly 92 MB to 840 MB by capture 30. The fixed
home-screen screenshot control had returned near baseline after each capture.
Thus intermediate evidence collection is not necessary for the growth; this
comparison does not isolate session rendering from the driver's repeated
accessibility reads/taps, or establish behavior on a physical phone. It also
precedes the lesson-completion Rive scene. Both ten-question controls graded
correctly; neither establishes a fix or a complete-lesson journey.

`research/audit_cast_frame_edges.py` examined 480 Peanuts character frames:
74 have alpha above 128 at an image edge (Charlie 1, Franklin 7, Linus 7,
Lucy 10, Patty 27, Pigpen 5, Sally 17). In particular, Lucy happy frames 08–13
have more than 50 such pixels along the lower edge. The supplied frame images
were visually inspected at 00 and 09; edge contact alone does not establish
how much artwork, if any, is cropped. These frames require source/playback
review before declaring uncropped animation; padding the PNG would not restore
missing artwork. This audit does not assess motion smoothness.

The Lucy happy source sheet was located in the original generated-image
workspace and compared with the shipped frames. Playback frames 08–11 use
source cells 12–15, and 12–13 reuse cells 14 and 12. These are all in the
sheet's bottom row, whose opaque shoe pixels reach the source canvas edge
(223 pixels above alpha 128 on the final row). The previous gutter extraction
therefore cannot recover the missing lower outlines. An image-generation edit
of the complete sheet was attempted, but its output still has opaque shoe
pixels at the lower boundary and cannot yet be accepted as an uncropped source.
Neither the edited candidate nor a padded copy has been integrated; full-frame
reconstruction, registration and timed playback review remain necessary.
