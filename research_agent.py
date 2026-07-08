"""
Composio assignment - research agent
For each app: try Composio's own toolkit registry first (fast, structured, ground truth).
If not found there, fall back to Gemini w/ Google Search grounding to research the docs URL.
"""
import json, os, time, re
from dotenv import load_dotenv
from composio import Composio
from google import genai
from google.genai import types

load_dotenv()

composio = Composio()
gclient = genai.Client()

with open("apps.json") as f:
    apps = json.load(f)

os.makedirs("output", exist_ok=True)
results = []

def slugify(name):
    return re.sub(r'[^a-z0-9]+', '', name.lower())

def from_composio(app):
    """Try Composio's own toolkit registry - ground truth if it exists."""
    candidates = [slugify(app["name"]), app["name"].lower().replace(" ", "_"), app["name"].lower().split()[0]]
    for slug in candidates:
        try:
            tk = composio.toolkits.get(slug=slug)
            auth_modes = list(set(a.mode for a in (tk.auth_config_details or [])))
            return {
                "source": "composio_registry",
                "category": tk.meta.categories[0].name if tk.meta and tk.meta.categories else app["category"],
                "description": tk.meta.description if tk.meta else "",
                "auth_methods": auth_modes or tk.composio_managed_auth_schemes,
                "self_serve_or_gated": "self-serve (composio-managed OAuth/API key)" if tk.composio_managed_auth_schemes else "unknown - check docs",
                "api_surface": f"{tk.meta.tools_count} tools available via Composio" if tk.meta else "unknown",
                "buildability_verdict": "Buildable today - already in Composio's toolkit registry",
                "evidence": tk.meta.app_url if tk.meta else app["hint"],
            }
        except Exception:
            continue
    return None

def from_gemini_research(app):
    """Fallback: ask Gemini w/ search grounding to research the app's docs."""
    prompt = f"""Research the app "{app['name']}" (hint: {app['hint']}) for building an AI agent toolkit.
Search their developer docs and answer ONLY with this exact JSON (no markdown fences, no extra text):
{{
  "category": "one line what it does",
  "auth_methods": ["OAuth2 or API key or Basic or token etc"],
  "self_serve_or_gated": "self-serve (free/trial signup) or gated (paid plan/partner/contact sales) - explain briefly",
  "api_surface": "REST/GraphQL, roughly how broad, any existing MCP server",
  "buildability_verdict": "could this be an agent toolkit today - yes/no/partial and the main blocker if not",
  "evidence": "the actual docs URL you found"
}}"""
    try:
        resp = gclient.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0,
            ),
        )
        text = resp.text.strip()
        text = re.sub(r'^```json\s*|\s*```$', '', text.strip())
        data = json.loads(text)
        data["source"] = "gemini_research"
        return data
    except Exception as e:
        return {"source": "gemini_research", "error": str(e)}

for app in apps:
    print(f"[{app['id']}/100] {app['name']}...", end=" ")
    entry = {"id": app["id"], "name": app["name"], "hint": app["hint"], "category_given": app["category"]}

    composio_result = from_composio(app)
    if composio_result:
        entry.update(composio_result)
        print("✓ composio registry")
    else:
        gemini_result = from_gemini_research(app)
        entry.update(gemini_result)
        print("✓ gemini research" if "error" not in gemini_result else f"✗ error: {gemini_result['error'][:60]}")
        time.sleep(1)  # be nice to rate limits

    results.append(entry)

    # save incrementally so a crash doesn't lose progress
    with open("output/results.json", "w") as f:
        json.dump(results, f, indent=2)

print(f"\nDone. {len(results)} apps processed. Saved to output/results.json")
composio_count = sum(1 for r in results if r.get("source") == "composio_registry")
gemini_count = sum(1 for r in results if r.get("source") == "gemini_research")
print(f"From Composio registry: {composio_count} | From Gemini research: {gemini_count}")