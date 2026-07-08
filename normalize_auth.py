"""Normalize the messy auth_method_distribution from patterns.json into clean buckets."""
import json
from collections import Counter

with open("output/patterns.json") as f:
    patterns = json.load(f)

raw = patterns["auth_method_distribution"]

buckets = Counter()
for method, count in raw.items():
    m = method.upper()
    if "OAUTH" in m or "OIDC" in m:
        buckets["OAuth2"] += count
    elif "API KEY" in m or "API TOKEN" in m or "TOKEN-BASED" in m:
        buckets["API Key"] += count
    elif "BEARER" in m:
        buckets["Bearer Token"] += count
    elif "BASIC" in m or "DIGEST" in m or "LOGIN CREDENTIALS" in m or "USERNAME AND PASSWORD" in m:
        buckets["Basic Auth"] += count
    elif "JWT" in m or "SIGNED JWT" in m or "JSON WEB TOKEN" in m:
        buckets["JWT"] += count
    elif "NONE" in m or "CLI TOOL" in m:
        buckets["None (local/CLI tool)"] += count
    else:
        buckets["Other / Proprietary"] += count

print(json.dumps(dict(buckets.most_common()), indent=2))

patterns["auth_method_distribution_normalized"] = dict(buckets.most_common())
with open("output/patterns.json", "w") as f:
    json.dump(patterns, f, indent=2)
print("\nSaved normalized buckets into patterns.json")