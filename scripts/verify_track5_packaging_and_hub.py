#!/usr/bin/env python3
"""
Track 5 Verification Suite: M3tal-Core Packaging, App Installation Standards & Hub Integration
Validates Phases 11, 12, and 13 implementations across m3tal-apt-key and M3tal-Hub.
"""

import os
import sys
import subprocess
import tarfile
import tempfile
import re

HUB_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APT_KEY_ROOT = "/home/m3tal/apps/m3tal-apt-key"
DEB_PATH = os.path.join(APT_KEY_ROOT, "pool", "main", "m3tal_v1.1.62_amd64.deb")

def print_step(msg):
    print(f"--> {msg}")

def check_deb_packaging():
    print_step("1. Verifying m3tal-core Debian package architecture and payload (Phase 11)...")
    assert os.path.exists(DEB_PATH), f"m3tal package missing at {DEB_PATH}"

    # Use dpkg-deb to inspect control and data
    res_control = subprocess.run(["dpkg-deb", "-I", DEB_PATH], capture_output=True, text=True, check=True)
    control_out = res_control.stdout
    assert "Package: m3tal" in control_out, "Package name is not 'm3tal'"
    assert "Version: 1.1.62" in control_out, "Package version is not 1.1.62"
    assert "Architecture: amd64" in control_out, "Architecture is not amd64"

    res_contents = subprocess.run(["dpkg-deb", "-c", DEB_PATH], capture_output=True, text=True, check=True)
    contents = res_contents.stdout
    assert "./usr/bin/m3tal" in contents, "Missing /usr/bin/m3tal binary"
    assert "./usr/bin/m3tal-api" in contents, "Missing /usr/bin/m3tal-api binary"
    assert "./lib/systemd/system/m3tal.service" in contents, "Missing m3tal.service"
    assert "./lib/systemd/system/m3tal-api.service" in contents, "Missing m3tal-api.service"
    assert "./etc/m3tal/.env.example" in contents, "Missing /etc/m3tal/.env.example"
    assert "./usr/share/applications/m3tal.desktop" in contents, "Missing desktop entry"
    assert "./usr/share/icons/hicolor/scalable/apps/m3tal.svg" in contents, "Missing scalable SVG icon"

    # Extract control scripts and verify postinst / postrm logic
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(["dpkg-deb", "-e", DEB_PATH, tmpdir], check=True)
        postinst = open(os.path.join(tmpdir, "postinst"), "r").read()
        postrm = open(os.path.join(tmpdir, "postrm"), "r").read()

        # Check postinst hooks
        assert "/etc/m3tal" in postinst, "postinst missing /etc/m3tal creation"
        assert "groupadd -r m3tal" in postinst, "postinst missing m3tal group creation"
        assert "systemctl daemon-reload" in postinst, "postinst missing systemctl daemon-reload"
        assert "m3tal-api.service" in postinst, "postinst missing m3tal-api.service enable/restart"
        assert "m3tal.service" in postinst, "postinst missing m3tal.service enable/restart"
        assert "ln -s /opt/m3tal/stack /docker" in postinst, "postinst missing /docker symlink logic"

        # Check postrm hooks
        assert "systemctl stop" in postrm, "postrm missing service stop logic"
        assert 'if [ "$1" = "purge" ]' in postrm, "postrm missing purge handling"
        assert "rm /docker" in postrm, "postrm missing /docker symlink removal"

    print("    [OK] m3tal-core deb package, binaries, services, and hooks verified.")

def check_spec_deliverables():
    print_step("2. Verifying Track 5 specification deliverables (Phases 11, 12, 13)...")
    docs_dir = os.path.join(HUB_ROOT, "docs", "packaging")
    spec_11 = os.path.join(docs_dir, "11-m3tal-core-spec.md")
    spec_12 = os.path.join(docs_dir, "12-app-installation-standard.md")
    spec_13 = os.path.join(docs_dir, "13-m3tal-hub-integration.md")

    for f in [spec_11, spec_12, spec_13]:
        assert os.path.exists(f), f"Specification deliverable missing: {f}"
        content = open(f, "r").read()
        assert len(content) > 1000, f"Specification {f} is suspiciously short"

    content_11 = open(spec_11, "r").read()
    assert "Bootstrap & Repository Isolation" in content_11
    assert "Systemd Service Units Specification" in content_11
    assert "Standard Filesystem Layout" in content_11

    content_12 = open(spec_12, "r").read()
    assert "sudo apt install m3tal-<app-name>" in content_12
    assert "Package Naming Standards" in content_12
    assert "Standard Filesystem Hierarchy (FHS Compliance)" in content_12

    content_13 = open(spec_13, "r").read()
    assert "Architectural Role & Boundary Separation" in content_13
    assert "Integrated Hub Interfaces" in content_13

    # Verify plan files in m3tal-apt-key/plan
    plan_dir = os.path.join(HUB_ROOT, "m3tal-apt-key", "plan")
    for phase_file in ["11-m3tal-core.md", "12-app-installation-standard.md", "13-m3tal-hub-integration.md"]:
        plan_path = os.path.join(plan_dir, phase_file)
        assert os.path.exists(plan_path), f"Plan file missing: {plan_path}"
        plan_content = open(plan_path, "r").read()
        assert "**Status**: Completed" in plan_content or "Status: Completed" in plan_content, f"Plan {phase_file} not marked Completed"
        assert "Tasks Executed" in plan_content, f"Plan {phase_file} missing Tasks Executed"
        assert "Deliverables" in plan_content, f"Plan {phase_file} missing Deliverables"
        assert "Completion Criteria Verification" in plan_content, f"Plan {phase_file} missing Criteria Verification"

    # Verify docs in m3tal-apt-key/docs match docs/packaging
    apt_docs_dir = os.path.join(HUB_ROOT, "m3tal-apt-key", "docs")
    for doc_file in ["11-m3tal-core-spec.md", "12-app-installation-standard.md", "13-m3tal-hub-integration.md"]:
        apt_doc_path = os.path.join(apt_docs_dir, doc_file)
        assert os.path.exists(apt_doc_path), f"m3tal-apt-key/docs missing {doc_file}"
        packaging_doc_path = os.path.join(docs_dir, doc_file)
        assert open(apt_doc_path).read() == open(packaging_doc_path).read(), f"Content mismatch between {apt_doc_path} and {packaging_doc_path}"

    print("    [OK] All Phase 11, 12, and 13 specification documents and plan files verified.")

