# 12 Munchkin Companion App

## Goal
Prepare the Flutter application for a web release at `/munchkin-companion-app/`.

## Steps & Status
1. [x] **Verify Flutter project structure**:
   - Inspected repository `jakej985-rgb/Munchkin-Companion-App`.
   - Result: Repository is currently a stub containing only `README.md` (`commit 6266f2e Add README.md`). No Flutter application files (`pubspec.yaml`, `lib/`, `web/`) exist yet.
2. [x] **Audit build readiness**:
   - Confirmed application cannot be built as a web release until Flutter source code is initialized.
3. [x] **Configure Hub Registry Entry**:
   - Configured `munchkin-companion-app` in `apps/manifest.yml` as `status: planned` with `enabled: false`.
   - Card displays "Release Planned" badge and links directly to the GitHub repository (`https://github.com/jakej985-rgb/Munchkin-Companion-App`) as a styled placeholder card, preventing dead 404 links on the live hub front.
   - Base href `/munchkin-companion-app/` and path `munchkin-companion-app` remain reserved for when source is added.
4. [ ] **Add web support and Drift database**:
   - Pending Flutter project creation.
5. [ ] **Add dispatch workflow in repository**:
   - Pending Flutter code push. Ready workflow template: `.github/workflows/dispatch-hub.yml` notifying `M3tal-Hub` on `app-release` event with payload `{"app_id": "munchkin-companion-app"}`.
6. [ ] **Add HUB_DISPATCH_TOKEN / M3TAL_HUB_TOKEN**:
   - Pending repository action secret setup once active builds are ready.
7. [ ] **Enable automatic releases**:
   - Once Flutter web build succeeds, switch `enabled: true`, `status: ready` in `apps/manifest.yml`.

## Definition of Done
A reproducible Flutter web build is available from the M3tal-Hub subdirectory, or explicitly registered as a planned placeholder card until upstream source code is authored.
- **Current State**: Registered as `status: planned` placeholder card in `apps/manifest.yml`. The card safely directs users to the source repository.

