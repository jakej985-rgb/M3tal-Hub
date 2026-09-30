# 13 Other Application Repositories

## Scope & Candidates
- GPS-speedometer (Android native)
- Ink-vault
- Shop-manager
- Tattoo-Shop-manager
- Infernal-Ink-Steel-Suite

## Steps & Execution
1. **Determine Architecture & Framework**:
   - Inspected repository structures, codebases, and build systems to establish whether each project is a static browser SPA, backend service, desktop application, or native mobile application.
2. **Identify Production Build Outputs**:
   - Identified whether artifacts are static web bundles (`index.html`, JS/WASM), native binaries (APK), or backend daemons/APIs.
3. **Decide GitHub Pages vs. Release/Repo Link**:
   - Static/browser SPAs belong under GitHub Pages subdirectories.
   - Native mobile, desktop, backend, and multi-service suites must NOT have Pages subdirectories configured, as they lack client-side browser deployment targets. They belong as repository or downloadable release links.
4. **Configure Subdirectory Routing Only for Static/Browser Applications**:
   - Confirmed only web-enabled applications receive `./<path>/` routes.
   - Non-web apps point directly to their GitHub repository or release URLs.
5. **Dispatch & Workflow Integration**:
   - Removed native/backend projects (`gps-speedometer`) from GitHub Pages build-and-deploy dispatch workflows (`.github/workflows/deploy.yml`).
6. **Keep Backend-Only Services Out of Pages Deployment**:
   - Prevented accidental dispatch or broken 404 directory generation for backend services.
7. **Enable Each Project Individually After Validation**:
   - Verified that all candidate entries in `apps/manifest.yml` and `index.html` link accurately to their repositories without dead links.

## Deployment Classifications & Audit Results

| Candidate | Framework / Architecture | Production Build Output | Web Frontend? | Pages Subdirectory? | Classification | Status & Hub Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **GPS-speedometer** | Android Native (Kotlin, Gradle DSL, `app/` module) | Android APK (`.apk`) | No | No (Excluded) | `android-native` | Excluded from Pages; repo link configured; `enabled: false`, `status: placeholder` |
| **Ink-vault** | Asset vault & indexing service for tattoo/studio assets | Backend service daemon / local asset store | No | No (Excluded) | `backend` | Excluded from Pages; repo link configured; `enabled: false`, `status: review` |
| **Shop-manager** | Studio operations, inventory & management system | Desktop executable / database application | No | No (Excluded) | `desktop` | Excluded from Pages; repo link configured; `enabled: false`, `status: review` |
| **Tattoo-Shop-manager** | Appointment scheduling & inventory tracking service | Backend server runtime / database API | No | No (Excluded) | `backend` | Excluded from Pages; repo link configured; `enabled: false`, `status: review` |
| **Infernal-Ink-Steel-Suite** | Multi-service studio management suite | Containerized multi-component suite | No (Web UI is isolated as `infernal-web`) | No (Excluded) | `suite` | Excluded from Pages; repo link configured; `enabled: false`, `status: review` |

## Registry & Landing Page Updates
- `apps/manifest.yml`:
  - `gps-speedometer`: Updated `type: android-native`, `enabled: false`, `status: placeholder`, removed `base_href`.
  - `ink-vault`: Updated `type: backend`, `enabled: false`, `status: review`.
  - `shop-manager`: Updated `type: desktop`, `enabled: false`, `status: review`.
  - `tattoo-shop-manager`: Updated `type: backend`, `enabled: false`, `status: review`.
  - `infernal-ink-steel-suite`: Updated `type: suite`, `enabled: false`, `status: review`.
- `.github/workflows/deploy.yml`:
  - Removed `gps-speedometer` from `workflow_dispatch` options to prevent failed Pages deployment attempts.
- `scripts/build_hub.py` & `index.html`:
  - Added explicit support for custom `url` property with fallback to `https://github.com/jakej985-rgb/{repo}` for non-Pages applications.
  - Generated updated `index.html` and `404.html` ensuring all non-web candidates link cleanly to their GitHub repos/releases without broken deployment paths.

## Definition of Done
Every candidate has an explicit deployment classification and is either integrated or intentionally excluded.
- **GPS-speedometer**: Explicitly classified as `android-native`; intentionally excluded from Pages deployment; linked to repo.
- **Ink-vault**: Explicitly classified as `backend`; intentionally excluded from Pages deployment; linked to repo.
- **Shop-manager**: Explicitly classified as `desktop`; intentionally excluded from Pages deployment; linked to repo.
- **Tattoo-Shop-manager**: Explicitly classified as `backend`; intentionally excluded from Pages deployment; linked to repo.
- **Infernal-Ink-Steel-Suite**: Explicitly classified as `suite`; intentionally excluded from Pages deployment; linked to repo.
