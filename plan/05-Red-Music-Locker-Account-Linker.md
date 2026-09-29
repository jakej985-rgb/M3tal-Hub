# 05 Red Music Locker Account Linker

## Goal
Prepare the extension repository for centralized release visibility without treating the browser extension as a normal Pages application.

## Steps
1. Identify Firefox and Chromium build outputs.
2. Add a release workflow to build extension packages.
3. Store release artifacts separately from Pages content.
4. Add a project card to M3tal-Hub.
5. Link to release artifacts/documentation rather than mounting the extension as a web app.
6. Enable registry entry only after packaging is reproducible.

## Definition of Done
M3tal-Hub acts as the release front while extension packages remain downloadable artifacts.
