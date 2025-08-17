Creative Agent (Streamlit + Gemini)

A Riyadh/KSA–aware creative brainstorming app powered by Google Gemini.

Run locally

1. Python 3.11 recommended. Create venv and install deps:
   ```bash
   py -m venv .venv
   .\\.venv\\Scripts\\Activate.ps1   # Windows PowerShell
   pip install -r requirements.txt
   ```
2. Set your Gemini API key (either name works):
   ```powershell
   $env:GEMINI_API_KEY="YOUR_KEY"
   # or
   $env:GOOGLE_API_KEY="YOUR_KEY"
   ```
3. Start the app:
   ```powershell
   python -m streamlit run app.py
   ```

Deploy on Streamlit Cloud

1. Push this folder as a GitHub repo. Ensure these files exist at the repo root:
   - app.py
   - requirements.txt
2. In Streamlit Cloud:
   - New app → Connect your GitHub repo
   - Branch: main (or your branch)
   - Main file path: app.py
3. Set Secrets (Settings → Secrets):
   ```toml
   GEMINI_API_KEY = "YOUR_PRODUCTION_KEY"
   ```
   The app also accepts GOOGLE_API_KEY if you prefer that name.
4. Deploy.

Environment & notes

- Each chain step uses strict JSON I/O and a system message: "Think privately but never reveal reasoning. Output only JSON or final formatted text."
- Default audience is Riyadh, Saudi Arabia when not provided.
- The app adds dynamic date/season context for KSA (weekend Fri–Sat, seasonal hints).
- Final Presenter renders friendly copy with a blockquoted 30s script, plus captions and CTA.

Troubleshooting

- Import errors in IDE: Select the same interpreter you used for the venv.
- API errors: Verify your key is present in Secrets/ENV and billing/quota is enabled.
- Mismatched language: English selected → the chain runs a strict polish (no translation).

Files

- app.py – Streamlit app with the full multi-step chain
- requirements.txt – Python dependencies


