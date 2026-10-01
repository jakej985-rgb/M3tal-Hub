#!/usr/bin/env python3
"""
M3tal-Hub Dynamic Landing Page & App Release Documentation Generator
Reads apps/manifest.yml and apps/status.json, generating:
- index.html (Central Hub Preview & Directory)
- 404.html (Not Found Error Page)
- apps/{app_id}.html (Dedicated Release, Version History/Changelog & Install Docs)
"""

import os
import sys
import json
import yaml
from datetime import datetime, timezone

CATEGORIES = [
    {
        "id": "apps",
        "title": "Applications & Frontends",
        "description": "Interactive web applications and client releases hosted on GitHub Pages.",
        "icon": "🚀",
    },
    {
        "id": "infrastructure",
        "title": "Infrastructure & Backend Services",
        "description": "Core infrastructure, backend services, container environments, and deployment stacks.",
        "icon": "⚙️",
    },
    {
        "id": "libraries",
        "title": "Libraries, SDKs & Templates",
        "description": "Shared component libraries, UI kits, API wrappers, and module scaffolding templates.",
        "icon": "📦",
    },
    {
        "id": "tooling",
        "title": "Tooling & Documentation",
        "description": "Developer tooling, package repositories, automation utilities, and architecture specs.",
        "icon": "🛠️",
    },
]

VALID_WEB_TYPES = {'flutter-web', 'vite', 'web', 'static'}

