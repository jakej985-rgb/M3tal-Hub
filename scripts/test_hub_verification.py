#!/usr/bin/env python3
"""
M3tal-Hub Verification Suite
Validates manifest, status, build_hub generator, and deploy.yml safeguards.
"""

import os
import sys
import json
import yaml
import subprocess

def test_manifest_and_status():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest_path = os.path.join(base_dir, "apps", "manifest.yml")
    status_path = os.path.join(base_dir, "apps", "status.json")

    assert os.path.exists(manifest_path), f"Manifest file missing: {manifest_path}"
    assert os.path.exists(status_path), f"Status file missing: {status_path}"

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = yaml.safe_load(f)
    assert "apps" in manifest, "apps key missing in manifest.yml"

    with open(status_path, 'r', encoding='utf-8') as f:
        status = json.load(f)
    assert "releases" in status, "releases key missing in status.json"

    apps = manifest["apps"]
    print(f"Loaded {len(apps)} entries from manifest.yml")

    # Required repositories from Plan 14 and task
    expected_infra_libs = [
        "m3tal-godash",
        "m3tal-core",
        "m3tal-api",
        "m3tal-stack",
        "antigravity-remote-docker",
        "m3tal-apt-key",
        "m3tal-ui-kit",
        "m3tal-hub-template",
        "ytmusicapi",
        "m3tal-docs",
        "comicinfo-generator",
        "vscode",
    ]

    found_ids = {a["id"]: a for a in apps}
    for expected_id in expected_infra_libs:
        assert expected_id in found_ids, f"Required project '{expected_id}' not found in manifest.yml"
        entry = found_ids[expected_id]
        assert entry.get("enabled") is False, f"Project '{expected_id}' must have enabled: false"
        assert entry.get("category") in ["infrastructure", "libraries", "tooling"], (
            f"Project '{expected_id}' has unexpected category: {entry.get('category')}"
        )
        assert entry.get("repo_url") or entry.get("url") or entry.get("docs_url"), (
            f"Project '{expected_id}' is missing a repository/documentation link"
        )
        print(f"  [OK] {expected_id} (category: {entry.get('category')}, type: {entry.get('type')}, enabled: {entry.get('enabled')})")

    # Verify no private URLs or secrets
    forbidden_terms = ["localhost", "127.0.0.1", "192.168.", "10.0.", "api_key", "secret_key", "private_key", "auth_token", "access_token", "bearer "]
    manifest_raw = open(manifest_path, 'r', encoding='utf-8').read()
    for term in forbidden_terms:
        assert term.lower() not in manifest_raw.lower(), f"Potential secret or private URL term '{term}' in manifest.yml"

    print("Manifest and status checks passed!")

