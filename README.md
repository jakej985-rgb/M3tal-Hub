# M3tal-Hub

**Unified release front for the M3tal application ecosystem.**

M3tal-Hub is the central GitHub Pages site that collects and serves deployable applications from independent repositories under unified subdirectories.

Live site: <https://jakej985-rgb.github.io/M3tal-Hub/>

## Ecosystem Repositories

The M3tal ecosystem is split across focused repositories with strict boundaries:

| Repository | Role |
| :--- | :--- |
| **M3tal-Hub** (this repo) | Public discovery & release front — GitHub Pages app catalog, per-app release/changelog/install pages. It does **not** store or sign `.deb` binaries. |
| **[m3tal-apt-key](https://github.com/jakej985-rgb/m3tal-apt-key)** | Debian package authority — hosts the signed APT repository (`pool/`, `dists/`), GPG keyring, and `install.sh` bootstrap at <https://jakej985-rgb.github.io/m3tal-apt-key/>. All `.deb` binary distribution lives here. |
| **[M3tal-core](https://github.com/jakej985-rgb/m3tal-core)** | Runtime & plugin host — ships the `m3tal` `.deb` with `m3tal-api.service` (Web GUI at `/gui/`, REST API at `/api/v2`, port 5050). |
| **[m3tal-plugins](https://github.com/jakej985-rgb/m3tal-plugins)** | Plugin source — plugin packages (`m3tal-plugin-*`) are built here, published to the APT repo, and auto-discovered by M3tal Core after `apt install`. |
| **[m3tal-llm](https://github.com/jakej985-rgb/m3tal-llm)** | AI research — scalar autograd, tensor ops, NN training, and an experimental language model (Go). |
| **[m3tal-review](https://github.com/jakej985-rgb/m3tal-review)** | Review CLI — deterministic local code-review tool (slop detection, security heuristics) for the ecosystem. |

### Installing M3tal Core & Plugins on Debian/Ubuntu

```bash
# 1. Bootstrap the signed APT repository (one time)
curl -fsSL https://jakej985-rgb.github.io/m3tal-apt-key/install.sh | sudo bash

# 2. Install the core runtime
sudo apt update && sudo apt install -y m3tal

# 3. Install plugins — Core discovers them automatically
sudo apt install -y m3tal-plugin-compose m3tal-plugin-docker-monitor \
  m3tal-plugin-mesh m3tal-plugin-mesh-cluster m3tal-plugin-mesh-node
```

Canonical GPG fingerprint: `5F84 FE50 A401 11C9 8141 0E11 775A D147 3BF2 5102`
(current package candidate: `m3tal` **0.24.6**).

> **Note:** the `m3tal-apt-key/` directory inside this repository is a stale
> mirrored snapshot of the apt repository docs kept for reference. The
> authoritative apt repository and its documentation live in the
> [m3tal-apt-key](https://github.com/jakej985-rgb/m3tal-apt-key) repository.

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