def load_manifest(manifest_path):
    with open(manifest_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_status(manifest_status_path, site_status_path=None):
    merged = {"releases": {}}
    if manifest_status_path and os.path.exists(manifest_status_path):
        try:
            with open(manifest_status_path, 'r', encoding='utf-8') as f:
                merged = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load manifest status ({manifest_status_path}): {e}", file=sys.stderr)

    if site_status_path and os.path.exists(site_status_path) and os.path.abspath(site_status_path) != os.path.abspath(manifest_status_path):
        try:
            with open(site_status_path, 'r', encoding='utf-8') as f:
                site_status = json.load(f)
            
            site_releases = site_status.get("releases", {})
            base_releases = merged.setdefault("releases", {})
            for app_id, s_rel in site_releases.items():
                if app_id not in base_releases:
                    base_releases[app_id] = s_rel
                else:
                    if s_rel.get("build_status") == "success":
                        base_releases[app_id]["build_status"] = "success"
                        if s_rel.get("status"):
                            base_releases[app_id]["status"] = s_rel.get("status")
                        if s_rel.get("last_released"):
                            base_releases[app_id]["last_released"] = s_rel.get("last_released")
                        if s_rel.get("version"):
                            base_releases[app_id]["version"] = s_rel.get("version")
                        if s_rel.get("ref"):
                            base_releases[app_id]["ref"] = s_rel.get("ref")
        except Exception as e:
            print(f"Warning: Failed to load site status cache ({site_status_path}): {e}", file=sys.stderr)

    return merged

def get_badge(app, release_info):
    status = app.get("status", "planned")
    enabled = app.get("enabled", False)
    category = app.get("category", "apps")
    
    if enabled and category == "apps" and release_info and release_info.get("build_status") == "success":
        return ("Live", "badge-live")
    
    if status == "ready":
        return ("Release Ready", "badge-ready")
    elif status == "active":
        return ("Active", "badge-active")
    elif status == "stable":
        return ("Stable", "badge-stable")
    elif status == "planned":
        return ("Release Planned", "badge-planned")
    elif status == "review":
        return ("In Review", "badge-review")
    elif status == "infrastructure-review":
        return ("Infra Review", "badge-review")
    elif status == "placeholder":
        return ("Placeholder", "badge-placeholder")
    elif not enabled and category == "apps":
        return ("Placeholder", "badge-placeholder")
    
    return (status.title(), "badge-active" if category != "apps" else "badge-planned")

PLATFORM_INFO = {
    "android": ("🤖", "Android", "os-android"),
    "roku": ("📺", "Roku", "os-roku"),
    "web": ("🌐", "Web", "os-web"),
    "docker": ("🐳", "Docker", "os-docker"),
    "server": ("🖥️", "Server", "os-server"),
    "linux": ("🐧", "Linux", "os-linux"),
    "windows": ("🪟", "Windows", "os-windows"),
    "macos": ("🍎", "macOS", "os-macos"),
    "desktop": ("🖥️", "Desktop", "os-desktop"),
    "chrome": ("🧩", "Chrome", "os-chrome"),
    "firefox": ("🦊", "Firefox", "os-firefox"),
    "extension": ("🧩", "Extension", "os-ext"),
    "python": ("🐍", "Python", "os-python"),
    "dart": ("🎯", "Dart", "os-dart"),
    "template": ("📦", "Template", "os-template"),
    "docs": ("📖", "Docs", "os-docs"),
    "cli": ("🛠️", "CLI", "os-tool"),
}

# Compatibility alias
PLATFORMS = PLATFORM_INFO

def get_platforms(app):
    """
    Returns a list of platform tuples: (icon, label, css_class) for the given application.
    Supports multi-platform specifications from manifest.yml.
    """
    if "platforms" in app and isinstance(app["platforms"], list) and len(app["platforms"]) > 0:
        res = []
        for p in app["platforms"]:
            pkey = str(p).lower().strip()
            if pkey in PLATFORM_INFO:
                res.append(PLATFORM_INFO[pkey])
            else:
                res.append(("⚡", str(p).title(), f"os-{pkey}"))
        return res

    explicit_os = str(app.get("os", "")).lower().strip()
    app_type = str(app.get("type", "web")).lower().strip()
    category = str(app.get("category", "apps")).lower().strip()
    package = str(app.get("package", "")).lower().strip()

    if explicit_os:
        if explicit_os in PLATFORM_INFO:
            return [PLATFORM_INFO[explicit_os]]
        return [("⚡", explicit_os.title(), f"os-{explicit_os}")]

    if app_type == "android-native":
        return [PLATFORM_INFO["android"]]
    elif app_type in VALID_WEB_TYPES:
        if app_type == "flutter-web":
            return [("🌐", "Web / PWA", "os-web")]
        return [PLATFORM_INFO["web"]]
    elif app_type == "extension":
        return [PLATFORM_INFO["extension"]]
    elif app_type in ["desktop", "suite"]:
        return [PLATFORM_INFO["desktop"]]
    elif package == "docker-compose" or app_type in ["container", "infrastructure"]:
        return [PLATFORM_INFO["docker"]]
    elif package == "gpg-keyring":
        return [("🐧", "Linux / APT", "os-linux")]
    elif app_type in ["service", "backend"]:
        return [PLATFORM_INFO["linux"], PLATFORM_INFO["server"]]
    elif category == "infrastructure":
        return [PLATFORM_INFO["linux"]]
    elif category == "libraries":
        if package == "pypi":
            return [PLATFORM_INFO["python"]]
        elif package == "dart-pkg":
            return [PLATFORM_INFO["dart"]]
        elif app_type == "template" or package == "template":
            return [PLATFORM_INFO["template"]]
        return [("📦", "Library", "os-lib")]
    elif category == "tooling":
        if app_type == "docs" or package == "docs":
            return [PLATFORM_INFO["docs"]]
        return [PLATFORM_INFO["cli"]]

    return [("⚡", "Universal", "os-cross")]

def get_os_info(app):
    platforms = get_platforms(app)
    if platforms:
        return platforms[0]
    return ("⚡", "Universal", "os-cross")

def get_changelog(app, release_info):
    if "changelog" in app and app["changelog"]:
        return app["changelog"]
    
    version = release_info.get("version") or app.get("version") or "1.0.0"
    date_val = release_info.get("last_released") or app.get("last_released") or "2026-09-30"
    date_str = str(date_val)[:10]
    
    app_type = app.get("type", "web")
    category = app.get("category", "apps")
    enabled = app.get("enabled", False)

    notes = [
        f"Initial release registered under M3tal Hub release registry.",
        f"Automated CI/CD integration and deployment verification safeguards enabled.",
    ]

    if app_type == "flutter-web":
        notes.append("Progressive Web App (PWA) manifest and responsive CanvasKit/HTML rendering.")
        notes.append("Optimized base-href asset routing for GitHub Pages hosting.")
        if app.get("apk_url") or (isinstance(app.get("platforms"), list) and "android" in app.get("platforms")):
            notes.append("Standalone native Android APK distribution available from GitHub Releases.")
    elif app_type == "vite":
        notes.append("React & Vite optimized modern bundle export.")
        notes.append("Automated Node.js deployment pipeline with environment asset base path injection.")
    elif app_type == "static":
        notes.append("Clean static distribution with sanitized relative links and asset paths.")
    elif app_type == "android-native":
        notes.append("Native Android release with Gradle build pipeline and standalone APK packaging.")
    elif category == "infrastructure":
        notes.append("Docker containerization and orchestration configuration verified.")
    elif category == "libraries":
        notes.append("Modular architecture and versioned package export.")
    else:
        notes.append("Ecosystem release tracking and documentation published.")

    return [
        {
            "version": version,
            "date": date_str,
            "tag": "Current Release",
            "notes": notes,
        }
    ]

def get_install_guide(app):
    if "install_guide" in app and app["install_guide"]:
        return app["install_guide"]
    
    app_id = app.get("id", "")
    app_type = app.get("type", "web")
    repo = app.get("repo", app.get("id", ""))
    path = app.get("path", app.get("id", ""))
    package = app.get("package", "")
    category = app.get("category", "apps")

    guide = {
        "summary": "",
        "prerequisites": [],
        "steps": []
    }

    if app_id == "idle-animals":
        return {
            "summary": "Idle Animals (Extinction Sanctuary) is available across both Android and modern Web browsers, offering instant Progressive Web App (PWA) gameplay with offline persistence alongside a standalone native Android APK release.",
            "prerequisites": [
                "🌐 Web / PWA: Modern browser (Google Chrome, Mozilla Firefox, Microsoft Edge, Safari)",
                "🤖 Android: Mobile device running Android 8.0 (API 26 / Oreo) or higher",
                "Android setting: 'Install unknown apps' enabled for your browser or file manager",
                "🛠️ Developer: Flutter SDK >= 3.22 and Dart SDK >= 3.4"
            ],
            "steps": [
                {
                    "title": "🌐 Web / PWA Browser Gameplay",
                    "content": "1. Play immediately in your browser via M3tal Hub (or visit /M3tal-Hub/Idle-animals/).\n2. No installer or download required for direct browser gameplay.\n3. To install locally as a standalone Progressive Web App (PWA), tap 'Install App' in your browser address bar or select 'Add to Home Screen' from the browser menu.\n4. Service workers automatically cache game assets for complete offline progression.",
                    "code": "# Live Web App URL:\nhttps://jakej985-rgb.github.io/M3tal-Hub/Idle-animals/"
                },
                {
                    "title": "🤖 Android APK Installation",
                    "content": "1. Download the release package extinction-sanctuary-v1.0.0+1.2.apk from GitHub Releases.\n2. On your Android device, navigate to Settings > Security / Apps > Special App Access and enable 'Install unknown apps' for your browser or file manager.\n3. Open the downloaded extinction-sanctuary-v1.0.0+1.2.apk file and tap 'Install'.\n4. Once installed, launch 'Extinction Sanctuary' from your app drawer and enjoy native gameplay.",
                    "code": "# Direct APK Download URL:\nhttps://github.com/jakej985-rgb/Idle-animals/releases/download/v1.0.0+1.2/extinction-sanctuary-v1.0.0+1.2.apk\n\n# Or sideload directly via ADB:\nadb install -r extinction-sanctuary-v1.0.0+1.2.apk"
                },
                {
                    "title": "🛠️ Local Development & Build",
                    "content": "Developers can clone the source code to build and test both the Web and Android APK targets locally.",
                    "code": "# Clone source repository\ngit clone https://github.com/jakej985-rgb/Idle-animals.git\ncd Idle-animals\nflutter pub get\n\n# Run locally in Chrome\nflutter run -d chrome\n\n# Run on Android device or emulator\nflutter run -d android\n\n# Build production releases\nflutter build web --release --base-href /M3tal-Hub/Idle-animals/\nflutter build apk --release"
                }
            ]
        }
    elif app_id == "android-card-games":
        return {
            "summary": "Android Card Games can be enjoyed across multiple platforms: on mobile via Android APK, on television screens via Roku TV sideloading, self-hosted via Docker container or standalone server binaries, or played directly in the browser via instant Web PWA.",
            "prerequisites": [
                "Android device running Android 8.0 (API 26) or higher for mobile play",
                "Roku Streaming Player or Roku TV with Developer Mode enabled",
                "Docker Engine >= 24.0 or Docker Compose v2 for containerized party server",
                "Linux, macOS, or Windows for standalone server binaries",
                "Modern web browser (Chrome, Firefox, Safari, Edge) for instant Web / PWA"
            ],
            "steps": [
                {
                    "title": "📱 Android APK Installation",
                    "content": "1. Download AndroidCardGames-v0.1.28.apk from the GitHub Releases page.\n2. On your Android device, enable 'Install unknown apps' in Settings > Apps & notifications > Special app access.\n3. Open the downloaded APK file and tap Install.\n4. Launch Android Card Games and enjoy local or room-connected card gameplay.",
                    "code": "# Or install via ADB to a connected device:\nadb install -r AndroidCardGames-v0.1.28.apk"
                },
                {
                    "title": "📺 Roku TV Developer Mode Sideloading",
                    "content": "1. Enable Developer Mode on your Roku device using the remote: press Home 3 times, Up 2 times, Right, Left, Right, Left, Right.\n2. Note the device IP address shown on screen and set your developer password.\n3. Open a browser on a device on the same local network and navigate to the Roku web portal (http://<roku-ip>).\n4. Log in with username 'rokudev' and your password.\n5. Upload cardgames-roku-v0.1.28.zip and click Install.\n6. The Android Card Games channel will immediately launch on your TV.",
                    "code": "curl -u rokudev:YOUR_PASSWORD -F \"mysubmit=Install\" -F \"archive=@cardgames-roku-v0.1.28.zip\" http://<roku-ip>/plugin_install"
                },
                {
                    "title": "🐳 Docker Self-Hosted TV Party Server",
                    "content": "Host a persistent multiplayer room server for living room TVs, mobile players, and web clients using Docker.",
                    "code": "docker run -d \\\n  --name android-card-games-server \\\n  --restart unless-stopped \\\n  -p 8080:8080 \\\n  -p 8081:8081 \\\n  ghcr.io/jakej985-rgb/android-card-games:v0.1.28"
                },
                {
                    "title": "💻 Standalone TV Server Binaries",
                    "content": "Standalone executable binaries are available for Linux, macOS, and Windows from GitHub Releases, requiring no Docker runtime.",
                    "code": "# Linux / macOS:\nchmod +x cardgames-server-linux\n./cardgames-server-linux --port 8080 --ws-port 8081\n\n# Windows (PowerShell / Command Prompt):\n.\\cardgames-server-windows.exe --port 8080 --ws-port 8081"
                },
                {
                    "title": "🌐 Instant Web / PWA",
                    "content": "Play immediately in your browser on desktop or mobile without downloading any installer. To install as an offline PWA app, select 'Install' or 'Add to Home Screen' in your browser.",
                    "code": "https://jakej985-rgb.github.io/M3tal-Hub/Android-card-games/"
                }
            ]
        }
    elif app_id == "monster-lab":
        return {
            "summary": "Monster Lab robotics learning platform supports multi-platform execution: Web PWA, Android APK/AAB, native desktop binaries (Linux deb/tarball and Windows exe/zip), and containerized backend via Docker Compose.",
            "prerequisites": [
                "Web: Modern web browser with WebGL and CanvasKit support",
                "Android: Android 8.0+ device",
                "Linux: Debian/Ubuntu x86_64 or compatible Linux distribution",
                "Windows: Windows 10/11 64-bit",
                "Docker: Docker Engine and Docker Compose v2.x"
            ],
            "steps": [
                {
                    "title": "Web Browser & PWA",
                    "content": "Access Monster Lab instantly in your web browser. Install as a PWA for offline robotics simulation."
                },
                {
                    "title": "Android Installation",
                    "content": "Download the latest `.apk` or `.aab` package from GitHub Releases and install on your Android device."
                },
                {
                    "title": "Desktop Installation (Linux & Windows)",
                    "content": "Download the Linux Debian package or portable tarball, or the Windows installer / portable zip from Releases:",
                    "code": "# Linux Debian / Ubuntu:\nsudo dpkg -i monster-lab_*.deb\n\n# Windows PowerShell:\nExpand-Archive monster-lab-win64.zip -DestinationPath C:\\MonsterLab"
                },
                {
                    "title": "Docker Compose Stack",
                    "code": f"git clone https://github.com/jakej985-rgb/{repo}.git\ncd {repo}\ndocker compose up -d"
                }
            ]
        }
    elif app_id == "red-music-locker":
        return {
            "summary": "Red Music Locker provides a responsive Web frontend for audio streaming on M3tal-Hub, paired with a Docker Compose synchronization backend container (ytsync.yml).",
            "prerequisites": [
                "Modern web browser for instant web player access",
                "Docker Engine >= 24.0 and Docker Compose v2.x",
                "Host music directory and .env configuration"
            ],
            "steps": [
                {
                    "title": "Web Application Access",
                    "content": "Open the live web interface on M3tal-Hub to browse playlists, stream audio, and manage library metadata."
                },
                {
                    "title": "Docker Backend Deployment (ytsync.yml & default.env.example)",
                    "code": f"# Download release assets:\ncurl -fsSLO https://github.com/jakej985-rgb/{repo}/releases/download/v0.0.1-beta/ytsync.yml\ncurl -fsSL https://github.com/jakej985-rgb/{repo}/releases/download/v0.0.1-beta/default.env.example -o .env || \\\ncurl -fsSL https://raw.githubusercontent.com/jakej985-rgb/{repo}/main/.env.example -o .env\n# Configure storage paths in .env\ndocker compose -f ytsync.yml up -d\ndocker compose -f ytsync.yml logs -f ytm-sync"
                }
            ]
        }
    elif app_id == "red-music-locker-account-linker":
        return {
            "summary": "Red Music Locker Account Linker browser extension is available for Google Chrome and Mozilla Firefox.",
            "prerequisites": [
                "Google Chrome >= 110 (Chromium browsers) or Mozilla Firefox >= 115",
                "Active YouTube Music session on music.youtube.com"
            ],
            "steps": [
                {
                    "title": "Google Chrome / Chromium Installation",
                    "content": "1. Download `red-music-locker-account-linker-chrome-v1.1.0.zip` from Releases and extract it.\n2. Navigate to chrome://extensions in Chrome.\n3. Enable 'Developer mode' in the top right.\n4. Click 'Load unpacked' and select the unzipped directory containing manifest.json.",
                    "code": f"wget https://github.com/jakej985-rgb/{repo}/releases/download/v1.1.0/red-music-locker-account-linker-chrome-v1.1.0.zip\nunzip red-music-locker-account-linker-chrome-v1.1.0.zip -d chrome-linker/"
                },
                {
                    "title": "Mozilla Firefox Installation",
                    "content": "1. Download `red-music-locker-account-linker-firefox-v1.1.0.zip` from Releases.\n2. Navigate to about:debugging#/runtime/this-firefox in Firefox.\n3. Click 'Load Temporary Add-on' and select the ZIP package or manifest.json.",
                    "code": f"wget https://github.com/jakej985-rgb/{repo}/releases/download/v1.1.0/red-music-locker-account-linker-firefox-v1.1.0.zip"
                }
            ]
        }
    elif app_id in ["subaru-specs-n-parts", "specs-n-parts"]:
        return {
            "summary": "Subaru Specs & Parts is an offline-first automotive reference application available as a Web PWA and as an Android APK package.",
            "prerequisites": [
                "Web: Any modern mobile or desktop browser",
                "Android: Android 7.0+ device"
            ],
            "steps": [
                {
                    "title": "Instant Web & Offline PWA",
                    "content": "Open the application in your browser and choose 'Install' or 'Add to Home Screen' to cache the full automotive catalog for offline roadside reference."
                },
                {
                    "title": "Android APK Installation",
                    "content": "1. Download the Android APK package zip from Releases.\n2. Extract and open the `.apk` on your Android device to install."
                }
            ]
        }
    elif app_id == "gps-speedometer":
        return {
            "summary": "GPS Speedometer is a native Android application built for mobile devices with high-frequency GPS sensor integration, velocity smoothing, and dark OLED HUD windshield projection.",
            "prerequisites": [
                "Android mobile device running Android 8.0 (Oreo / API 26) or higher",
                "Hardware GPS / Location sensor capability",
                "For developers: Android Studio / Java 17 (JDK) / Gradle toolchain"
            ],
            "steps": [
                {
                    "title": "📱 Installation via Pre-built APK",
                    "content": "1. Download the latest `.apk` package from GitHub Releases.\n2. In Android Settings, enable 'Install unknown apps' for your browser or file manager.\n3. Open the downloaded APK file and tap 'Install'.\n4. Launch GPS Speedometer and grant Location permissions when prompted.",
                    "code": "# Or sideload via ADB to connected device:\nadb install -r *.apk"
                },
                {
                    "title": "🛠️ Compiling from Source",
                    "content": "To build the release APK directly from the source repository using Gradle:",
                    "code": f"git clone https://github.com/jakej985-rgb/{repo}.git\ncd {repo}\n./gradlew assembleRelease"
                }
            ]
        }
    elif app_id == "comicinfo-generator":
        return {
            "summary": "ComicInfo Generator provides both a command-line tool (CLI) and an automated Docker container release for batch ComicInfo.xml generation.",
            "prerequisites": [
                "Docker Engine >= 24.0 or Python 3.10+ with pip"
            ],
            "steps": [
                {
                    "title": "Running with Docker",
                    "code": f"docker run --rm -v /path/to/comics:/comics jakej985/comicinfo-generator:latest /comics"
                },
                {
                    "title": "Running with Python CLI",
                    "code": f"git clone https://github.com/jakej985-rgb/{repo}.git\ncd {repo}\npip install -e .\ncomicinfo --help"
                }
            ]
        }
    elif app_id in ["shop-manager", "infernal-ink-steel-suite"]:
        return {
            "summary": f"{app.get('name', 'Application')} is a Qt C++ desktop application built for Linux and Windows desktop environments.",
            "prerequisites": [
                "Linux (Ubuntu/Debian, Fedora, Arch) or Windows 10/11",
                "Qt 6.x runtime libraries"
            ],
            "steps": [
                {
                    "title": "Installation from Releases",
                    "content": "Download the pre-compiled binary package or installer from the GitHub Releases page for your operating system."
                },
                {
                    "title": "Building from Source",
                    "code": f"git clone https://github.com/jakej985-rgb/{repo}.git\ncd {repo}\ncmake -B build\ncmake --build build"
                }
            ]
        }
    elif app_type == "flutter-web":
        guide["summary"] = "This application can be accessed instantly in any modern web browser or installed locally as a Progressive Web App (PWA)."
        guide["prerequisites"] = [
            "Modern web browser (Google Chrome, Mozilla Firefox, Microsoft Edge, Safari)",
            "For local builds: Flutter SDK >= 3.22 (stable channel)",
            "Dart SDK >= 3.4"
        ]
        guide["steps"] = [
            {
                "title": "Instant Web & PWA Installation",
                "content": "No installation required for direct use. Open the live web application and choose 'Install' or 'Add to Home Screen' from your browser menu to run offline."
            },
            {
                "title": "Local Development Setup",
                "code": f"git clone https://github.com/jakej985-rgb/{repo}.git\ncd {repo}\nflutter pub get\nflutter run -d chrome"
            },
            {
                "title": "Building Production Web Release",
                "code": f"flutter build web --release --base-href /M3tal-Hub/{path}/"
            }
        ]
    elif app_type == "vite":
        guide["summary"] = "Modern React/Vite web application with component-based architecture and dynamic client rendering."
        guide["prerequisites"] = [
            "Modern web browser",
            "Node.js >= 20.x LTS",
            "npm >= 10.x"
        ]
        guide["steps"] = [
            {
                "title": "Instant Browser Access",
                "content": "Access the application instantly through GitHub Pages without local setup."
            },
            {
                "title": "Local Development Setup",
                "code": f"git clone https://github.com/jakej985-rgb/{repo}.git\ncd {repo}\nnpm install\nnpm run dev"
            },
            {
                "title": "Building Production Release",
                "code": f"BASE_HREF=/M3tal-Hub/{path}/ npm run build"
            }
        ]
    elif app_type == "static":
        guide["summary"] = "Lightweight static web application with zero external runtime dependencies."
        guide["prerequisites"] = [
            "Modern web browser",
            "Python 3.x (optional, for local preview server)"
        ]
        guide["steps"] = [
            {
                "title": "Local Testing & Preview",
                "code": f"git clone https://github.com/jakej985-rgb/{repo}.git\ncd {repo}\npython3 -m http.server 8080"
            }
        ]
    elif app_type == "android-native":
        guide["summary"] = "Native Android application built for mobile devices with Gradle build toolchain."
        guide["prerequisites"] = [
            "Android device running Android 8.0 (Oreo / API 26) or higher",
            "For developers: Android Studio / Java 17 / Gradle"
        ]
        guide["steps"] = [
            {
                "title": "Installation via Pre-built APK",
                "content": "1. Download the latest `.apk` package from the Releases section.\n2. On your Android device, enable 'Install unknown apps' in Settings for your browser or file manager.\n3. Open the downloaded APK and tap 'Install'."
            },
            {
                "title": "Compiling from Source",
                "code": f"git clone https://github.com/jakej985-rgb/{repo}.git\ncd {repo}\n./gradlew assembleRelease"
            }
        ]
    elif category == "infrastructure" or app_type in ["service", "backend", "container", "infrastructure"]:
        if package == "docker-compose" or app_type in ["container", "infrastructure"]:
            guide["summary"] = "Containerized infrastructure service orchestratable via Docker Compose."
            guide["prerequisites"] = [
                "Docker Engine >= 24.0",
                "Docker Compose v2.x",
                "Linux / macOS / WSL2 environment"
            ]
            guide["steps"] = [
                {
                    "title": "Launching Stack with Docker Compose",
                    "code": f"git clone https://github.com/jakej985-rgb/{repo}.git\ncd {repo}\ndocker compose up -d"
                },
                {
                    "title": "Inspecting Container Status",
                    "code": "docker compose ps\ndocker compose logs -f"
                }
            ]
        elif package == "gpg-keyring":
            guide["summary"] = "APT archive signing key and Debian repository configuration."
            guide["prerequisites"] = ["Debian or Ubuntu Linux system with sudo privileges", "curl and gpg"]
            guide["steps"] = [
                {
                    "title": "Importing Archive Keyring",
                    "code": f"curl -fsSL https://raw.githubusercontent.com/jakej985-rgb/{repo}/main/m3tal-archive-keyring.gpg | sudo tee /etc/apt/trusted.gpg.d/m3tal.gpg > /dev/null"
                }
            ]
        else:
            guide["summary"] = "Backend service and system infrastructure component."
            guide["prerequisites"] = ["Git", "Go >= 1.22 or Python 3.11 depending on module"]
            guide["steps"] = [
                {
                    "title": "Clone and Run Locally",
                    "code": f"git clone https://github.com/jakej985-rgb/{repo}.git\ncd {repo}\n# Follow service-specific configuration in README.md"
                }
            ]
    elif category == "libraries":
        if package == "dart-pkg":
            guide["summary"] = "Dart and Flutter shared component library."
            guide["prerequisites"] = ["Flutter SDK >= 3.22", "Dart SDK >= 3.4"]
            guide["steps"] = [
                {
                    "title": "Add Dependency to pubspec.yaml",
                    "code": f"dependencies:\n  {app.get('id')}:\n    git:\n      url: https://github.com/jakej985-rgb/{repo}.git\n      ref: main"
                }
            ]
        elif package == "pypi":
            guide["summary"] = "Python API client and metadata library."
            guide["prerequisites"] = ["Python >= 3.9", "pip package manager"]
            guide["steps"] = [
                {
                    "title": "Install via Pip",
                    "code": f"pip install git+https://github.com/jakej985-rgb/{repo}.git"
                }
            ]
        else:
            guide["summary"] = "Starter template and scaffolding for M3tal ecosystem web modules."
            guide["prerequisites"] = ["GitHub CLI (gh) or Git"]
            guide["steps"] = [
                {
                    "title": "Use Template Repository",
                    "code": f"gh repo create my-m3tal-app --template jakej985-rgb/{repo}"
                }
            ]
    else:
        guide["summary"] = "Developer tooling and workspace configuration utility."
        guide["prerequisites"] = ["Git", "Standard Linux / UNIX shell"]
        guide["steps"] = [
            {
                "title": "Repository Clone & Configuration",
                "code": f"git clone https://github.com/jakej985-rgb/{repo}.git\ncd {repo}\n# Review configuration files and documentation"
            }
        ]

    return guide

def render_card(app, release_info):
    app_id = app.get("id")
    name = app.get("name")
    desc = app.get("description", "")
    repo = app.get("repo", "")
    path = app.get("path", "")
    enabled = app.get("enabled", False)
    category = app.get("category", "apps")
    
    badge_text, badge_class = get_badge(app, release_info)
    platforms = get_platforms(app)
    platform_badges_html = " ".join([
        f'<span class="badge badge-os {css}">{icon} {lbl}</span>'
        for icon, lbl, css in platforms
    ])
    primary_icon = platforms[0][0] if platforms else "⚡"

    meta_info = []
    if app.get("type"):
        meta_info.append(f'<span class="app-type">{primary_icon} {app["type"]}</span>')
    
    version = release_info.get("version") or app.get("version")
    if version:
        meta_info.append(f'<span class="app-version">v{version}</span>')
    
    last_released = release_info.get("last_released") or app.get("last_released")
    if last_released:
        meta_info.append(f'<span class="app-date">{str(last_released)[:10]}</span>')
    
    pkg_status = release_info.get("package_status") or app.get("package")
    if pkg_status:
        meta_info.append(f'<span class="app-pkg">{pkg_status}</span>')
    
    meta_html = f'<div class="meta-row">{" ".join(meta_info)}</div>' if meta_info else ""

    is_web_deployable = app.get("type") in VALID_WEB_TYPES

    if category == "apps" and app.get("status") in ["placeholder", "review", None] and not enabled:
        card_class = "card placeholder"
    elif category != "apps":
        card_class = "card info-card"
    else:
        card_class = "card"

    # Detail page destination
    detail_href = f"./apps/{app_id}.html"

    # Actions footer buttons
    actions = []
    actions.append(f'<a class="card-btn" href="{detail_href}">Release & Docs →</a>')

    if enabled and is_web_deployable:
        actions.append(f'<a class="card-btn card-btn-primary" href="./{path}/">Launch ↗</a>')
    
    repo_url = app.get("repo_url") or (f"https://github.com/jakej985-rgb/{repo}" if repo else "")
    if repo_url and not (enabled and is_web_deployable):
        actions.append(f'<a class="card-btn" href="{repo_url}" target="_blank" rel="noopener noreferrer">Repo ↗</a>')

    actions_html = f'<div class="card-actions">{" ".join(actions)}</div>'

    return f"""        <div class="{card_class}">
            <a class="card-main-link" href="{detail_href}">
                <div class="card-header">
                    <h2>{name}</h2>
                    <div class="badge-group">
                        {platform_badges_html}
                        <span class="badge {badge_class}">{badge_text}</span>
                    </div>
                </div>
                <p>{desc}</p>
                {meta_html}
            </a>
            {actions_html}
        </div>"""

def generate_app_page(app, release_info, category_map):
    app_id = app.get("id")
    name = app.get("name")
    desc = app.get("description", "")
    repo = app.get("repo", "")
    path = app.get("path", app_id)
    enabled = app.get("enabled", False)
    category = app.get("category", "apps")
    app_type = app.get("type", "web")
    
    badge_text, badge_class = get_badge(app, release_info)
    platforms = get_platforms(app)
    platform_badges_html = " ".join([
        f'<span class="badge badge-os {css}">{icon} {lbl}</span>'
        for icon, lbl, css in platforms
    ])
    platform_pills_html = " ".join([
        f'<span class="pill pill-accent">{icon} {lbl}</span>'
        for icon, lbl, css in platforms
    ])
    platforms_spec_str = ", ".join([f"{icon} {lbl}" for icon, lbl, css in platforms])

    version = release_info.get("version") or app.get("version") or "1.0.0"
    last_released = release_info.get("last_released") or app.get("last_released") or "2026-09-30"
    repo_url = app.get("repo_url") or (f"https://github.com/jakej985-rgb/{repo}" if repo else "")
    release_url = app.get("release_url") or (f"{repo_url}/releases" if repo_url else "")
    docs_url = app.get("docs_url")

    is_web_deployable = app_type in VALID_WEB_TYPES

    # Find category metadata
    cat_meta = next((c for c in CATEGORIES if c["id"] == category), CATEGORIES[0])

    # Hero Action Buttons
    action_buttons = []
    if enabled and is_web_deployable:
        action_buttons.append(f'<a href="../{path}/" class="btn btn-primary">🚀 Launch Web Application</a>')
    
    if app.get("apk_url"):
        action_buttons.append(f'<a href="{app["apk_url"]}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary">🤖 Download Android APK ↗</a>')
    elif app_type == "android-native" and release_url:
        action_buttons.append(f'<a href="{release_url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary">📦 Download Release / APK ↗</a>')

    if repo_url:
        action_buttons.append(f'<a href="{repo_url}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary">🐙 GitHub Repository ↗</a>')
    if docs_url:
        action_buttons.append(f'<a href="{docs_url}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary">📖 Documentation ↗</a>')
    
    action_buttons.append('<a href="../" class="btn btn-secondary">← Back to Hub</a>')
    action_buttons_html = "\n                ".join(action_buttons)

    # Changelog render
    changelog_entries = get_changelog(app, release_info)
    changelog_html_parts = []
    for entry in changelog_entries:
        ver = entry.get("version", version)
        dt = entry.get("date", str(last_released)[:10])
        tag = entry.get("tag", "Release")
        items = entry.get("notes", [])
        items_html = "".join([f"<li>{item}</li>" for item in items])
        
        changelog_html_parts.append(f"""
            <div class="changelog-entry">
                <div class="changelog-header">
                    <span class="changelog-version">v{ver}</span>
                    <span class="changelog-tag">{tag}</span>
                    <span class="changelog-date">{dt}</span>
                </div>
                <ul class="changelog-list">
                    {items_html}
                </ul>
            </div>
        """)
    changelog_html = "\n".join(changelog_html_parts)

    # Install Docs render
    guide = get_install_guide(app)
    summary_html = f'<p class="guide-summary">{guide["summary"]}</p>' if guide.get("summary") else ""
    
    prereqs_html = ""
    if guide.get("prerequisites"):
        prereq_items = "".join([f"<li>{p}</li>" for p in guide["prerequisites"]])
        prereqs_html = f"""
        <div class="guide-prereqs">
            <h3>System Prerequisites</h3>
            <ul>{prereq_items}</ul>
        </div>
        """

    steps_html_parts = []
    for idx, step in enumerate(guide.get("steps", []), 1):
        step_title = step.get("title", f"Step {idx}")
        step_content = f'<p>{step["content"]}</p>' if "content" in step else ""
        step_code = f'<pre><code>{step["code"]}</code></pre>' if "code" in step else ""
        steps_html_parts.append(f"""
            <div class="guide-step">
                <h4>{step_title}</h4>
                {step_content}
                {step_code}
            </div>
        """)
    steps_html = "\n".join(steps_html_parts)

    base_href_val = app.get("base_href", f"/{path}/" if is_web_deployable else "N/A")
    package_val = release_info.get("package_status") or app.get("package") or ("pwa" if is_web_deployable else "source")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} | Release & Documentation | M3tal Hub</title>
    <meta name="description" content="Release notes, version history, and installation documentation for {name} on M3tal Hub.">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚙️</text></svg>">
    <style>
        :root {{
            --bg: #0d1117;
            --surface: #161b22;
            --surface-hover: #21262d;
            --surface-alt: #10141a;
            --border: #30363d;
            --border-hover: #58a6ff;
            --text-main: #e6edf3;
            --text-sub: #8b949e;
            --accent: #58a6ff;
            --accent-glow: rgba(88, 166, 255, 0.15);
            --ready: #3fb950;
            --live: #2ea043;
            --active: #58a6ff;
            --stable: #3fb950;
            --review: #d29922;
            --placeholder: #6e7681;
            --service: #bc8cff;
            --tooling: #f0883e;
            --code-bg: #07090e;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
            max-width: 1120px;
            margin: 0 auto;
            padding: 32px 24px;
            line-height: 1.5;
            background: var(--bg);
            color: var(--text-main);
        }}
        .nav-bar {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 28px;
            font-size: 13.5px;
            color: var(--text-sub);
        }}
        .nav-bar a {{
            color: var(--accent);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .nav-bar a:hover {{
            text-decoration: underline;
        }}
        .hero-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 32px;
            margin-bottom: 32px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
            position: relative;
            overflow: hidden;
        }}
        .hero-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 12px;
        }}
        .hero-title-group {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .hero-icon {{
            font-size: 32px;
            background: var(--accent-glow);
            border: 1px solid var(--border);
            width: 52px;
            height: 52px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
        }}
        .hero-title {{
            font-size: 28px;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.5px;
        }}
        .hero-desc {{
            color: var(--text-sub);
            font-size: 16px;
            margin: 0 0 20px 0;
            max-width: 840px;
            line-height: 1.6;
        }}
        .meta-pills {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 24px;
            font-size: 12px;
        }}
        .pill {{
            padding: 4px 10px;
            border-radius: 6px;
            border: 1px solid var(--border);
            background: rgba(255, 255, 255, 0.03);
            color: var(--text-sub);
            font-family: monospace;
        }}
        .pill-accent {{
            background: var(--accent-glow);
            color: var(--accent);
            border-color: rgba(88, 166, 255, 0.3);
        }}
        .actions-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
        }}
        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            font-weight: 600;
            padding: 10px 18px;
            border-radius: 6px;
            text-decoration: none;
            transition: all 0.2s ease;
            cursor: pointer;
        }}
        .btn-primary {{
            background: #238636;
            color: #ffffff;
            border: 1px solid rgba(240, 246, 252, 0.1);
            box-shadow: 0 0 12px rgba(46, 160, 67, 0.35);
        }}
        .btn-primary:hover {{
            background: #2ea043;
            transform: translateY(-1px);
        }}
        .btn-secondary {{
            background: #21262d;
            color: var(--text-main);
            border: 1px solid var(--border);
        }}
        .btn-secondary:hover {{
            background: #30363d;
            border-color: var(--border-hover);
            color: var(--accent);
        }}
        .layout-grid {{
            display: grid;
            grid-template-columns: 1fr 340px;
            gap: 24px;
            align-items: start;
        }}
        @media (max-width: 860px) {{
            .layout-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        .content-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        .card-heading {{
            font-size: 19px;
            font-weight: 600;
            margin: 0 0 16px 0;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .guide-summary {{
            color: var(--text-sub);
            font-size: 14px;
            margin: 0 0 18px 0;
            line-height: 1.6;
        }}
        .guide-prereqs {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 8px;
            padding: 14px 18px;
            margin-bottom: 20px;
        }}
        .guide-prereqs h3 {{
            font-size: 13.5px;
            font-weight: 600;
            margin: 0 0 8px 0;
            color: var(--text-main);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .guide-prereqs ul {{
            margin: 0;
            padding-left: 20px;
            color: var(--text-sub);
            font-size: 13.5px;
        }}
        .guide-prereqs li {{
            margin-bottom: 4px;
        }}
        .guide-step {{
            margin-bottom: 20px;
        }}
        .guide-step h4 {{
            font-size: 14.5px;
            font-weight: 600;
            margin: 0 0 8px 0;
            color: var(--accent);
        }}
        .guide-step p {{
            color: var(--text-sub);
            font-size: 13.5px;
            margin: 0 0 10px 0;
            white-space: pre-line;
        }}
        pre {{
            background: var(--code-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 14px;
            overflow-x: auto;
            margin: 0 0 12px 0;
        }}
        code {{
            font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
            font-size: 12.5px;
            color: #79c0ff;
            line-height: 1.5;
        }}
        .changelog-entry {{
            padding: 16px;
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.02);
            margin-bottom: 16px;
        }}
        .changelog-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }}
        .changelog-version {{
            font-size: 15px;
            font-weight: 700;
            color: var(--accent);
            font-family: monospace;
        }}
        .changelog-tag {{
            font-size: 11px;
            font-weight: 600;
            background: rgba(88, 166, 255, 0.1);
            color: var(--accent);
            padding: 2px 8px;
            border-radius: 999px;
            border: 1px solid rgba(88, 166, 255, 0.2);
        }}
        .changelog-date {{
            font-size: 12px;
            color: var(--text-sub);
            margin-left: auto;
            font-family: monospace;
        }}
        .changelog-list {{
            margin: 0;
            padding-left: 20px;
            color: var(--text-sub);
            font-size: 13.5px;
        }}
        .changelog-list li {{
            margin-bottom: 6px;
        }}
        .spec-list {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .spec-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            font-size: 13px;
        }}
        .spec-label {{
            color: var(--text-sub);
        }}
        .spec-value {{
            font-weight: 500;
            color: var(--text-main);
            font-family: monospace;
            text-align: right;
            max-width: 180px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .badge-group {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            flex-wrap: wrap;
            justify-content: flex-end;
        }}
        .badge {{
            display: inline-block;
            font-size: 11px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 999px;
            white-space: nowrap;
        }}
        .badge-os {{
            background: rgba(255, 255, 255, 0.06);
            color: var(--text-main);
            border: 1px solid var(--border);
            font-size: 11px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .os-android {{
            border-color: rgba(63, 185, 80, 0.35);
            background: rgba(63, 185, 80, 0.12);
            color: #56d364;
        }}
        .os-web {{
            border-color: rgba(88, 166, 255, 0.35);
            background: rgba(88, 166, 255, 0.12);
            color: #79c0ff;
        }}
        .os-ext {{
            border-color: rgba(210, 153, 34, 0.35);
            background: rgba(210, 153, 34, 0.12);
            color: #e3b341;
        }}
        .os-desktop {{
            border-color: rgba(188, 140, 255, 0.35);
            background: rgba(188, 140, 255, 0.12);
            color: #d2a8ff;
        }}
        .os-docker {{
            border-color: rgba(56, 139, 253, 0.35);
            background: rgba(56, 139, 253, 0.12);
            color: #58a6ff;
        }}
        .os-linux {{
            border-color: rgba(240, 136, 62, 0.35);
            background: rgba(240, 136, 62, 0.12);
            color: #ff9b5e;
        }}
        .os-lib {{
            border-color: rgba(188, 140, 255, 0.35);
            background: rgba(188, 140, 255, 0.12);
            color: #bc8cff;
        }}
        .os-tool {{
            border-color: rgba(240, 136, 62, 0.35);
            background: rgba(240, 136, 62, 0.12);
            color: #f0883e;
        }}
        .os-roku {{
            border-color: rgba(163, 113, 247, 0.35);
            background: rgba(163, 113, 247, 0.12);
            color: #d2a8ff;
        }}
        .os-server {{
            border-color: rgba(57, 197, 187, 0.35);
            background: rgba(57, 197, 187, 0.12);
            color: #4ee2d4;
        }}
        .os-windows {{
            border-color: rgba(0, 164, 239, 0.35);
            background: rgba(0, 164, 239, 0.12);
            color: #4dc9f6;
        }}
        .os-macos {{
            border-color: rgba(235, 235, 235, 0.35);
            background: rgba(235, 235, 235, 0.12);
            color: #e0e0e0;
        }}
        .os-chrome {{
            border-color: rgba(234, 67, 53, 0.35);
            background: rgba(234, 67, 53, 0.12);
            color: #f28b82;
        }}
        .os-firefox {{
            border-color: rgba(255, 113, 34, 0.35);
            background: rgba(255, 113, 34, 0.12);
            color: #ff9436;
        }}
        .os-python {{
            border-color: rgba(255, 212, 59, 0.35);
            background: rgba(255, 212, 59, 0.12);
            color: #ffe873;
        }}
        .os-dart {{
            border-color: rgba(1, 117, 194, 0.35);
            background: rgba(1, 117, 194, 0.12);
            color: #40c4ff;
        }}
        .os-template {{
            border-color: rgba(163, 113, 247, 0.35);
            background: rgba(163, 113, 247, 0.12);
            color: #d2a8ff;
        }}
        .os-docs {{
            border-color: rgba(88, 166, 255, 0.35);
            background: rgba(88, 166, 255, 0.12);
            color: #79c0ff;
        }}
        .os-cross {{
            border-color: rgba(110, 118, 129, 0.35);
            background: rgba(110, 118, 129, 0.12);
            color: #c9d1d9;
        }}
        .badge-live {{
            background: rgba(46, 160, 67, 0.2);
            color: var(--live);
            border: 1px solid rgba(46, 160, 67, 0.4);
        }}
        .badge-ready {{
            background: rgba(63, 185, 80, 0.15);
            color: var(--ready);
            border: 1px solid rgba(63, 185, 80, 0.3);
        }}
        .badge-active {{
            background: rgba(88, 166, 255, 0.15);
            color: var(--active);
            border: 1px solid rgba(88, 166, 255, 0.3);
        }}
        .badge-stable {{
            background: rgba(63, 185, 80, 0.15);
            color: var(--stable);
            border: 1px solid rgba(63, 185, 80, 0.3);
        }}
        .badge-planned {{
            background: rgba(88, 166, 255, 0.1);
            color: var(--accent);
            border: 1px solid rgba(88, 166, 255, 0.25);
        }}
        .badge-review {{
            background: rgba(210, 153, 34, 0.15);
            color: var(--review);
            border: 1px solid rgba(210, 153, 34, 0.3);
        }}
        .badge-placeholder {{
            background: rgba(110, 118, 129, 0.15);
            color: var(--placeholder);
            border: 1px solid rgba(110, 118, 129, 0.25);
        }}
        footer {{
            margin-top: 48px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
            color: var(--text-sub);
            font-size: 12px;
        }}
        footer a {{
            color: var(--accent);
            text-decoration: none;
        }}
        footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <nav class="nav-bar">
        <a href="../">← M3tal Hub</a>
        <span>/</span>
        <span>{cat_meta['title']}</span>
        <span>/</span>
        <span>{name}</span>
    </nav>

    <header class="hero-card">
        <div class="hero-header">
            <div class="hero-title-group">
                <div class="hero-icon">{cat_meta.get('icon', '⚙️')}</div>
                <div>
                    <h1 class="hero-title">{name}</h1>
                </div>
            </div>
            <div class="badge-group">
                {platform_badges_html}
                <span class="badge {badge_class}">{badge_text}</span>
            </div>
        </div>
        <p class="hero-desc">{desc}</p>
        <div class="meta-pills">
            {platform_pills_html}
            <span class="pill">{app_type}</span>
            <span class="pill">v{version}</span>
            <span class="pill">{cat_meta['title']}</span>
            <span class="pill">pkg: {package_val}</span>
            <span class="pill">ref: {str(last_released)[:10]}</span>
        </div>
        <div class="actions-row">
            {action_buttons_html}
        </div>
    </header>

    <main class="layout-grid">
        <div class="main-column">
            <section class="content-card">
                <h2 class="card-heading">📖 Installation & Setup Documentation</h2>
                {summary_html}
                {prereqs_html}
                {steps_html}
            </section>

            <section class="content-card">
                <h2 class="card-heading">📜 Version History & Changelog</h2>
                {changelog_html}
            </section>
        </div>

        <aside class="sidebar-column">
            <div class="content-card">
                <h2 class="card-heading">⚙️ System Specifications</h2>
                <div class="spec-list">
                    <div class="spec-item">
                        <span class="spec-label">Target OS / Platforms</span>
                        <span class="spec-value">{platforms_spec_str}</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-label">Target Architecture</span>
                        <span class="spec-value">{app_type}</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-label">Ecosystem Category</span>
                        <span class="spec-value">{cat_meta['title']}</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-label">Source Repository</span>
                        <span class="spec-value">jakej985-rgb/{repo}</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-label">Target Base Path</span>
                        <span class="spec-value">{base_href_val}</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-label">Current Release</span>
                        <span class="spec-value">v{version}</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-label">Package Format</span>
                        <span class="spec-value">{package_val}</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-label">Pipeline Status</span>
                        <span class="spec-value">{badge_text}</span>
                    </div>
                </div>
            </div>

            <div class="content-card">
                <h2 class="card-heading">🔗 Ecosystem Links</h2>
                <div class="spec-list">
                    <div class="spec-item">
                        <span class="spec-label">M3tal Hub Home</span>
                        <a href="../" class="spec-value" style="color: var(--accent); text-decoration: none;">View Directory ↗</a>
                    </div>
                    {f'''<div class="spec-item">
                        <span class="spec-label">Source Code</span>
                        <a href="{repo_url}" target="_blank" rel="noopener noreferrer" class="spec-value" style="color: var(--accent); text-decoration: none;">GitHub ↗</a>
                    </div>''' if repo_url else ''}
                    {f'''<div class="spec-item">
                        <span class="spec-label">GitHub Releases</span>
                        <a href="{release_url}" target="_blank" rel="noopener noreferrer" class="spec-value" style="color: var(--accent); text-decoration: none;">Releases ↗</a>
                    </div>''' if release_url else ''}
                </div>
            </div>
        </aside>
    </main>

    <footer>
        <div>M3tal Hub Unified Release Front • Source repositories maintain independent releases.</div>
        <div><a href="../">Return to Directory</a></div>
    </footer>
</body>
</html>
"""
    return html

def generate_hub(manifest_path, status_path, output_dir, site_status_path=None):
    data = load_manifest(manifest_path)
    status_data = load_status(status_path, site_status_path)
    releases = status_data.get("releases", {})

    apps = data.get("apps", [])

    # Group apps by category
    category_map = {c["id"]: [] for c in CATEGORIES}
    for app in apps:
        cat = app.get("category", "apps")
        if cat not in category_map:
            cat = "apps"
        category_map[cat].append(app)

    sections_html = []
    for cat_def in CATEGORIES:
        cat_id = cat_def["id"]
        cat_apps = category_map[cat_id]
        if not cat_apps:
            continue
        
        cards = []
        for app in cat_apps:
            app_id = app.get("id")
            release_info = releases.get(app_id, {})
            cards.append(render_card(app, release_info))
        
        rendered_grid = "\n".join(cards)
        section = f"""    <section class="section-group">
        <div class="section-header">
            <h2 class="section-title">{cat_def['title']}</h2>
            <p class="section-desc">{cat_def['description']}</p>
        </div>
        <div class="grid">
{rendered_grid}
        </div>
    </section>"""
        sections_html.append(section)

    all_sections = "\n\n".join(sections_html)

    # Calculate ecosystem stats
    app_count = len(category_map.get("apps", []))
    infra_count = len(category_map.get("infrastructure", []))
    lib_count = len(category_map.get("libraries", []))
    tool_count = len(category_map.get("tooling", []))

    generated_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>M3tal Hub | Unified Application & Ecosystem Release Front</title>
    <meta name="description" content="Central GitHub Pages release front and ecosystem directory for M3tal applications, services, and libraries.">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚙️</text></svg>">
    <style>
        :root {{
            --bg: #0d1117;
            --surface: #161b22;
            --surface-hover: #21262d;
            --border: #30363d;
            --border-hover: #58a6ff;
            --text-main: #e6edf3;
            --text-sub: #8b949e;
            --accent: #58a6ff;
            --ready: #3fb950;
            --live: #2ea043;
            --active: #58a6ff;
            --stable: #3fb950;
            --review: #d29922;
            --placeholder: #6e7681;
            --service: #bc8cff;
            --tooling: #f0883e;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
            max-width: 1120px;
            margin: 0 auto;
            padding: 40px 24px;
            line-height: 1.5;
            background: var(--bg);
            color: var(--text-main);
        }}
        header {{
            margin-bottom: 36px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 24px;
        }}
        .brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 8px;
        }}
        .brand h1 {{
            font-size: 30px;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.5px;
        }}
        .tagline {{
            color: var(--text-sub);
            font-size: 15px;
            margin: 0;
        }}
        .stats-bar {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 16px;
            font-size: 12px;
        }}
        .stat-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 4px 10px;
            border-radius: 999px;
            color: var(--text-sub);
        }}
        .stat-count {{
            font-weight: 700;
            color: var(--accent);
        }}
        .section-group {{
            margin-bottom: 44px;
        }}
        .section-header {{
            margin-bottom: 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            padding-bottom: 8px;
        }}
        .section-title {{
            font-size: 20px;
            font-weight: 600;
            margin: 0 0 4px 0;
            color: var(--text-main);
        }}
        .section-desc {{
            font-size: 13.5px;
            color: var(--text-sub);
            margin: 0;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 18px;
        }}
        .card {{
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 20px;
            border: 1px solid var(--border);
            border-radius: 10px;
            background: var(--surface);
            color: inherit;
            transition: border-color 0.2s ease, transform 0.2s ease, background-color 0.2s ease;
        }}
        .card:hover {{
            border-color: var(--border-hover);
            background: var(--surface-hover);
            transform: translateY(-2px);
        }}
        .card.info-card {{
            border-left: 3px solid rgba(88, 166, 255, 0.5);
        }}
        .card.info-card:hover {{
            border-left-color: var(--accent);
        }}
        .card.placeholder {{
            opacity: 0.6;
            border-style: dashed;
        }}
        .card.placeholder:hover {{
            opacity: 0.85;
            border-color: var(--text-sub);
        }}
        .card-main-link {{
            color: inherit;
            text-decoration: none;
            display: flex;
            flex-direction: column;
            flex-grow: 1;
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 8px;
            margin-bottom: 8px;
        }}
        .card h2 {{
            font-size: 17px;
            font-weight: 600;
            margin: 0;
            color: var(--text-main);
            display: flex;
            align-items: center;
        }}
        .card p {{
            margin: 0 0 16px 0;
            color: var(--text-sub);
            font-size: 13.5px;
            flex-grow: 1;
        }}
        .meta-row {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            color: var(--text-sub);
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }}
        .app-type {{
            background: rgba(88, 166, 255, 0.1);
            color: var(--accent);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }}
        .app-version {{
            background: rgba(255, 255, 255, 0.05);
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .app-date {{
            background: rgba(255, 255, 255, 0.05);
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .app-pkg {{
            background: rgba(188, 140, 255, 0.1);
            color: var(--service);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }}
        .card-actions {{
            display: flex;
            gap: 8px;
            margin-top: 14px;
            padding-top: 12px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }}
        .card-btn {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 12px;
            font-weight: 500;
            padding: 5px 10px;
            border-radius: 6px;
            text-decoration: none;
            border: 1px solid var(--border);
            background: rgba(255, 255, 255, 0.03);
            color: var(--text-main);
            transition: all 0.15s ease;
        }}
        .card-btn:hover {{
            border-color: var(--accent);
            color: var(--accent);
            background: rgba(88, 166, 255, 0.1);
        }}
        .card-btn-primary {{
            background: rgba(46, 160, 67, 0.15);
            border-color: rgba(46, 160, 67, 0.4);
            color: #3fb950;
        }}
        .card-btn-primary:hover {{
            background: rgba(46, 160, 67, 0.25);
            border-color: #3fb950;
            color: #56d364;
        }}
        .badge-group {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            flex-wrap: wrap;
            justify-content: flex-end;
        }}
        .badge {{
            display: inline-block;
            font-size: 11px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 999px;
            white-space: nowrap;
        }}
        .badge-os {{
            background: rgba(255, 255, 255, 0.06);
            color: var(--text-main);
            border: 1px solid var(--border);
            font-size: 10.5px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .os-android {{
            border-color: rgba(63, 185, 80, 0.35);
            background: rgba(63, 185, 80, 0.12);
            color: #56d364;
        }}
        .os-web {{
            border-color: rgba(88, 166, 255, 0.35);
            background: rgba(88, 166, 255, 0.12);
            color: #79c0ff;
        }}
        .os-ext {{
            border-color: rgba(210, 153, 34, 0.35);
            background: rgba(210, 153, 34, 0.12);
            color: #e3b341;
        }}
        .os-desktop {{
            border-color: rgba(188, 140, 255, 0.35);
            background: rgba(188, 140, 255, 0.12);
            color: #d2a8ff;
        }}
        .os-docker {{
            border-color: rgba(56, 139, 253, 0.35);
            background: rgba(56, 139, 253, 0.12);
            color: #58a6ff;
        }}
        .os-linux {{
            border-color: rgba(240, 136, 62, 0.35);
            background: rgba(240, 136, 62, 0.12);
            color: #ff9b5e;
        }}
        .os-lib {{
            border-color: rgba(188, 140, 255, 0.35);
            background: rgba(188, 140, 255, 0.12);
            color: #bc8cff;
        }}
        .os-tool {{
            border-color: rgba(240, 136, 62, 0.35);
            background: rgba(240, 136, 62, 0.12);
            color: #f0883e;
        }}
        .os-roku {{
            border-color: rgba(163, 113, 247, 0.35);
            background: rgba(163, 113, 247, 0.12);
            color: #d2a8ff;
        }}
        .os-server {{
            border-color: rgba(57, 197, 187, 0.35);
            background: rgba(57, 197, 187, 0.12);
            color: #4ee2d4;
        }}
        .os-windows {{
            border-color: rgba(0, 164, 239, 0.35);
            background: rgba(0, 164, 239, 0.12);
            color: #4dc9f6;
        }}
        .os-macos {{
            border-color: rgba(235, 235, 235, 0.35);
            background: rgba(235, 235, 235, 0.12);
            color: #e0e0e0;
        }}
        .os-chrome {{
            border-color: rgba(234, 67, 53, 0.35);
            background: rgba(234, 67, 53, 0.12);
            color: #f28b82;
        }}
        .os-firefox {{
            border-color: rgba(255, 113, 34, 0.35);
            background: rgba(255, 113, 34, 0.12);
            color: #ff9436;
        }}
        .os-python {{
            border-color: rgba(255, 212, 59, 0.35);
            background: rgba(255, 212, 59, 0.12);
            color: #ffe873;
        }}
        .os-dart {{
            border-color: rgba(1, 117, 194, 0.35);
            background: rgba(1, 117, 194, 0.12);
            color: #40c4ff;
        }}
        .os-template {{
            border-color: rgba(163, 113, 247, 0.35);
            background: rgba(163, 113, 247, 0.12);
            color: #d2a8ff;
        }}
        .os-docs {{
            border-color: rgba(88, 166, 255, 0.35);
            background: rgba(88, 166, 255, 0.12);
            color: #79c0ff;
        }}
        .os-cross {{
            border-color: rgba(110, 118, 129, 0.35);
            background: rgba(110, 118, 129, 0.12);
            color: #c9d1d9;
        }}
        .badge-live {{
            background: rgba(46, 160, 67, 0.2);
            color: var(--live);
            border: 1px solid rgba(46, 160, 67, 0.4);
        }}
        .badge-ready {{
            background: rgba(63, 185, 80, 0.15);
            color: var(--ready);
            border: 1px solid rgba(63, 185, 80, 0.3);
        }}
        .badge-active {{
            background: rgba(88, 166, 255, 0.15);
            color: var(--active);
            border: 1px solid rgba(88, 166, 255, 0.3);
        }}
        .badge-stable {{
            background: rgba(63, 185, 80, 0.15);
            color: var(--stable);
            border: 1px solid rgba(63, 185, 80, 0.3);
        }}
        .badge-planned {{
            background: rgba(88, 166, 255, 0.1);
            color: var(--accent);
            border: 1px solid rgba(88, 166, 255, 0.25);
        }}
        .badge-review {{
            background: rgba(210, 153, 34, 0.15);
            color: var(--review);
            border: 1px solid rgba(210, 153, 34, 0.3);
        }}
        .badge-placeholder {{
            background: rgba(110, 118, 129, 0.15);
            color: var(--placeholder);
            border: 1px solid rgba(110, 118, 129, 0.25);
        }}
        footer {{
            margin-top: 48px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
            color: var(--text-sub);
            font-size: 12px;
        }}
        footer a {{
            color: var(--accent);
            text-decoration: none;
        }}
        footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <h1>⚙️ M3tal Hub</h1>
        </div>
        <p class="tagline">Unified GitHub Pages release front & ecosystem directory for M3tal applications, services, and libraries.</p>
        <div class="stats-bar">
            <span class="stat-pill"><span class="stat-count">{app_count}</span> Applications</span>
            <span class="stat-pill"><span class="stat-count">{infra_count}</span> Infrastructure & Services</span>
            <span class="stat-pill"><span class="stat-count">{lib_count}</span> Libraries & Templates</span>
            <span class="stat-pill"><span class="stat-count">{tool_count}</span> Tooling & Documentation</span>
        </div>
    </header>

    <main>
{all_sections}
    </main>

    <footer>
        <div>Centralized release front. Source repositories maintain independent releases.</div>
        <div>Generated: {generated_time}</div>
    </footer>
</body>
</html>
"""

    error_404_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Not Found | M3tal Hub</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
            background: #0d1117;
            color: #e6edf3;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 80vh;
            margin: 0;
            padding: 20px;
            text-align: center;
        }
        h1 { font-size: 48px; margin: 0 0 16px 0; color: #58a6ff; }
        p { color: #8b949e; font-size: 16px; margin: 0 0 24px 0; max-width: 480px; }
        a {
            display: inline-block;
            background: #21262d;
            border: 1px solid #30363d;
            color: #58a6ff;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        a:hover {
            border-color: #58a6ff;
            background: #30363d;
        }
    </style>
</head>
<body>
    <h1>404</h1>
    <p>The requested application or path could not be found under M3tal Hub.</p>
    <a href="../">Return to Hub Home</a>
</body>
</html>
"""

    os.makedirs(output_dir, exist_ok=True)

    index_output_path = os.path.join(output_dir, "index.html")
    with open(index_output_path, "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"Generated {index_output_path}")

    error_output_path = os.path.join(output_dir, "404.html")
    with open(error_output_path, "w", encoding="utf-8") as f:
        f.write(error_404_html)
    print(f"Generated {error_output_path}")

    # Generate individual application detail pages in output_dir/apps/
    apps_out_dir = os.path.join(output_dir, "apps")
    os.makedirs(apps_out_dir, exist_ok=True)

    for app in apps:
        app_id = app.get("id")
        rel_info = releases.get(app_id, {})
        page_html = generate_app_page(app, rel_info, category_map)
        app_page_path = os.path.join(apps_out_dir, f"{app_id}.html")
        with open(app_page_path, "w", encoding="utf-8") as f:
            f.write(page_html)
        print(f"Generated {app_page_path}")

    # Synchronize merged status to output directory
    out_status_path = os.path.join(apps_out_dir, "status.json")
    with open(out_status_path, "w", encoding="utf-8") as f:
        json.dump(status_data, f, indent=2)
    print(f"Synchronized {out_status_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest = os.path.join(base_dir, "apps", "manifest.yml")
    status = os.path.join(base_dir, "apps", "status.json")
    out = sys.argv[1] if len(sys.argv) > 1 else base_dir

    site_status = None
    if os.path.abspath(out) != os.path.abspath(base_dir):
        candidate_site_status = os.path.join(out, "apps", "status.json")
        if os.path.exists(candidate_site_status):
            site_status = candidate_site_status

    generate_hub(manifest, status, out, site_status_path=site_status)