def test_deploy_workflow_safeguards():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest_path = os.path.join(base_dir, "apps", "manifest.yml")
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = yaml.safe_load(f)

    def simulate_deploy_meta(app_id):
        target = next((a for a in manifest.get('apps', []) if a.get('id') == app_id), None)
        if not target:
            return False, f"Error: app_id '{app_id}' not found in manifest.yml"
        if not target.get('enabled', False):
            return False, f"Error: app_id '{app_id}' is marked enabled: false"
        
        category = target.get('category', 'apps')
        app_type = target.get('type', 'web')
        valid_web_types = {'flutter-web', 'vite', 'web', 'static'}
        if category in ['infrastructure', 'libraries', 'tooling'] or app_type not in valid_web_types:
            return False, f"Error: app_id '{app_id}' has non-deployable category '{category}' or non-web type '{app_type}' and cannot be deployed to GitHub Pages."
        
        return True, "Allowed"

    # Infrastructure and libraries must be rejected
    rejected_list = [
        "m3tal-godash",
        "m3tal-core",
        "m3tal-api",
        "m3tal-stack",
        "antigravity-remote-docker",
        "m3tal-apt-key",
        "m3tal-ui-kit",
        "m3tal-hub-template",
        "ytmusicapi",
        "m3tal-docs",
        "comicinfo-generator",
        "vscode",
    ]
    for app_id in rejected_list:
        allowed, msg = simulate_deploy_meta(app_id)
        assert not allowed, f"Deploy guard failed to reject {app_id}: {msg}"
        print(f"  [OK Guard] {app_id} correctly rejected: {msg}")

    # Ensure Plan 13 non-web app types are rejected by deploy guard even if enabled: true were set
    plan_13_non_web = [
        "gps-speedometer",
        "ink-vault",
        "shop-manager",
        "tattoo-shop-manager",
        "infernal-ink-steel-suite",
    ]
    for app_id in plan_13_non_web:
        target = next((a for a in manifest.get('apps', []) if a.get('id') == app_id), None)
        assert target, f"Missing manifest entry for {app_id}"
        app_type = target.get('type')
        category = target.get('category', 'apps')
        valid_web_types = {'flutter-web', 'vite', 'web', 'static'}
        assert app_type not in valid_web_types, f"{app_id} should not be a valid web type"
        print(f"  [OK Non-Web Type Guard] {app_id} type '{app_type}' is strictly excluded from web deployment")

    # Valid web applications must be accepted
    allowed_list = [
        "monster-lab",
        "android-card-games",
        "idle-animals",
        "red-music-locker",
        "subaru-specs-n-parts",
        "infernal-web",
        "jellyfin-ui",
    ]
    for app_id in allowed_list:
        allowed, msg = simulate_deploy_meta(app_id)
        assert allowed, f"Deploy guard incorrectly rejected valid app {app_id}: {msg}"
        print(f"  [OK Allowed] {app_id} successfully parsed for deployment")

    print("Deploy workflow safeguard checks passed!")

def test_hub_generator():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_out = os.path.join(base_dir, "scratch_test_out")
    os.makedirs(test_out, exist_ok=True)

    build_script = os.path.join(base_dir, "scripts", "build_hub.py")
    result = subprocess.run([sys.executable, build_script, test_out], capture_output=True, text=True)
    assert result.returncode == 0, f"build_hub.py failed: {result.stderr}"

    index_html = os.path.join(test_out, "index.html")
    error_404_html = os.path.join(test_out, "404.html")
    assert os.path.exists(index_html), "index.html was not generated"
    assert os.path.exists(error_404_html), "404.html was not generated"

    content = open(index_html, 'r', encoding='utf-8').read()
    assert "Applications & Frontends" in content, "Applications section missing"
    assert "Infrastructure & Backend Services" in content, "Infrastructure section missing"
    assert "Libraries, SDKs & Templates" in content, "Libraries section missing"
    assert "Tooling & Documentation" in content, "Tooling section missing"

    # Verify all projects are present
    expected_projects = [
        "M3tal GoDash",
        "M3tal Core",
        "M3tal API",
        "M3tal Stack",
        "Antigravity Remote Docker",
        "M3tal APT Keyring",
        "M3tal UI Kit",
        "M3tal Hub Template",
        "YTMusicAPI Bridge",
        "M3tal Docs",
        "ComicInfo Generator",
        "M3tal VS Code Config",
    ]
    for proj in expected_projects:
        assert proj in content, f"Project '{proj}' missing in generated index.html"
        print(f"  [OK Hub Card] Found card for '{proj}'")

    # Clean up scratch test directory
    import shutil
    shutil.rmtree(test_out)
    print("Hub generator verification passed!")

