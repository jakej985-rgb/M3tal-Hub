# 08 Infernal Web

## Goal
Release Infernal Web through M3tal-Hub at `/infernal-web/`.

## Steps
1. Audit `build-vercel.sh`.
2. Separate Vercel-specific deployment from static build generation.
3. Make the build produce a deterministic directory.
4. Add subdirectory/base-path support.
5. Add dispatch workflow.
6. Add HUB_DISPATCH_TOKEN.
7. Test the generated site locally.
8. Dispatch and verify the Pages deployment.
9. Enable automatic releases.

## Definition of Done
Infernal Web can build without Vercel and can run correctly below a hub subdirectory.
