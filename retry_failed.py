"""Retry only the apps that failed (error field present) in results.json, with backoff."""
import json, time, re
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
gclient = genai.Client()

with open("output/results.json") as f:
    results = json.load(f)

failed_ids = [r["id"] for r in results if "error" in r]
print(f"Retrying {len(failed_ids)} failed apps: {failed_ids}")

def research(app):
    prompt = f"""Research the app "{app['name']}" (hint: {app['hint']}) for building an AI agent toolkit.
Search their developer docs and answer ONLY with this exact JSON (no markdown fences, no extra text, ensure valid JSON with properly escaped quotes):
{{
  "category": "one line what it does",
  "auth_methods": ["OAuth2 or API key or Basic or token etc"],
  "self_serve_or_gated": "self-serve (free/trial signup) or gated (paid plan/partner/contact sales) - explain briefly",
  "api_surface": "REST/GraphQL, roughly how broad, any existing MCP server",
  "buildability_verdict": "could this be an agent toolkit today - yes/no/partial and the main blocker if not",
  "evidence": "the actual docs URL you found"
}}"""
    resp = gclient.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0,
        ),
    )
    text = re.sub(r'^```json\s*|\s*```$', '', resp.text.strip())
    return json.loads(text)

for rid in failed_ids:
    idx = next(i for i, r in enumerate(results) if r["id"] == rid)
    app = {"name": results[idx]["name"], "hint": results[idx]["hint"]}
    print(f"Retrying [{rid}] {app['name']}...", end=" ")

    for attempt in range(4):
        try:
            data = research(app)
            data["source"] = "gemini_research_retry"
            results[idx].pop("error", None)
            results[idx].update(data)
            print(f"✓ (attempt {attempt+1})")
            break
        except Exception as e:
            wait = 10 * (attempt + 1)
            print(f"✗ attempt {attempt+1} failed ({str(e)[:50]}), waiting {wait}s...")
            time.sleep(wait)
    else:
        print(f"  gave up on {app['name']} after 4 attempts")

    with open("output/results.json", "w") as f:
        json.dump(results, f, indent=2)
    time.sleep(3)  # spacing between calls to avoid re-triggering rate limit

still_failed = [r["name"] for r in results if "error" in r]
print(f"\nDone. Still failing: {still_failed if still_failed else 'none'}")