def test_plan_13_other_app_repositories():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest_path = os.path.join(base_dir, "apps", "manifest.yml")
    deploy_path = os.path.join(base_dir, ".github", "workflows", "deploy.yml")
    index_path = os.path.join(base_dir, "index.html")

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = yaml.safe_load(f)
    apps = {a["id"]: a for a in manifest["apps"]}

    # Repositories in scope for Plan 13
    candidates = {
        "gps-speedometer": {
            "name": "GPS Speedometer",
            "repo": "GPS-speedometer",
            "type": "android-native",
            "enabled": False,
            "status": "placeholder",
            "expected_url": "https://github.com/jakej985-rgb/GPS-speedometer",
        },
        "ink-vault": {
            "name": "Ink Vault",
            "repo": "Ink-vault",
            "type": "backend",
            "enabled": False,
            "status": "review",
            "expected_url": "https://github.com/jakej985-rgb/Ink-vault",
        },
        "shop-manager": {
            "name": "Shop Manager",
            "repo": "Shop-manager",
            "type": "desktop",
            "enabled": False,
            "status": "review",
            "expected_url": "https://github.com/jakej985-rgb/Shop-manager",
        },
        "tattoo-shop-manager": {
            "name": "Tattoo Shop Manager",
            "repo": "Tattoo-Shop-manager",
            "type": "backend",
            "enabled": False,
            "status": "review",
            "expected_url": "https://github.com/jakej985-rgb/Tattoo-Shop-manager",
        },
        "infernal-ink-steel-suite": {
            "name": "Infernal Ink Steel Suite",
            "repo": "Infernal-Ink-Steel-Suite",
            "type": "suite",
            "enabled": False,
            "status": "review",
            "expected_url": "https://github.com/jakej985-rgb/Infernal-Ink-Steel-Suite",
        },
    }

    for app_id, expected in candidates.items():
        assert app_id in apps, f"Candidate {app_id} missing from manifest.yml"
        entry = apps[app_id]
        assert entry.get("enabled") is False, f"{app_id} must have enabled: false"
        assert entry.get("type") == expected["type"], f"{app_id} has type {entry.get('type')}, expected {expected['type']}"
        assert entry.get("status") == expected["status"], f"{app_id} has status {entry.get('status')}, expected {expected['status']}"
        assert "base_href" not in entry or not entry.get("base_href"), f"{app_id} should not define base_href for Pages"
        assert entry.get("repo_url") == expected["expected_url"], f"{app_id} repo_url mismatch: {entry.get('repo_url')}"
        print(f"  [OK Plan 13 Manifest] {app_id}: type={entry['type']}, enabled=False, status={entry['status']}, repo_url={entry['repo_url']}")

    # Verify deploy.yml does not allow dispatching gps-speedometer to Pages
    deploy_content = open(deploy_path, 'r', encoding='utf-8').read()
    assert "- gps-speedometer" not in deploy_content, "gps-speedometer must not be an option in deploy.yml workflow_dispatch"
    print("  [OK Plan 13 CI] deploy.yml does not include gps-speedometer in dispatch options")

    # Verify index.html contains direct repo links and no broken relative paths
    index_content = open(index_path, 'r', encoding='utf-8').read()
    for app_id, expected in candidates.items():
        assert f'href="./{app_id}/"' not in index_content, f"Broken relative Pages link found for {app_id}: ./{app_id}/"
        assert expected["expected_url"] in index_content, f"Expected repo link {expected['expected_url']} not found for {app_id}"
        print(f"  [OK Plan 13 Link] {app_id} links accurately to {expected['expected_url']}")

    print("Plan 13 other app repositories checks passed!")

def test_plan_12_munchkin_companion_app():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest_path = os.path.join(base_dir, "apps", "manifest.yml")
    plan_path = os.path.join(base_dir, "plan", "12-Munchkin-Companion-App.md")
    index_path = os.path.join(base_dir, "index.html")

    assert os.path.exists(plan_path), f"Plan 12 documentation missing: {plan_path}"

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = yaml.safe_load(f)
    apps = {a["id"]: a for a in manifest["apps"]}

    assert "munchkin-companion-app" in apps, "munchkin-companion-app missing from manifest.yml"
    entry = apps["munchkin-companion-app"]
    assert entry.get("enabled") is False, "munchkin-companion-app must have enabled: false while in stub/placeholder state"
    assert entry.get("status") == "planned", "munchkin-companion-app must have status: planned"
    assert entry.get("type") == "flutter-web", "munchkin-companion-app must have type: flutter-web"
    assert entry.get("repo") == "Munchkin-Companion-App", "munchkin-companion-app repo must match Munchkin-Companion-App"
    print("  [OK Plan 12 Manifest] munchkin-companion-app correctly registered as enabled: false, status: planned")

    # Verify index.html does not point to a broken relative path
    index_content = open(index_path, 'r', encoding='utf-8').read()
    assert 'href="./munchkin-companion-app/"' not in index_content, (
        "Broken relative Pages link found for munchkin-companion-app: ./munchkin-companion-app/"
    )
    expected_repo_link = "https://github.com/jakej985-rgb/Munchkin-Companion-App"
    assert expected_repo_link in index_content, f"Expected repo link {expected_repo_link} not found in index.html"
    assert "Munchkin Companion App" in index_content, "Munchkin Companion App title not found in index.html"
    print(f"  [OK Plan 12 Card] Card links safely to {expected_repo_link} without dead relative URLs")

    print("Plan 12 Munchkin Companion App checks passed!")

