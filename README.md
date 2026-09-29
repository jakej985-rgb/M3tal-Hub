# M3tal-Hub

**Unified release front for the M3tal application ecosystem.**

M3tal-Hub is the central GitHub Pages site that collects and serves deployable applications from independent repositories under unified subdirectories.

## Architecture

```
Application repository (e.g. Monster-Lab)
        |
        | push to main / tag
        v
repository_dispatch (app-release)
        |
        v
M3tal-Hub (.github/workflows/deploy.yml)
        |
        +-- fetch cached gh-pages subdirectories
        +-- build target application with base href /<path>/
        +-- publish to /<path>/ in _site/
        +-- update release status (apps/status.json)
        +-- generate dynamic landing page & 404 (scripts/build_hub.py)
        |
        v
GitHub Pages & gh-pages branch
```

## Registry

The application registry is [`apps/manifest.yml`](apps/manifest.yml). It defines each project's repository, release path, build type, enabled state, description, and base href.

Release metadata and timestamps are tracked in [`apps/status.json`](apps/status.json).

## Hub Generation

The landing page and 404 handler are dynamically generated from the registry:

```bash
python3 scripts/build_hub.py [output_directory]
```

- Live and ready applications are rendered as clickable cards pointing to `./<path>/`.
- Placeholder / review projects link to their repository.
- Generates `index.html` and `404.html` with SPA fallback.

## Dispatch Configuration for Application Repositories

To enable automated release triggers on push:
1. Create a GitHub Personal Access Token (PAT) with `repo` or `contents:write` scope.
2. In the application repository (e.g., `Monster-Lab`), go to **Settings > Secrets and variables > Actions**.
3. Add a repository secret named `M3TAL_HUB_TOKEN` with the PAT.
4. Add the dispatch workflow (see [Monster-Lab dispatch workflow](https://github.com/jakej985-rgb/Monster-Lab/blob/main/.github/workflows/dispatch-hub.yml)).

## Manual Release Dispatch

You can manually trigger or test any registered application release directly in M3tal-Hub:
1. Go to **Actions > M3tal-Hub Release & Deploy**.
2. Click **Run workflow**.
3. Select the `app_id` (e.g., `monster-lab`) and git ref (`main`).
4. Select `none` to simply regenerate and redeploy the hub front without rebuilding applications.

## Plans

All implementation plans are under `plan/`.
- `plan/00-M3tal-Hub-Foundation.md`: Hub release front architecture & workflows.
- `plan/01-Monster-Lab.md`: First proof Flutter Web release under `/Monster-Lab/`.
- `plan/99-Rollout-Order.md`: Rollout order for subsequent application repositories.
