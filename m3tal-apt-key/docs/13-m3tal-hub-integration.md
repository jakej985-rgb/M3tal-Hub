# M3tal Hub Integration Specification (Phase 13)

> **Phase**: Phase 13 — M3tal Hub Integration  
> **Hub URL**: `https://jakej985-rgb.github.io/M3tal-Hub/`  
> **APT Repository URL**: `https://jakej985-rgb.github.io/m3tal-apt-key/`  
> **Current package candidate**: `m3tal` **0.24.6**  
> **Status**: Completed & Validated
>
> **Note**: the `m3tal-apt-key/` directory inside this repository is a stale
> mirrored snapshot of the apt repository documentation kept for reference.
> The authoritative repository lives at
> [github.com/jakej985-rgb/m3tal-apt-key](https://github.com/jakej985-rgb/m3tal-apt-key).

---

## 1. Architectural Role & Boundary Separation

The M3tal software distribution architecture maintains a strict separation between **discovery/presentation** and **package delivery/storage**:

```
+-------------------------------------------------------------------+
|               M3tal Hub (GitHub Pages Web Front)                  |
|               https://jakej985-rgb.github.io/M3tal-Hub/           |
|                                                                   |
|  - Web Application Launcher (PWAs, Web Demos)                     |
|  - Ecosystem Catalog & Discovery (Cards, Categories, Search)      |
|  - Release Notes & Multi-Platform Documentation                   |
|  - Direct APT Copy-Paste Installation Guides                      |
+-------------------------------------------------------------------+
                                  |
            Links to Repository & Bootstrap Commands
                                  v
+-------------------------------------------------------------------+
|            M3tal APT Repository (Debian Package Storage)          |
|            https://jakej985-rgb.github.io/m3tal-apt-key/          |
|                                                                   |
|  - GPG Keyring & Trust Store (KEY.gpg / Release.gpg)              |
|  - Repository Metadata (dists/stable/Release, Packages.gz)        |
|  - Binary Package Pool (pool/main/*.deb)                          |
|  - Universal One-Line Bootstrap Installer (install.sh)            |
+-------------------------------------------------------------------+
```

### Decoupling Rules:
1. **Separation of Concerns**: M3tal Hub never stores binary `.deb` packages directly. All package discovery points to `m3tal-apt-key`.
2. **Independent Deployments**: Changes to M3tal Hub templates, stylesheets, or web applications deploy independently without triggering APT repository metadata re-indexing.
3. **No Dead Links**: Every Hub entry with a Linux Debian distribution target displays tested, verified copy-paste commands pointing to the permanent repository.

---

## 2. Integrated Hub Interfaces

### 2.1 M3tal APT Keyring Page (`apps/m3tal-apt-key.html`)
- **Location**: `/apps/m3tal-apt-key.html`
- **Role**: Primary trust and bootstrap onboarding page for any Debian or Ubuntu user.
- **Integrated Instructions**:
  - **Universal Bootstrap**:
    ```bash
    curl -fsSL https://jakej985-rgb.github.io/m3tal-apt-key/install.sh | sudo bash
    ```
  - **Manual Signed-By Configuration**:
    ```bash
    # 1. Create keyrings directory
    sudo install -m 0755 -d /etc/apt/keyrings

    # 2. Download and dearmor M3tal public key
    curl -fsSL https://jakej985-rgb.github.io/m3tal-apt-key/public.key | sudo gpg --dearmor -o /etc/apt/keyrings/m3tal-archive-keyring.gpg
    sudo chmod a+r /etc/apt/keyrings/m3tal-archive-keyring.gpg

    # 3. Add APT sources list entry
    echo "deb [signed-by=/etc/apt/keyrings/m3tal-archive-keyring.gpg] https://jakej985-rgb.github.io/m3tal-apt-key stable main" | sudo tee /etc/apt/sources.list.d/m3tal.list > /dev/null

    # 4. Synchronize package lists
    sudo apt update
    ```
  - **Cryptographic Trust Verification**:
    Documents public key fingerprint `5F84 FE50 A401 11C9 8141 0E11 775A D147 3BF2 5102` and verification commands via `gpg --show-keys` and `apt-cache policy`.

### 2.2 M3tal Core Page (`apps/m3tal-core.html`)
- **Location**: `/apps/m3tal-core.html`
- **Role**: Operational documentation and installation guide for the foundation `m3tal` Debian package.
- **Integrated Instructions**:
  - **Step 1**: Bootstrap repository using `install.sh`.
  - **Step 2**: APT package installation:
    ```bash
    sudo apt update && sudo apt install -y m3tal
    ```
  - **Step 3**: Service inspection (`systemctl status m3tal-api.service`). The runtime is the `m3tal-api.service` daemon — there is no `/usr/bin/m3tal` CLI orchestrator.
  - **Step 4**: Runtime endpoints — embedded Web GUI at `http://localhost:5050/gui/` and REST API at `http://localhost:5050/api/v2` (port configurable via `API_PORT` in `/etc/m3tal/.env`).
  - **Plugins**: Ecosystem plugins (`m3tal-plugin-compose`, `m3tal-plugin-docker-monitor`, `m3tal-plugin-mesh`, `m3tal-plugin-mesh-cluster`, `m3tal-plugin-mesh-node`) install via the same APT repository and are auto-discovered by M3tal Core.
- **Release Information**:
  - Displays version `v0.24.6 Debian Release` with package format `.deb`.

### 2.3 Hub Homepage Directory (`index.html`)
- **Location**: `/index.html`
- **Integration Features**:
  - **APT Repository Banner**: Prominently featured above the "Infrastructure & Backend Services" section grid:
    - Callout: "📦 Official M3tal Debian/APT Repository"
    - Direct command: `curl -fsSL https://jakej985-rgb.github.io/m3tal-apt-key/install.sh | sudo bash`
    - Action button linking directly to `./apps/m3tal-apt-key.html`.
  - **M3tal Core Card**: Links to `./apps/m3tal-core.html` with OS badge `🐧 Linux` and release documentation button.
  - **M3tal APT Keyring Card**: Links to `./apps/m3tal-apt-key.html` with OS badge `🐧 Linux` and direct repo access.

---

## 3. Automation Engine & Build Synchronization

The integration is fully automated and codified in `scripts/build_hub.py`:
- `get_install_guide(app)` dynamically generates standard APT instructions for `m3tal-core` and `m3tal-apt-key`.
- `render_card` and `generate_hub` inject the repository banner and format multi-platform cards.
- `scripts/test_hub_verification.py` runs 100% pass verification on all generated HTML files, links, badges, and catalog metadata.
