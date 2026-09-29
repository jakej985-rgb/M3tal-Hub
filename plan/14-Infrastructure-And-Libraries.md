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

## Steps
1. Keep them out of the static Pages build by default.
2. Add release cards only when useful.
3. Link to documentation, releases, containers, packages, or source repositories as appropriate.
4. If a project later gains a static frontend, give that frontend its own registry entry.
5. Never expose backend secrets or private service endpoints through M3tal-Hub.

## Definition of Done
M3tal-Hub remains a release front rather than becoming an accidental deployment target for infrastructure.
