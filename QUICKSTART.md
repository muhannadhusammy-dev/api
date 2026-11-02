# TajerOS — Start here

This download contains two working applications:

1. **Business workspace:** React + ASP.NET Core + Python AI. Purchases, sales, inventory, approvals, returns, OCR, document evidence and operational health. Uses a local SQLite database by default.
2. **Sales intelligence:** Python/Streamlit. Historical sales analysis, CSV upload, store comparisons, ML forecasts and an optional OpenAI advisor.

## Windows

Install **Python 3.12**, **.NET 10 SDK**, **Node.js 22 or newer**, **Tesseract OCR** and **FFmpeg**. Ensure their commands are on PATH. Extract the ZIP to a normal folder before running anything.

Open PowerShell in the extracted `TajerOS` folder:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
powershell -ExecutionPolicy Bypass -File scripts/start.ps1
```

The `Bypass` flag applies only to that local script process. Read scripts before running them. Setup reports any missing prerequisite. The Windows launcher is provided but was not executed in the Linux validation environment.

Open `http://127.0.0.1:5082` in your browser.

To run just the sales dashboard after setup, open a second PowerShell:

```powershell
.venv\Scripts\python.exe -m streamlit run llm_streamlit/app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

## Linux / macOS

Install the same prerequisites. On Debian/Ubuntu, the OCR/audio packages are `tesseract-ocr` and `ffmpeg`; install the .NET 10 SDK using Microsoft's instructions.

```bash
bash scripts/setup.sh
bash scripts/start.sh
# In another terminal, if you also want sales intelligence:
bash scripts/dashboard.sh
```

Business workspace: port **5082**. Sales dashboard: port **8501**. AI service: port **8091**. Ctrl+C stops the processes started by the business launcher.

## Sign in

- Owner: `owner@tajer.local`
- Staff: `staff@tajer.local`
- Local demo password for both: `TajerDemo!2026`

Owner approves changes; staff can submit proposals. These are demonstration accounts. To select a different demo password, export `DEMO_PASSWORD` **before the first database creation**. Later changes to that variable do not replace existing stored password hashes. Do not delete a real database to change a password.

## Five-minute business demonstration

1. Upload `data/demo_receipt.png` in Receipts. OCR should extract **50 cartons**, total **EGP 12,000**. Review, create proposal, and approve as owner.
2. In Assistant enter `بعت 15 كرتونة زيت`. A sale proposal appears; no stock changes until approval. Supply selling total **4,500**, save, then approve.
3. Inventory shows **35 oil cartons**. Gross profit is **900** before expenses/tax.
4. Propose and activate a returns workflow; return **2 cartons** against that sale and approve. Stock becomes **37**, net revenue **3,900**, gross profit **780**.
5. Ask `ما هي سياسة المرتجعات؟` in Knowledge. Show source citations.

Use a fresh demonstration database for those exact balances. Automated tests use a temporary database instead of your demonstration data.

## Sales dashboard demonstration

Open Dashboard, choose a store, then Forecast. Compare Ridge, Random Forest and seasonal repeat by chronological holdout MAE. Download forecast CSV. The included 6,435 records cover 45 stores in 2010–2012; this is historical US retail data. A currency label does not convert money. Missing weeks disable forecasts; monetary sales cannot determine reorder quantities by themselves.

## Optional LLM and voice

Dashboard/forecasting/OCR/text commands/cited document excerpts work **without paid credentials**.

- Streamlit advisor: create `llm_streamlit/.env` from its `.env.example` and set your own `OPENAI_API_KEY` securely. Do not commit it. `OPENAI_MODEL` defaults to `gpt-4.1-mini`. Aggregated facts are sent to OpenAI only when a question is submitted.
- Document generation: export `LLM_API_KEY`, `LLM_MODEL` and optionally `LLM_BASE_URL` before starting the AI service. Otherwise it returns source excerpts.
- Speech: run `.venv/bin/python scripts/download_optional_models.py --voice` (Windows: `.venv\Scripts\python.exe ...`). This downloads substantial external weights and verifies their recorded hashes. Internet access to Hugging Face and its asset hosts is needed.

External LLM calls and speech inference were not validated in this delivery because no API key or speech weights were supplied. Their disabled/unavailable states are intentional and disclosed. See `docs/VALIDATION.md`.

## Tests

After setup, install developer dependencies with the virtual environment's Python:

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest tests/test_dashboard.py -q
PATH="$PWD/.venv/bin:$PATH" bash tests/run.sh
```

Stop your own local stack before the integration suite; tests own ports 5082 and 8091 and create a temporary database. `tests/browser_smoke.py` requires both applications running plus Chromium. It accepts `CHROMIUM_PATH`; defaults to `/usr/bin/chromium` on Linux.

## Presentation and documentation

- `docs/TajerOS_Final_Presentation.pptx`: editable final slide deck with speaker notes.
- `docs/Study_Guide.html`: original detailed explanation and defense questions.
- `docs/VALIDATION.md`: current delivery checks, fixes and boundaries.
- `data/SOURCES.json` and `docs/THIRD_PARTY_NOTICES.md`: third-party data/model provenance. Check upstream reuse terms before commercial distribution.

This is a local academic prototype, with three seeded products and a constrained returns workflow. Production deployment, arbitrary ERP generation and tax compliance are outside its tested scope.
