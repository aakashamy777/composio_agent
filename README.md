# Composio Agent Research & Dashboard

AI research agent pipeline profiling the integration surface area of 100 applications across 10 categories to assess their buildability as agent toolkits.

## Key Insights (from Dashboard)

* **90% Buildable Today:** 90% of the researched apps can be integrated as agent toolkits today (including 56% already supported in the Composio registry).
* **61% Self-Serve:** Most tools offer self-serve access, free sandboxes, or instant API key generation.
* **12% Gated:** Access is restricted behind paid plans, partner approvals, or sales contact.
* **Normalized Auth:** Compressed 70+ messy raw auth method variations into 6 clean buckets (OAuth2, API Key, Bearer Token, Basic Auth, JWT, None).

## How to Run It

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the root directory and add your API keys:
   ```env
   COMPOSIO_API_KEY=your_composio_api_key
   GOOGLE_API_KEY=your_gemini_api_key
   ```

3. Run the research agent:
   ```bash
   python research_agent.py
   ```

4. If any calls failed or hit rate limits, you can retry them with:
   ```bash
   python retry_failed.py
   ```

## The Pipeline & Dashboard

1. **Stage 1 (Registry Lookup):** Queries Composio's SDK registry for native toolkits (56 apps matched).
2. **Stage 2 (Gemini Fallback):** Researches live documentation for remaining apps via Gemini with Google Search grounding (21 apps).
3. **Stage 3 (Auto-Retry):** Handles rate-limiting and parse failures using exponential backoff (21 recovered).
4. **Stage 4 (Verification Loop):** Evaluates a 15-app random sample against live docs to guarantee accuracy.

To view, filter, and search the findings, open **`index.html`** in any web browser.
