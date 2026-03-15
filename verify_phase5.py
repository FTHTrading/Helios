"""
Verify Phase 5: Sovereign Design System v1
"""
import os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
passed = 0
failed = 0

def check(desc, condition):
    global passed, failed
    if condition:
        print(f"  [PASS] {desc}")
        passed += 1
    else:
        print(f"  [FAIL] {desc}")
        failed += 1

print("\n=== Phase 5: Sovereign Design System v1 Verification ===\n")

# 1. Master Spec doc
print("1. Master Design System Spec")
spec = os.path.join(BASE, "docs", "MASTER_DESIGN_SYSTEM_V1.md")
check("Spec document exists", os.path.isfile(spec))
with open(spec, "r", encoding="utf-8") as f:
    content = f.read()
check("Contains Design DNA laws", "Design DNA" in content)
check("Contains 5 brand themes", "xxxiii" in content and "NIL33" in content and "Y3K" in content and "UnyKorn" in content and "Helios" in content)
check("Contains token architecture", "--sv-accent-1" in content)
check("Contains component families", "Hero Core" in content and "Proof Strip" in content)
check("Contains device adaptations", "Watch" in content and "Glasses" in content)
check("Contains prompt templates", "Prompt Templates" in content)

# 2. Sovereign CSS
print("\n2. Sovereign Token System CSS")
sov = os.path.join(BASE, "static", "css", "sovereign.css")
check("sovereign.css exists", os.path.isfile(sov))
with open(sov, "r", encoding="utf-8") as f:
    css = f.read()
check("Contains --sv-bg token", "--sv-bg:" in css)
check("Contains --sv-accent-1 token", "--sv-accent-1:" in css)
check("Contains --sv-speed-hover token", "--sv-speed-hover:" in css)
check("Contains --sv-font-ui token", "--sv-font-ui:" in css)
check("Contains --sv-max-width token", "--sv-max-width:" in css)
check("Contains .sv-nav component", ".sv-nav {" in css or ".sv-nav{" in css)
check("Contains .sv-hero component", ".sv-hero {" in css or ".sv-hero{" in css)
check("Contains .sv-card component", ".sv-card {" in css or ".sv-card{" in css)
check("Contains .sv-btn component", ".sv-btn {" in css or ".sv-btn{" in css)
check("Contains .sv-proof-strip component", ".sv-proof-strip {" in css or ".sv-proof-strip{" in css)
check("Contains .sv-metric component", ".sv-metric {" in css or ".sv-metric{" in css)
check("Contains .sv-status-pill component", ".sv-status-pill {" in css or ".sv-status-pill{" in css)
check("Contains .sv-dock component", ".sv-dock {" in css or ".sv-dock{" in css)
check("Contains .sv-rail component", ".sv-rail {" in css or ".sv-rail{" in css)
check("Contains .sv-constellation component", ".sv-constellation {" in css or ".sv-constellation{" in css)
check("Contains .sv-fab component", ".sv-fab {" in css or ".sv-fab{" in css)
check("Contains .sv-footer component", ".sv-footer {" in css or ".sv-footer{" in css)
check("Contains .sv-badge component", ".sv-badge {" in css or ".sv-badge{" in css)
check("Contains watch media query", "max-width: 200px" in css)
css_size = len(css)
check(f"CSS size is substantial ({css_size} chars)", css_size > 5000)

# 3. Theme files
print("\n3. Brand Theme Files")
themes_dir = os.path.join(BASE, "static", "css", "themes")
check("themes/ directory exists", os.path.isdir(themes_dir))
for name in ["helios", "xxxiii", "nil33", "y3k", "unykorn"]:
    path = os.path.join(themes_dir, f"{name}.theme.css")
    check(f"{name}.theme.css exists", os.path.isfile(path))
    with open(path, "r", encoding="utf-8") as f:
        tc = f.read()
    check(f"{name}.theme.css has --sv-accent-1", "--sv-accent-1:" in tc)
    check(f"{name}.theme.css has --sv-bg", "--sv-bg:" in tc)
    check(f"{name}.theme.css has --sv-glow", "--sv-glow:" in tc)

# 4. base.html integration
print("\n4. base.html Integration")
base = os.path.join(BASE, "templates", "base.html")
with open(base, "r", encoding="utf-8") as f:
    html = f.read()
check("base.html loads sovereign.css", "sovereign.css" in html)
check("base.html loads brand theme", "brand_theme" in html)
check("base.html has body.sv class", 'class="sv"' in html)
check("base.html preserves helios.css", "helios.css" in html)

# 5. app.py context
print("\n5. App Context Processor")
app_py = os.path.join(BASE, "app.py")
with open(app_py, "r", encoding="utf-8") as f:
    app_content = f.read()
check("app.py provides brand_theme", "brand_theme" in app_content)

# 6. Flask server check
print("\n6. Server Smoke Test")
sys.path.insert(0, BASE)
try:
    from app import create_app
    test_app = create_app()
    client = test_app.test_client()
    resp = client.get("/")
    check(f"Homepage returns {resp.status_code}", resp.status_code == 200)
    page = resp.data.decode()
    check("Homepage includes sovereign.css link", "sovereign.css" in page)
    check("Homepage includes theme CSS link", ".theme.css" in page)
    check('Homepage has body class="sv"', 'class="sv"' in page)
except Exception as e:
    check(f"Server smoke test: {e}", False)

print(f"\n{'='*50}")
print(f"Phase 5 Results: {passed} passed, {failed} failed")
if failed == 0:
    print("ALL CHECKS PASSED — Sovereign Design System v1 verified.")
else:
    print(f"{failed} check(s) FAILED — review above.")
print(f"{'='*50}\n")
