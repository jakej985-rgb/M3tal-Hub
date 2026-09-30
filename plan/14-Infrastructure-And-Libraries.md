# 14 Infrastructure And Libraries

These repositories should not be blindly treated as Pages applications.

## Infrastructure / backend
- m3tal-core
- m3tal-api
- m3tal-godash
- m3tal-stack
- m3tal-apt-key
- m3tal-docs
- antigravity-remote-docker

## Tooling / source projects
- vscode
- ytmusicapi
- comicinfo-generator

## Libraries & Templates
- m3tal-ui-kit
- m3tal-hub-template

## Steps
1. [x] Keep them out of the static Pages build by default (`enabled: false` and workflow safeguards).
2. [x] Add release cards only when useful.
3. [x] Link to documentation, releases, containers, packages, or source repositories as appropriate.
4. [x] If a project later gains a static frontend, give that frontend its own registry entry.
5. [x] Never expose backend secrets or private service endpoints through M3tal-Hub.

## Implementation Details
- **Registry Classification**: Registered under `apps/manifest.yml` with `category: infrastructure`, `libraries`, or `tooling`, distinct `type`, explicit repository links, and `enabled: false`.
- **Workflow Protection**: Added explicit category and type safeguards to `.github/workflows/deploy.yml` blocking any accidental Pages deployment of infrastructure, services, or libraries.
- **Informational Release Cards**: Upgraded `scripts/build_hub.py` to render dedicated ecosystem sections with informative badges (`Active`, `Stable`, `Infra Review`), version info, package tags, and external link indicators.
- **Status Metadata**: Configured release status and package tracking in `apps/status.json`.

## Definition of Done
M3tal-Hub remains a release front rather than becoming an accidental deployment target for infrastructure. (Completed & Verified)
