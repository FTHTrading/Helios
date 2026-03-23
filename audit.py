"""
Helios OS — Full System Audit
Tests every route, API, template, and static asset.
"""
import os, sys, json, time

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("  ☀  HELIOS OS — FULL SYSTEM AUDIT")
print("=" * 70)

# ─── 1. CONFIG ────────────────────────────────────────────────────
print("\n[1] CONFIG VALIDATION")
try:
    from config import HeliosConfig
    HeliosConfig.validate()
    print("  ✓ Config loaded & validated")
    print(f"    Domain: {HeliosConfig.DOMAIN}")
    print(f"    DB: {HeliosConfig.DATABASE_URL}")
    print(f"    Port: {HeliosConfig.PORT}")
    print(f"    Token supply: {HeliosConfig.TOKEN_TOTAL_SUPPLY:,}")
except Exception as e:
    print(f"  ✗ Config FAILED: {e}")

# ─── 2. APP FACTORY ──────────────────────────────────────────────
print("\n[2] APP FACTORY")
try:
    from app import create_app
    app = create_app()
    print("  ✓ create_app() succeeded")
except Exception as e:
    print(f"  ✗ create_app() FAILED: {e}")
    sys.exit(1)

# ─── 3. ALL REGISTERED ROUTES ────────────────────────────────────
print("\n[3] REGISTERED ROUTES")
rules = sorted([r for r in app.url_map.iter_rules() if not r.rule.startswith('/static')], key=lambda r: r.rule)
for r in rules:
    methods = ','.join(sorted(r.methods - {'HEAD', 'OPTIONS'}))
    print(f"    {methods:6} {r.rule}")
print(f"  Total: {len(rules)} routes")

# ─── 4. PAGE ROUTES ──────────────────────────────────────────────
print("\n[4] PAGE ROUTES (GET → HTML)")
page_routes = [
    "/", "/dashboard", "/field", "/network", "/ask", "/protocol",
    "/status", "/treasury", "/vault", "/vault/gold", "/activate",
    "/metrics", "/enter", "/join", "/health"
]
ok = fail = 0
with app.test_client() as client:
    for route in page_routes:
        try:
            r = client.get(route)
            body = r.data.decode("utf-8", errors="replace")
            has_nav = "<nav" in body
            has_css = "helios.css" in body or route == "/health"
            has_fallback = "static-fallback.js" in body or route == "/health"
            size = len(r.data)
            issues = []
            if r.status_code != 200:
                issues.append(f"HTTP {r.status_code}")
            if not has_nav and route != "/health":
                issues.append("NO <nav>")
            if not has_css:
                issues.append("NO helios.css")
            if not has_fallback:
                issues.append("NO fallback.js")
            if 'styleshee et' in body:
                issues.append("BROKEN rel=stylesheet")

            if issues:
                print(f"  ⚠ {route:20} {size:>7}B  ISSUES: {', '.join(issues)}")
                fail += 1
            else:
                print(f"  ✓ {route:20} {size:>7}B  OK")
                ok += 1
        except Exception as e:
            print(f"  ✗ {route:20} ERROR: {e}")
            fail += 1

print(f"  Pages: {ok} OK, {fail} issues")

# ─── 5. API ROUTES ───────────────────────────────────────────────
print("\n[5] API ROUTES (GET → JSON)")
api_routes = [
    "/api/health",
    "/api/field/status",
    "/api/metrics/all",
    "/api/treasury/reserves",
    "/api/token/info",
    "/api/token/supply",
    "/api/token/verify",
    "/api/token/founder-lock",
    "/api/rewards/protocol",
    "/api/energy/conservation",
    "/api/infra/status",
    "/api/certificates/active",
]
ok = fail = 0
with app.test_client() as client:
    for route in api_routes:
        try:
            r = client.get(route)
            ct = r.headers.get("content-type", "")
            is_json = "json" in ct
            size = len(r.data)
            issues = []
            if r.status_code != 200:
                issues.append(f"HTTP {r.status_code}")
            if not is_json:
                issues.append(f"NOT JSON ({ct})")
            else:
                try:
                    data = json.loads(r.data)
                except:
                    issues.append("INVALID JSON")

            if issues:
                print(f"  ⚠ {route:35} {size:>7}B  {', '.join(issues)}")
                fail += 1
            else:
                print(f"  ✓ {route:35} {size:>7}B  OK")
                ok += 1
        except Exception as e:
            print(f"  ✗ {route:35} ERROR: {e}")
            fail += 1

print(f"  APIs: {ok} OK, {fail} issues")

