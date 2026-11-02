# TajerOS LLM | Beginner-friendly Python + Streamlit

This is an **additional, simple standalone dashboard** included alongside the original TajerOS ASP.NET/React project. The original project is preserved. The new project uses Python only, with no custom `def` functions or `with` statements in `app.py`.

## Features
- Existing 6,435-row Walmart weekly-sales dataset from your uploaded TajerOS ZIP (45 stores, 2010–2012).
- Replace the demo dataset by uploading a CSV with `Store,Date,Weekly_Sales`.
- Interactive charts and store filters.
- Real **scikit-learn** Ridge and Random Forest forecasts, compared against a seasonal repeat baseline on the most recent chronological holdout; model chosen by lowest MAE.
- Download a weekly forecast CSV.
- Optional real OpenAI LLM business advisor grounded in computed facts from **your selected data**. No hardcoded replies, no imitation of an LLM.
- No LLM key needed to use the dashboard and ML.

## How to run (Windows PowerShell or CMD)

**1.** Open a terminal in this folder.

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

**2.** Create a file called `.env` next to `app.py`. Use `.env.example` as a template:

```text
OPENAI_API_KEY=your_actual_api_key
OPENAI_MODEL=gpt-4.1-mini
```

Get an API key at https://platform.openai.com/api-keys (separate from ChatGPT Plus billing). **Never upload `.env` to GitHub.** The chosen model must be available to your account. The OpenAI API requires network access and usage may incur charges.

**3.** Start the app:

```powershell
python -m streamlit run app.py
```

Open http://localhost:8501

Optional: verify your LLM credentials before opening the dashboard:

```powershell
python check_llm.py
```

If you saw `streamlit is not recognized`, the `python -m streamlit` command above avoids relying on the executable being directly on PATH.

## First demo
1. Open Dashboard and filter Store 1; show the historical sales charts.
2. Open Forecast and show Ridge vs Random Forest vs seasonal baseline, holdout validation, and next 8 weeks.
3. Open AI Advisor and ask `What happened to sales recently, and what should I investigate?`.
4. Ask `Do we need to reorder 200 units?`—a good answer will ask for inventory, demand **in units**, and supplier lead time, because that information is not in the source dataset.
5. Upload a different CSV with the required columns to use your own records; the assistant's context changes automatically.

## Architecture

`CSV (real sales records) → Pandas calculations → scikit-learn forecast + metric comparison → Streamlit charts → snapshot of verified facts → OpenAI Responses API → natural-language recommendations`

The model does not run SQL or arbitrary Python. The LLM has no permissions to approve sales, update stock or place orders. Only limited computed facts (not the raw CSV) are transmitted when an AI question is submitted.

## Important limitations
- Demo sales are historical **2010–2012**, not current 2026 sales. Predictions are for the first weeks **after the latest date in the uploaded data**, not a forecast for today unless you upload current data.
- `Weekly_Sales` is a monetary amount, not units sold or inventory. A reorder quantity cannot responsibly be derived from this CSV alone.
- The currency selector changes the display label only. It does **not** convert amounts.
- Data must be consecutive weekly observations for forecasting. Irregular/daily or missing-week data remains viewable, but forecasts are disabled. Infinite, negative and invalid sales values are removed with a warning.
- ML forecasts are estimates. The automatically selected model may be the seasonal repeat baseline if it beats both ML models on recent validation. No predictive guarantee or causal claims.
- Chat history is limited to your current Streamlit session; there is no authentication, authorization or persistence in this standalone prototype. Do not publish it publicly or upload confidential data without adding access control, rate limiting, security review and privacy/legal checks.
- Your **original** TajerOS project already has a separate optional external LLM document Q&A pathway: `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` in `ai/service.py`. That feature is independent of this Streamlit advisor.

## Next steps toward a real production ERP
Use a proper authenticated backend, store approved transactions in a database, load current store data on a scheduled ETL pipeline, add unit-sales and inventory history, evaluate with walk-forward backtesting, add LLM logging and human-reviewed workflows, and deploy secrets in an encrypted secrets manager.
