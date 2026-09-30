# 09 GPS Speedometer

## Goal
Release GPS Speedometer through M3tal-Hub at `/gps-speedometer/` or establish appropriate release and repository routing.

## Architectural Assessment & Framework Investigation
1. **Framework & Architecture**:
   - Repository inspected at `/home/m3tal/apps/GPS-speedometer`.
   - Identified as a native Android application using Kotlin, Jetpack Compose, and Gradle (`build.gradle.kts`, `app/` module).
   - Target SDK: 34, Min SDK: 29.
   - Build outputs: Android APKs (`.apk`) via `./gradlew :app:assembleRelease` and `.github/workflows/build-release-apk.yml`.
2. **Web / Browser Compatibility**:
   - Geolocation in this codebase is implemented using Android platform `com.google.android.gms:play-services-location`.
   - No Flutter or web frontend exists.
3. **Consolidation with Plan 13 (Other Application Repositories)**:
   - Per Plan 13 evaluation, native mobile applications are intentionally excluded from GitHub Pages deployment.
   - Removed `gps-speedometer` from GitHub Pages workflow dispatch (`.github/workflows/deploy.yml`) to prevent invalid deployment jobs.
   - Registered in `apps/manifest.yml` as `type: android-native`, `enabled: false`, `status: placeholder` with direct repository link (`https://github.com/jakej985-rgb/GPS-speedometer`) and release link (`https://github.com/jakej985-rgb/GPS-speedometer/releases`).
   - Tracked in `apps/status.json` with native APK versioning (`v1.0`).

## Definition of Done
Architectural framework identified; native Android deployment route established; broken GitHub Pages deployment paths eliminated; consolidated under [Plan 13: Other App Repositories](13-Other-App-Repositories.md).

