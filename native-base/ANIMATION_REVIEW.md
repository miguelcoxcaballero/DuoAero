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
