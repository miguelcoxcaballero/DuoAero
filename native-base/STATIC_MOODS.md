# Static character pose experiment

This branch uses existing transparent Peanuts artwork for original static
drawable names that explicitly identify a matching pose: flying, thinking,
surprised, happy, cheering, affectionate, chef, meditation and heroic. Named
radio characters use the same Peanuts cast mapping as the in-lesson artwork. It
preserves the original drawable IDs and intrinsic dimensions. The host checks
verify the appended resource table and that the wrappers link, but do not
establish what every screen looks like on Android.

This is partial coverage: a name-based inventory currently identifies only
110 of 503 replaced mascot paths for a reviewed non-generic pose or character. Sad, crying,
and ambiguous names deliberately remain on the prior generic artwork rather
than mapping them to an unrelated emotion. Android animated-vector resources
are not demonstrated to animate merely because the replacement artwork is
transparent. A scene-by-scene artwork and animation review remains necessary.
