"""Cluster results.json into patterns: auth distribution, self-serve vs gated, category breakdown, blockers."""
import json
from collections import Counter, defaultdict

with open("output/results.json") as f:
    results = json.load(f)

# --- Auth method distribution ---
auth_counter = Counter()
for r in results:
    methods = r.get("auth_methods", [])
    if isinstance(methods, str):
        methods = [methods]
    for m in methods:
        m_norm = str(m).upper().replace("OAUTH2", "OAuth2").replace("API_KEY", "API Key").replace("API KEY", "API Key")
        auth_counter[m_norm] += 1

# --- Self-serve vs gated ---
serve_counter = Counter()
for r in results:
    s = str(r.get("self_serve_or_gated", "")).lower()
    if "self-serve" in s or "self serve" in s:
        serve_counter["Self-serve"] += 1
    elif "gated" in s or "partner" in s or "contact sales" in s or "paid" in s:
        serve_counter["Gated"] += 1
    else:
        serve_counter["Unclear"] += 1

# --- By category: self-serve vs gated ---
cat_serve = defaultdict(lambda: Counter())
for r in results:
    cat = r.get("category_given", "Unknown")
    s = str(r.get("self_serve_or_gated", "")).lower()
    if "self-serve" in s or "self serve" in s:
        cat_serve[cat]["Self-serve"] += 1
    elif "gated" in s or "partner" in s or "contact sales" in s or "paid" in s:
        cat_serve[cat]["Gated"] += 1
    else:
        cat_serve[cat]["Unclear"] += 1

# --- Buildability verdict ---
verdict_counter = Counter()
for r in results:
    v = str(r.get("buildability_verdict", "")).lower()
    if v.startswith("buildable") or "yes" in v[:20]:
        verdict_counter["Buildable today"] += 1
    elif "not" in v[:20] or "no" in v[:10]:
        verdict_counter["Not buildable / blocked"] += 1
    else:
        verdict_counter["Partial / unclear"] += 1

# --- Source breakdown ---
source_counter = Counter(r.get("source", "unknown") for r in results)

# --- Common blocker keywords (from gated/verdict text) ---
blocker_keywords = Counter()
keywords = ["contact sales", "partner", "paid plan", "no public api", "no api", "closed platform",
            "enterprise", "approval", "waitlist", "invite", "cli tool", "no auth"]
for r in results:
    text = (str(r.get("self_serve_or_gated", "")) + " " + str(r.get("buildability_verdict", ""))).lower()
    for kw in keywords:
        if kw in text:
            blocker_keywords[kw] += 1

output = {
    "total_apps": len(results),
    "source_breakdown": dict(source_counter),
    "auth_method_distribution": dict(auth_counter.most_common()),
    "self_serve_vs_gated": dict(serve_counter),
    "category_self_serve_vs_gated": {k: dict(v) for k, v in cat_serve.items()},
    "buildability_verdict_summary": dict(verdict_counter),
    "common_blocker_keywords": dict(blocker_keywords.most_common()),
}

with open("output/patterns.json", "w") as f:
    json.dump(output, f, indent=2)

print(json.dumps(output, indent=2))