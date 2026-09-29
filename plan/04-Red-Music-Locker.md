# 04 Red Music Locker

## Goal
Release the browser-facing Red Music Locker interface through M3tal-Hub.

## Steps
1. Identify the production web frontend and backend boundary.
2. Do not publish server-only components as static Pages content.
3. Build only the browser frontend if supported.
4. Configure its public base path.
5. Add the standard dispatch workflow.
6. Add HUB_DISPATCH_TOKEN.
7. Verify API endpoint configuration is environment-based.
8. Dispatch a test release.
9. Verify authentication and API calls from the subdirectory.
10. Enable automatic release only after the backend boundary is confirmed.

## Definition of Done
The public frontend is deployable independently without exposing private server configuration.
