"""
Helios OS — Static Site Export for Netlify
Freezes the Flask app into static HTML for deployment.
"""

import os
import sys
import shutil
import datetime
import re
import subprocess
from app import create_app

def freeze():
    """Export all page routes as static HTML files."""
    # Stamp each build so we can verify what's deployed.
    build_id = os.environ.get("HELIOS_BUILD_ID")
    if not build_id:
        ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        git_sha = "nogit"
        try:
            git_sha = (
                subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL)
                .decode("utf-8", errors="ignore")
                .strip()
            )
        except Exception:
            pass
        build_id = f"{ts}-{git_sha}"
        os.environ["HELIOS_BUILD_ID"] = build_id

    app = create_app()
    build_dir = os.path.join(os.path.dirname(__file__), "build")

    # Clean build directory
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir, exist_ok=True)

    # Page routes to freeze
    pages = [
        ("/", "index.html"),
        ("/dashboard", "dashboard/index.html"),
        ("/field", "field/index.html"),
        ("/network", "network/index.html"),
        ("/ask", "ask/index.html"),
        ("/guide", "guide/index.html"),
        ("/protocol", "protocol/index.html"),
        ("/status", "status/index.html"),
        ("/treasury", "treasury/index.html"),
        ("/vault", "vault/index.html"),
        ("/vault/gold", "vault/gold/index.html"),
        ("/activate", "activate/index.html"),
        ("/metrics", "metrics/index.html"),
        ("/earnings", "earnings/index.html"),
        ("/certificates", "certificates/index.html"),
        ("/opportunity", "opportunity/index.html"),
        ("/recruit", "recruit/index.html"),
        ("/enter", "enter/index.html"),
        ("/join", "join/index.html"),
        ("/qr", "qr/index.html"),
        # ═══ Founder QR Pages — personal share cards ═══
        ("/qr/elliot-a", "qr/elliot-a/index.html"),
        ("/qr/aaron-w", "qr/aaron-w/index.html"),
        ("/qr/ryan-a", "qr/ryan-a/index.html"),
        ("/qr/veunca-j", "qr/veunca-j/index.html"),
        ("/qr/nicholas-w", "qr/nicholas-w/index.html"),
        ("/qr/paul-w", "qr/paul-w/index.html"),
        ("/qr/eddie-m", "qr/eddie-m/index.html"),
        ("/qr/dan-morgan", "qr/dan-morgan/index.html"),
        ("/qr/neandria-p", "qr/neandria-p/index.html"),
        ("/qr/joseph-d", "qr/joseph-d/index.html"),
        ("/qr/brian-rawlston", "qr/brian-rawlston/index.html"),
        ("/qr/blyss-w", "qr/blyss-w/index.html"),
        ("/qr/nakia-r", "qr/nakia-r/index.html"),
        ("/launch", "launch/index.html"),
        ("/token-offering", "token-offering/index.html"),
        ("/tokenomics", "tokenomics/index.html"),
        ("/web3", "web3/index.html"),
        ("/health", "health/index.html"),
    ]

    with app.test_client() as client:
        for route, output_path in pages:
            try:
                response = client.get(route)
                if response.status_code == 200:
                    full_path = os.path.join(build_dir, output_path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, "wb") as f:
                        f.write(response.data)
                    print(f"  ✓ {route} → {output_path}")
                else:
                    print(f"  ✗ {route} → HTTP {response.status_code}")
            except Exception as e:
                print(f"  ✗ {route} → Error: {e}")

    # Persist build id for deploy/debug.
    try:
        with open(os.path.join(build_dir, "BUILD_ID.txt"), "w", encoding="utf-8") as f:
            f.write(build_id + "\n")
    except Exception as e:
        print(f"  ✗ BUILD_ID.txt → Error: {e}")

    # Validate frozen HTML to prevent production-only blank pages caused by malformed tags.
    # This specifically guards against the historical `rel=\"styleshee et\"` issue.
    html_files = []
    for root, _dirs, files in os.walk(build_dir):
        for name in files:
            if name.lower().endswith(".html"):
                html_files.append(os.path.join(root, name))

    bad_files = []
    # Only validate the actual Google Fonts stylesheet request, not preconnect.
    font_css_link_re = re.compile(
        r"<link\b[^>]*href=\"https://fonts\.googleapis\.com/(?:css2|css)[^\"]*\"[^>]*>",
        re.IGNORECASE,
    )
    rel_re = re.compile(r"\brel=\"([^\"]+)\"", re.IGNORECASE)
    for path in html_files:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                html = f.read()

            # Skip non-HTML outputs (e.g., frozen JSON endpoints like /health).
            head_sample = html[:1000].lower()
            if "<html" not in head_sample:
                continue

            if "rel=\"styleshee et\"" in html or "rel=\"styleshee%20et\"" in html:
                bad_files.append((path, "malformed rel attribute (styleshee et)"))
                continue

            for match in font_css_link_re.finditer(html):
                tag = match.group(0)
                m = rel_re.search(tag)
                rel_val = (m.group(1) if m else "").strip().lower()
                if "stylesheet" not in rel_val:
                    bad_files.append((path, f"fonts.googleapis.com stylesheet link missing rel=stylesheet (rel={rel_val or 'MISSING'})"))
                    break

            if "/static/css/helios.css" not in html:
                bad_files.append((path, "missing /static/css/helios.css link"))
        except Exception as e:
            bad_files.append((path, f"validator exception: {e}"))

    if bad_files:
        print("\n  ✗ Build validation failed:")
        for path, reason in bad_files[:30]:
            rel = os.path.relpath(path, build_dir)
            print(f"    - {rel}: {reason}")
        raise SystemExit("\nFreeze aborted due to invalid HTML output. Fix templates and re-run freeze.py")

    # Copy static assets
    static_src = os.path.join(os.path.dirname(__file__), "static")
    static_dst = os.path.join(build_dir, "static")
    if os.path.exists(static_src):
        shutil.copytree(static_src, static_dst, dirs_exist_ok=True)
        print(f"  ✓ Static assets copied")

    # Copy Netlify config files into build
    project_root = os.path.dirname(__file__)
    for netlify_file in ("_headers", "_redirects"):
        src = os.path.join(project_root, netlify_file)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(build_dir, netlify_file))
            print(f"  ✓ {netlify_file} copied to build")

    print(f"\n  ☀ Helios OS — Build complete: {build_dir}")
    print(f"  {len([p for p in pages])} pages frozen for Netlify deployment")
    print(f"  Build ID: {build_id}")


if __name__ == "__main__":
    freeze()
