# Original runtime investigation

This isolated test preserves the original DuoApp, LaunchActivity, activities, services and all eleven DEX files. It does not start the custom DuoAero MainActivity. Only the package, provider authorities, test label and explicit original SDK bounds are changed. The resources come from the decoded resource cache, while assets, libraries and DEX files come directly from the supplied APK.

Installed on the disposable emulator. Android reported a successful cold launch of the original LaunchActivity. No AndroidRuntime crash was present in the subsequent checked log. This is not proof that an aerospace lesson can run.

Remaining: adapt original user/course/path/session data models and their repositories, route account access to the authorized Inhouse flow, substitute the requested course, wire Drive and the updater without replacing original screens, and replace visible mascot assets. HomeFragment constructs its original controller with many injected repositories; the original Session and RemotePathUnitData models must be supplied rather than bypassed with custom views.

This test APK is not a release and must not be published as a completed DuoAero app. The 1.1.x controller is not the requested final architecture.
