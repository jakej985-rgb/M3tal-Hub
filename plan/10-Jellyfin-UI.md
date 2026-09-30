# 10 Jellyfin UI

## Goal
Release the standalone React/Vite UI through M3tal-Hub at `/jellyfin-ui/`.

## Steps & Execution
1. [x] **Confirm correct release branch**:
   - Default/feature branch: `feat/netflix-jellyfin-ui-8605598523484562409`.
   - Configured in `apps/manifest.yml` with `ref`, `type: vite`, `path: jellyfin-ui`, and `enabled: true`.
2. [x] **Verify Vite production build**:
   - Implemented `scripts/build_web_release.sh` in `Jellyfin-ui` which handles `npm ci`, environment-based `BASE_HREF` build, and output staging to `dist/` and `build/web/`.
3. [x] **Configure Vite base to the hub subdirectory**:
   - Configured `base: process.env.BASE_HREF || './'` in `vite.config.ts`.
   - Set `base_href: /jellyfin-ui/` in `apps/manifest.yml`.
4. [x] **Configure SPA fallback/deep-link handling for GitHub Pages**:
   - GitHub Pages fallback handled via root `404.html` in M3tal-Hub.
   - Application is a standalone Netflix-style dashboard without nested browser routing, ensuring clean refresh and load states.
5. [x] **Add dispatch workflow**:
   - Configured `.github/workflows/dispatch-hub.yml` in `Jellyfin-ui` with repository dispatch targeting `jakej985-rgb/M3tal-Hub` (`event-type: app-release`).
6. [x] **Add HUB_DISPATCH_TOKEN**:
   - Integrated `secrets.HUB_DISPATCH_TOKEN` into `M3tal-Hub/.github/workflows/deploy.yml` for multi-repo checkout.
7. [x] **Test static asset paths**:
   - Verified asset paths in built bundle (`favicon.svg`, `icons.svg`, `assets/*.js`, `assets/*.css`).
8. [x] **Dispatch and validate**:
   - Release successfully triggered and built via CI (commit `eaf9675`).
   - Verified deployed files on `origin/gh-pages` and HTTP 200 live deployment at `https://jakej985-rgb.github.io/M3tal-Hub/jellyfin-ui/`.
9. [x] **Enable automatic releases**:
   - Automated push triggers on `main`, `master`, and `feat/**` paths in `dispatch-hub.yml`.

## Definition of Done
The Vite application loads, routes, refreshes, and serves assets correctly under its hub path. (Completed & Verified)

