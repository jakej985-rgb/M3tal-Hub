# M3tal-Hub

**Unified release front for the M3tal application ecosystem.**

M3tal-Hub is the central GitHub Pages site that collects deployable applications from independent repositories.

## Architecture

```
Application repository
        |
        | push to main
        v
repository_dispatch
        |
        v
M3tal-Hub
        |
        +-- build application
        +-- publish /application-path/
        +-- update hub
        |
        v
GitHub Pages
```

## Registry

The application registry is `apps/manifest.yml`. It defines each project's repository, release path, build type, enabled state, and integration status.

## Plans

All implementation plans are under `plan/`.

Start with:
1. `plan/00-M3tal-Hub-Foundation.md`
2. `plan/99-Rollout-Order.md`

Each release candidate has its own integration plan.

## Rule

M3tal-Hub is a **release front**, not a replacement for the individual repositories. Source code remains in its own repository. M3tal-Hub receives only the build output required for the public release.

Infrastructure, backend-only, library, and tooling repositories stay outside the Pages build unless they later provide a specific web release.