def check_hub_integration_files():
    print_step("3. Verifying M3tal Hub integration pages (Phase 13)...")
    core_page = os.path.join(HUB_ROOT, "apps", "m3tal-core.html")
    apt_key_page = os.path.join(HUB_ROOT, "apps", "m3tal-apt-key.html")
    index_page = os.path.join(HUB_ROOT, "index.html")

    assert os.path.exists(core_page), f"m3tal-core.html missing at {core_page}"
    assert os.path.exists(apt_key_page), f"m3tal-apt-key.html missing at {apt_key_page}"
    assert os.path.exists(index_page), f"index.html missing at {index_page}"

    # Verify m3tal-core.html
    core_html = open(core_page, "r").read()
    assert "sudo apt install -y m3tal" in core_html, "m3tal-core.html missing apt install command"
    assert "curl -fsSL https://jakej985-rgb.github.io/m3tal-apt-key/install.sh" in core_html, "m3tal-core.html missing repo setup bootstrap"
    assert "systemctl status m3tal.service" in core_html, "m3tal-core.html missing systemctl service status"
    assert "m3tal help" in core_html, "m3tal-core.html missing m3tal help command"
    assert "v1.1.62" in core_html, "m3tal-core.html missing v1.1.62 changelog entry"

    # Verify m3tal-apt-key.html
    key_html = open(apt_key_page, "r").read()
    assert "curl -fsSL https://jakej985-rgb.github.io/m3tal-apt-key/install.sh | sudo bash" in key_html, "m3tal-apt-key.html missing universal bootstrap command"
    assert "signed-by=/etc/apt/keyrings/m3tal-archive-keyring.gpg" in key_html, "m3tal-apt-key.html missing signed-by repository entry"
    assert "B95A 45C6 4757 7DEB CC87  7C49 AF61 90B0 C013 46DD" in key_html, "m3tal-apt-key.html missing GPG fingerprint verification"

    # Verify index.html
    index_html = open(index_page, "r").read()
    assert "Official M3tal Debian/APT Repository" in index_html, "index.html missing APT repo banner"
    assert "curl -fsSL https://jakej985-rgb.github.io/m3tal-apt-key/install.sh | sudo bash" in index_html, "index.html missing bootstrap command in banner"
    assert 'href="./apps/m3tal-apt-key.html"' in index_html, "index.html banner missing link to m3tal-apt-key.html"
    assert 'href="./apps/m3tal-core.html"' in index_html, "index.html missing link to m3tal-core.html"

    print("    [OK] Hub pages (m3tal-core.html, m3tal-apt-key.html, index.html) verified.")

def run_hub_test_suite():
    print_step("4. Running full M3tal-Hub verification test suite...")
    test_script = os.path.join(HUB_ROOT, "scripts", "test_hub_verification.py")
    res = subprocess.run([sys.executable, test_script], capture_output=True, text=True)
    if res.returncode != 0:
        print("ERROR: test_hub_verification.py failed:\n", res.stderr)
        sys.exit(1)
    print("    [OK] Full Hub verification test suite passed with 0 regressions.")

def main():
    print("==================================================")
    print(" Track 5 Packaging, Standards & Hub Verification  ")
    print("==================================================")
    check_deb_packaging()
    check_spec_deliverables()
    check_hub_integration_files()
    run_hub_test_suite()
    print("==================================================")
    print(" ✅ All Track 5 Verification Checks PASSED!       ")
    print("==================================================")

if __name__ == "__main__":
    main()
