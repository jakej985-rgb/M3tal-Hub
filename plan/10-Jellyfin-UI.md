# 10 Jellyfin UI

## Goal
Release the standalone React/Vite UI through M3tal-Hub at `/jellyfin-ui/`.

## Steps
1. Confirm the correct release branch.
2. Verify Vite production build.
3. Configure Vite base to the hub subdirectory.
4. Configure SPA fallback/deep-link handling for GitHub Pages.
5. Add dispatch workflow.
6. Add HUB_DISPATCH_TOKEN.
7. Test static asset paths.
8. Dispatch and validate.
9. Enable automatic releases.

## Definition of Done
The Vite application loads, routes, refreshes, and serves assets correctly under its hub path.
