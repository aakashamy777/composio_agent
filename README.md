# Composio Agent Research

AI research agent for Composio product intern assignment.

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
