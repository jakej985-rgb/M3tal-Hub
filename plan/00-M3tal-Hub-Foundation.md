# 00 M3tal-Hub Foundation

## Goal
Turn M3tal-Hub into the unified release front for selected application repositories.

## Steps
1. Keep M3tal-Hub as the only GitHub Pages deployment target.
2. Maintain the application registry in `apps/manifest.yml`.
3. Build a reusable release workflow that reads the registry.
4. Accept `repository_dispatch` events from application repositories.
5. Build only the application that requested the release.
6. Publish each application under its registered subdirectory.
7. Generate the hub landing page from the registry.
8. Add build status and last-release information.
9. Keep disabled projects visible as placeholders but do not build them.
10. Add manual workflow dispatch for testing any registered application.

## Definition of Done
- M3tal-Hub builds successfully.
- GitHub Pages serves the hub.
- One application can dispatch a release.
- The application is available at its own subdirectory.
- A failed application build does not destroy the existing deployed site.
