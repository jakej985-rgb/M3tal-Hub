#!/usr/bin/env python3
"""
M3tal-Hub Dynamic Landing Page Generator
Reads apps/manifest.yml and apps/status.json, generating index.html and 404.html.
Supports application releases, infrastructure services, libraries, and tooling.
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
    },
    {
        "id": "infrastructure",
        "title": "Infrastructure & Backend Services",
        "description": "Core infrastructure, backend services, container environments, and deployment stacks.",
    },
    {
        "id": "libraries",
        "title": "Libraries, SDKs & Templates",
        "description": "Shared component libraries, UI kits, API wrappers, and module scaffolding templates.",
    },
    {
        "id": "tooling",
        "title": "Tooling & Documentation",
        "description": "Developer tooling, package repositories, automation utilities, and architecture specs.",
    },
]

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

def render_card(app, release_info):
    name = app.get("name")
    desc = app.get("description", "")
    repo = app.get("repo", "")
    path = app.get("path", "")
    enabled = app.get("enabled", False)
    category = app.get("category", "apps")
    
    badge_text, badge_class = get_badge(app, release_info)

    meta_info = []
    if app.get("type"):
        meta_info.append(f'<span class="app-type">{app["type"]}</span>')
    
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

    valid_web_types = {'flutter-web', 'vite', 'web', 'static'}
    is_web_deployable = app.get("type") in valid_web_types

    if enabled and is_web_deployable:
        href = f"./{path}/"
        card_class = "card"
        is_external = False
    else:
        href = app.get("url") or app.get("release_url") or app.get("repo_url") or app.get("docs_url") or (f"https://github.com/jakej985-rgb/{repo}" if repo else "#")
        is_external = href.startswith("http://") or href.startswith("https://")
        if category == "apps" and app.get("status") in ["placeholder", "review", None]:
            card_class = "card placeholder"
        else:
            card_class = "card info-card"

    target_attr = ' target="_blank" rel="noopener noreferrer"' if is_external else ''
    icon_html = ' <span class="ext-icon" aria-hidden="true">↗</span>' if is_external else ''

    return f"""        <a class="{card_class}" href="{href}"{target_attr}>
            <div class="card-header">
                <h2>{name}{icon_html}</h2>
                <span class="badge {badge_class}">{badge_text}</span>
            </div>
            <p>{desc}</p>
            {meta_html}
        </a>"""

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
            text-decoration: none;
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
        .ext-icon {{
            font-size: 13px;
            color: var(--text-sub);
            opacity: 0.7;
            margin-left: 5px;
            font-weight: normal;
        }}
        .card:hover .ext-icon {{
            color: var(--accent);
            opacity: 1;
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
        .badge {{
            display: inline-block;
            font-size: 11px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 999px;
            white-space: nowrap;
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
    <a href="./">Return to Hub Home</a>
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

    # Synchronize merged status to output directory
    apps_out_dir = os.path.join(output_dir, "apps")
    os.makedirs(apps_out_dir, exist_ok=True)
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
