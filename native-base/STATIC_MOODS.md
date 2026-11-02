# Static character pose experiment

This branch uses existing transparent Peanuts artwork for original static
drawable names that explicitly identify a matching pose: flying, thinking,
surprised, happy, cheering, affectionate, chef, meditation and heroic. Named
radio characters use the same Peanuts cast mapping as the in-lesson artwork. It
preserves the original drawable IDs and intrinsic dimensions. The host checks
verify the appended resource table and that the wrappers link, but do not
establish what every screen looks like on Android.

This is partial coverage: a name-based inventory currently identifies only
133 of 503 replaced mascot paths for a reviewed non-generic pose or character.
Explicit sad and crying names use a transparent sad Snoopy; ambiguous names
deliberately remain on the prior generic artwork rather than mapping them to
an unrelated emotion. Android animated-vector resources
are not demonstrated to animate merely because the replacement artwork is
transparent. A scene-by-scene artwork and animation review remains necessary.

The follow-up also targets 78 explicit single-character static vectors for the
ten existing Peanuts cast mappings. Correct and incorrect radio illustrations
use their respective happy and sad artwork. Host checks confirm the wrappers;
original-screen placement and these character states still need Android review.
Multi-character pictures and unclassified names remain outside this change.

The follow-up adds a transparent Snoopy reading an aerospace book for the
explicit original reading-story artwork. This is one static pose, not an
animation, and its placement in the original Android screens needs inspection.
An additional gem-holding Snoopy targets two explicit static gem poses; it too
requires original-screen inspection and is not evidence of chest animation.

The `duo_happy` original ImageView now has a static celebration fallback;
its experimental transparent 16-frame wave is not yet attached to that
screen. Direct XML references to custom application drawables crashed the
original quit sheet. A targeted hook instead installs the sad animation after
that original layout inflates; attached-screen playback and smoothness still
require Android evidence. Run 41380455084 opened the sheet, but its screen
recording showed a static image. The next probe checks the attached drawable
and actual changing pixels rather than considering an open sheet sufficient.