# ─── 6. STATIC ASSETS ────────────────────────────────────────────
print("\n[6] STATIC ASSETS")
required_static = [
    "static/css/helios.css",
    "static/js/static-fallback.js",
    "static/js/network-viz.js",
]
for f in required_static:
    path = os.path.join(os.path.dirname(__file__), f)
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"  ✓ {f:40} {size:>7}B")
    else:
        print(f"  ✗ {f:40} MISSING!")

# ─── 7. TEMPLATES ────────────────────────────────────────────────
print("\n[7] TEMPLATES")
template_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = sorted(os.listdir(template_dir))
for t in templates:
    path = os.path.join(template_dir, t)
    if os.path.isfile(path):
        size = os.path.getsize(path)
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            content = fh.read()
        issues = []
        if "styleshee et" in content:
            issues.append("BROKEN rel=stylesheet")
        if t != "base.html" and "{% extends" not in content and "{% block" not in content and "<html" not in content:
            issues.append("NOT A TEMPLATE?")
        status = f"  ISSUES: {', '.join(issues)}" if issues else ""
        print(f"  {'✗' if issues else '✓'} {t:25} {size:>7}B{status}")

# ─── 8. MODELS ───────────────────────────────────────────────────
print("\n[8] MODELS (import check)")
model_dir = os.path.join(os.path.dirname(__file__), "models")
model_files = [f[:-3] for f in os.listdir(model_dir) if f.endswith(".py") and f != "__init__.py"]
for m in sorted(model_files):
    try:
        __import__(f"models.{m}")
        print(f"  ✓ models.{m}")
    except Exception as e:
        print(f"  ✗ models.{m}: {e}")

# ─── 9. CORE MODULES ─────────────────────────────────────────────
print("\n[9] CORE MODULES (import check)")
core_dir = os.path.join(os.path.dirname(__file__), "core")
core_files = [f[:-3] for f in os.listdir(core_dir) if f.endswith(".py") and f != "__init__.py"]
for m in sorted(core_files):
    try:
        __import__(f"core.{m}")
        print(f"  ✓ core.{m}")
    except Exception as e:
        print(f"  ✗ core.{m}: {e}")

# ─── 10. FREEZE PIPELINE ─────────────────────────────────────────
print("\n[10] FREEZE PIPELINE")
try:
    from freeze import freeze
    print("  ✓ freeze.py imports OK")
except Exception as e:
    print(f"  ✗ freeze.py import FAILED: {e}")

# Check build dir
build_dir = os.path.join(os.path.dirname(__file__), "build")
if os.path.exists(build_dir):
    html_count = sum(1 for r, d, f in os.walk(build_dir) for name in f if name.endswith('.html'))
    static_exists = os.path.exists(os.path.join(build_dir, "static"))
    bid_path = os.path.join(build_dir, "BUILD_ID.txt")
    bid = open(bid_path).read().strip() if os.path.exists(bid_path) else "NONE"
    print(f"  ✓ build/ exists: {html_count} HTML files, static={'YES' if static_exists else 'NO'}, BUILD_ID={bid}")
else:
    print("  ⚠ No build/ directory — run freeze.py")

# ─── 11. NETLIFY CONFIG ──────────────────────────────────────────
print("\n[11] NETLIFY CONFIG")
toml_path = os.path.join(os.path.dirname(__file__), "netlify.toml")
if os.path.exists(toml_path):
    with open(toml_path, "r") as f:
        toml = f.read()
    issues = []
    if 'publish = "build"' not in toml:
        issues.append("publish dir not 'build'")
    if "skip_processing = true" not in toml:
        issues.append("post-processing not disabled")
    if 'rel="styleshee' in toml:
        issues.append("broken stylesheet in toml?!")
    if "/* → /index.html" in toml or "/*  /index.html" in toml:
        issues.append("SPA catch-all still present")
    csp_line = [l for l in toml.split('\n') if 'Content-Security-Policy' in l]
    if csp_line:
        csp = csp_line[0]
        if "'unsafe-inline'" not in csp:
            issues.append("CSP missing 'unsafe-inline' for scripts or styles")
        if "d3js.org" not in csp:
            issues.append("CSP missing d3js.org")
    if issues:
        for i in issues:
            print(f"  ⚠ {i}")
    else:
        print("  ✓ netlify.toml looks correct")
else:
    print("  ✗ No netlify.toml!")

# ─── 12. .ENV ────────────────────────────────────────────────────
print("\n[12] ENVIRONMENT")
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, encoding="utf-8", errors="replace") as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    print(f"  ✓ .env exists with {len(lines)} keys")
    keys_present = [l.split('=')[0] for l in lines]
    for k in keys_present:
        print(f"    {k}")
else:
    print("  ⚠ No .env file")

# ─── SUMMARY ─────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  AUDIT COMPLETE")
print("=" * 70)
