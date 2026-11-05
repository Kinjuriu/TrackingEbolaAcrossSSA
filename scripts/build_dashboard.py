# Rebuilds docs/dashboard.html from scripts/dashboard_template.html, keeping the data that is
# already inline in docs/dashboard.html (the "const DATA = ..., DEFAULTS = ...;" line).
# Run from anywhere: python3 scripts/build_dashboard.py
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(ROOT, "docs", "dashboard.html")
cur = open(out, encoding="utf-8").read()
i = cur.index("const DATA"); line = cur[i:cur.index("\n", i)]
assert "DEFAULTS" in line
tpl = open(os.path.join(ROOT, "scripts", "dashboard_template.html"), encoding="utf-8").read()
open(out, "w", encoding="utf-8").write(tpl.replace("__DATALINE__", line))
print("wrote docs/dashboard.html")