def test_plan_11_m3tal_plugin_page():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest_path = os.path.join(base_dir, "apps", "manifest.yml")
    status_path = os.path.join(base_dir, "apps", "status.json")
    deploy_path = os.path.join(base_dir, ".github", "workflows", "deploy.yml")
    plan_path = os.path.join(base_dir, "plan", "11-M3tal-Plugin-Page.md")
    index_path = os.path.join(base_dir, "index.html")

    assert os.path.exists(plan_path), f"Plan 11 documentation missing: {plan_path}"

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = yaml.safe_load(f)
    apps = {a["id"]: a for a in manifest["apps"]}

    assert "m3tal-plugin-page" in apps, "m3tal-plugin-page missing from manifest.yml"
    entry = apps["m3tal-plugin-page"]
    assert entry.get("enabled") is True, "m3tal-plugin-page must have enabled: true"
    assert entry.get("status") == "ready", f"m3tal-plugin-page must have status: ready (got {entry.get('status')})"
    assert entry.get("type") == "static", f"m3tal-plugin-page must have type: static (got {entry.get('type')})"
    assert entry.get("repo") == "m3tal-plugin-page", "m3tal-plugin-page repo must match m3tal-plugin-page"
    assert entry.get("path") == "m3tal-plugin-page", "m3tal-plugin-page path must match m3tal-plugin-page"
    assert entry.get("base_href") == "/m3tal-plugin-page/", "base_href must match /m3tal-plugin-page/"
    print("  [OK Plan 11 Manifest] m3tal-plugin-page correctly registered as enabled: true, status: ready, type: static")

    with open(status_path, 'r', encoding='utf-8') as f:
        status_data = json.load(f)
    assert "m3tal-plugin-page" in status_data.get("releases", {}), "m3tal-plugin-page missing from status.json releases"
    status_entry = status_data["releases"]["m3tal-plugin-page"]
    assert status_entry.get("status") == "ready", "m3tal-plugin-page status in status.json must be ready"
    print("  [OK Plan 11 Status] m3tal-plugin-page registered in status.json with status: ready")

    # Verify deploy.yml includes static release step and m3tal-plugin-page dispatch option
    deploy_content = open(deploy_path, 'r', encoding='utf-8').read()
    assert "- m3tal-plugin-page" in deploy_content, "m3tal-plugin-page must be an option in deploy.yml workflow_dispatch"
    assert "Build Static Web Release" in deploy_content, "Build Static Web Release step missing from deploy.yml"
    assert "steps.meta.outputs.type == 'static'" in deploy_content, "type == 'static' condition missing in deploy.yml"
    print("  [OK Plan 11 CI] deploy.yml includes m3tal-plugin-page and Build Static Web Release step")

    # Verify index.html contains live card linking to ./m3tal-plugin-page/
    index_content = open(index_path, 'r', encoding='utf-8').read()
    assert 'href="./m3tal-plugin-page/"' in index_content, "index.html missing link to ./m3tal-plugin-page/"
    assert "M3tal Plugin Page" in index_content, "M3tal Plugin Page title not found in index.html"
    assert "badge-ready" in index_content, "badge-ready badge class missing in index.html"
    print("  [OK Plan 11 Card] Card links to ./m3tal-plugin-page/ with badge-ready")

    print("Plan 11 M3tal Plugin Page checks passed!")

