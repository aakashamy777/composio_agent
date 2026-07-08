import json, random

with open("output/results.json") as f:
    results = json.load(f)

random.seed(42)  # fixed seed - reproducible, not cherry-picked
sample = random.sample(results, 15)

print(f"{'ID':<4}{'Name':<25}{'Source':<22}{'Auth (agent said)':<30}{'Self-serve/Gated (agent said)'}")
print("-" * 130)
for r in sample:
    auth = str(r.get("auth_methods", ""))[:28]
    serve = str(r.get("self_serve_or_gated", ""))[:50]
    print(f"{r['id']:<4}{r['name']:<25}{r.get('source',''):<22}{auth:<30}{serve}")
    print(f"     evidence: {r.get('evidence','')}")
    print()

with open("output/verification_sample.json", "w") as f:
    json.dump(sample, f, indent=2)
print("Saved 15-app sample to output/verification_sample.json")