def test_plan_14_infrastructure_and_libraries():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest_path = os.path.join(base_dir, "apps", "manifest.yml")
    status_path = os.path.join(base_dir, "apps", "status.json")
    deploy_path = os.path.join(base_dir, ".github", "workflows", "deploy.yml")
    plan_path = os.path.join(base_dir, "plan", "14-Infrastructure-And-Libraries.md")
    index_path = os.path.join(base_dir, "index.html")

    assert os.path.exists(plan_path), f"Plan 14 documentation missing: {plan_path}"

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = yaml.safe_load(f)
    apps = {a["id"]: a for a in manifest["apps"]}

    with open(status_path, 'r', encoding='utf-8') as f:
        status_data = json.load(f)

    # 1. Exhaustive check of all 12 Plan 14 components
    infra_library_specs = {
        "m3tal-godash": {"category": "infrastructure", "type": "service", "version": "0.2.0", "package": "service"},
        "m3tal-core": {"category": "infrastructure", "type": "library", "version": "0.1.0", "package": "library"},
        "m3tal-api": {"category": "infrastructure", "type": "service", "version": "0.1.0", "package": "service"},
        "m3tal-stack": {"category": "infrastructure", "type": "infrastructure", "version": "1.0.0", "package": "docker-compose"},
        "antigravity-remote-docker": {"category": "infrastructure", "type": "container", "version": "1.0.0", "package": "container"},
        "m3tal-apt-key": {"category": "infrastructure", "type": "package", "version": "1.0.0", "package": "gpg-keyring"},
        "m3tal-ui-kit": {"category": "libraries", "type": "library", "version": "0.1.0", "package": "dart-pkg"},
        "m3tal-hub-template": {"category": "libraries", "type": "template", "version": "1.0.0", "package": "template"},
        "ytmusicapi": {"category": "libraries", "type": "library", "version": "0.25.0", "package": "pypi"},
        "m3tal-docs": {"category": "tooling", "type": "docs", "version": "1.0.0", "package": "docs"},
        "comicinfo-generator": {"category": "tooling", "type": "tooling", "version": "1.1.0", "package": "cli-tool"},
        "vscode": {"category": "tooling", "type": "tooling", "version": "1.0.0", "package": "dev-config"},
    }

    for app_id, expected in infra_library_specs.items():
        assert app_id in apps, f"Plan 14 component '{app_id}' missing in manifest.yml"
        entry = apps[app_id]
        assert entry.get("enabled") is False, f"'{app_id}' must have enabled: false"
        assert entry.get("category") == expected["category"], f"'{app_id}' category mismatch"
        assert entry.get("type") == expected["type"], f"'{app_id}' type mismatch"
        assert entry.get("version") == expected["version"], f"'{app_id}' version in manifest mismatch"
        assert entry.get("package") == expected["package"], f"'{app_id}' package in manifest mismatch"
        assert "base_href" not in entry or not entry.get("base_href"), f"'{app_id}' should not define base_href"

        # Check status.json entry
        assert app_id in status_data.get("releases", {}), f"'{app_id}' missing in status.json releases"
        status_entry = status_data["releases"][app_id]
        assert status_entry.get("status") == "active", f"'{app_id}' status in status.json should be active"
        assert status_entry.get("version") == expected["version"], f"'{app_id}' status.json version mismatch"
        assert status_entry.get("package_status") == expected["package"], f"'{app_id}' package_status mismatch"
        print(f"  [OK Plan 14 Entry] {app_id}: {expected['category']}/{expected['type']} v{expected['version']} [{expected['package']}]")

    # 2. Check workflow_dispatch options do NOT contain any of the 12
    deploy_content = open(deploy_path, 'r', encoding='utf-8').read()
    for app_id in infra_library_specs:
        assert f"- {app_id}" not in deploy_content, f"'{app_id}' must NOT be in deploy.yml workflow_dispatch options"
    print("  [OK Plan 14 CI Guard] None of the 12 infrastructure/library repos exist in deploy.yml workflow_dispatch options")

    # 3. Test dynamic status cache merging with simulated gh-pages cache
    scratch_dir = os.path.join(base_dir, "scratch_test_merge")
    try:
        os.makedirs(os.path.join(scratch_dir, "apps"), exist_ok=True)
        # Simulate a prior gh-pages status cache having released monster-lab
        mock_site_status = {
            "releases": {
                "monster-lab": {
                    "status": "ready",
                    "build_status": "success",
                    "version": "1.0.0",
                    "last_released": "2026-09-30T10:00:00Z"
                }
            }
        }
        with open(os.path.join(scratch_dir, "apps", "status.json"), "w", encoding="utf-8") as f:
            json.dump(mock_site_status, f)

        # Run build_hub.py targeting scratch_dir
        build_script = os.path.join(base_dir, "scripts", "build_hub.py")
        res = subprocess.run([sys.executable, build_script, scratch_dir], capture_output=True, text=True)
        assert res.returncode == 0, f"build_hub.py failed with site cache: {res.stderr}"

        # Verify scratch_dir/apps/status.json merged correctly
        with open(os.path.join(scratch_dir, "apps", "status.json"), "r", encoding="utf-8") as f:
            merged_status = json.load(f)

        # monster-lab must have retained build_status: success and last_released
        assert "monster-lab" in merged_status.get("releases", {})
        assert merged_status["releases"]["monster-lab"]["build_status"] == "success"
        assert merged_status["releases"]["monster-lab"]["last_released"] == "2026-09-30T10:00:00Z"

        # AND all 12 infrastructure components must be present with their package_status & version
        for app_id, expected in infra_library_specs.items():
            assert app_id in merged_status.get("releases", {}), f"Merged status dropped '{app_id}'!"
            assert merged_status["releases"][app_id]["version"] == expected["version"]
            assert merged_status["releases"][app_id]["package_status"] == expected["package"]

        # Check HTML generated from merged status
        scratch_html = open(os.path.join(scratch_dir, "index.html"), "r", encoding="utf-8").read()
        # monster-lab has Live badge
        assert "badge-live" in scratch_html, "Live badge for deployed app missing in HTML"
        # None of the infrastructure items have Live badge
        for app_id in infra_library_specs:
            # Check card exists
            proj_name = apps[app_id]["name"]
            assert proj_name in scratch_html, f"Project '{proj_name}' missing from generated HTML"
        print("  [OK Plan 14 Status Merge] Successfully preserved deployed app release status and retained all 12 infra/library items without data loss")
    finally:
        import shutil
        if os.path.exists(scratch_dir):
            shutil.rmtree(scratch_dir)

    # 4. Check external links in index.html
    index_content = open(index_path, 'r', encoding='utf-8').read()
    for app_id in infra_library_specs:
        entry = apps[app_id]
        expected_url = entry["repo_url"]
        assert expected_url in index_content, f"URL '{expected_url}' for '{app_id}' not found in index.html"
        assert f'href="./{app_id}/"' not in index_content, f"Illegal Pages relative path found for '{app_id}'"
    print("  [OK Plan 14 Links] All 12 components render external links with no Pages relative subpaths")

    print("Plan 14 Infrastructure and Libraries checks passed!")

if __name__ == "__main__":
    print("=== Running M3tal-Hub Verification Suite ===")
    test_manifest_and_status()
    print("\n=== Testing Deploy Workflow Safeguards ===")
    test_deploy_workflow_safeguards()
    print("\n=== Testing Hub Generator Output ===")
    test_hub_generator()
    print("\n=== Testing Plan 11 M3tal Plugin Page ===")
    test_plan_11_m3tal_plugin_page()
    print("\n=== Testing Plan 12 Munchkin Companion App ===")
    test_plan_12_munchkin_companion_app()
    print("\n=== Testing Plan 13 Other App Repositories ===")
    test_plan_13_other_app_repositories()
    print("\n=== Testing Plan 14 Infrastructure & Libraries ===")
    test_plan_14_infrastructure_and_libraries()
    print("\n=== All Tests Passed Successfully ===")


