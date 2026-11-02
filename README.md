# TajerOS AI
An Egyptian business assistant with a React + TypeScript interface, ASP.NET Core 10 business backend, EF Core persistence and a Python AI service. This is a tested academic prototype, with measured model comparisons and explicit limitations.

## Quick start

Start with [QUICKSTART.md](QUICKSTART.md) for Windows and Linux instructions. Run `bash scripts/setup.sh` then `bash scripts/start.sh` on Linux/macOS with the prerequisites installed. The sales intelligence dashboard is a second, independent interface: `bash scripts/dashboard.sh`. The editable presentation is `docs/TajerOS_Final_Presentation.pptx`. Current validation and known limitations are in [docs/VALIDATION.md](docs/VALIDATION.md).

## Run the submission
Prerequisites: .NET 10 SDK, Python 3.12, Tesseract OCR and FFmpeg on PATH. Node 22+ is only needed to rebuild the UI. The compiled UI is included in backend/wwwroot.

From the extracted TajerOS directory:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell instead:
# .venv\Scripts\Activate.ps1
pip install -r ai/requirements-runtime.txt
python -m uvicorn service:app --app-dir ai --host 127.0.0.1 --port 8091
```
In a second terminal in TajerOS:
```bash
dotnet run --project backend --urls http://127.0.0.1:5082
```
Open http://127.0.0.1:5082. Owner: `owner@tajer.local`; staff: `staff@tajer.local`; demo password for both: `TajerDemo!2026`. Change `DEMO_PASSWORD` BEFORE the first database creation to choose another password. Existing hashes do not change when the environment changes. This is a single-shop demo, not a production multi-tenant deployment.

SQLite creates a local database automatically. For PostgreSQL set `ConnectionStrings__Postgres` to a connection string; this chooses Npgsql automatically. The Docker Compose configuration provides PostgreSQL. Docker/PostgreSQL integration was not executed in the authoring environment; the native SQLite stack was tested.

### Voice and optional model comparisons
Text commands, business workflows, receipt OCR and BM25 document answers need no paid API. Download the selected Whisper speech model before using microphone/audio:
```bash
python scripts/download_optional_models.py --voice
```
This is a large download. For reproducing transformer comparisons also run `--embedding`. For both Whisper candidates use `--all-voice`. Optional model weights are not inside the code ZIP. The default assistant uses exact source excerpts. Setting `LLM_API_KEY`, `LLM_BASE_URL` and `LLM_MODEL` enables optional external generation; this provider path has not been evaluated and sends selected company text to that provider.

### Rebuild UI
```bash
cd frontend
npm ci
npm run build
```
Build output goes into backend/wwwroot. For hot reload use `npm run dev` while the backend runs at port 5082.

### Docker
Copy `.env.example` to `.env`, change passwords, then `docker compose up --build`. Open http://127.0.0.1:5082. PostgreSQL data persists in a named volume. Model/data folders mount read-only into the AI container. Do not expose this demonstration to the public internet without production hardening.

## Six-minute demonstration
1. Log in as owner. Explain seeded rice/sugar opening stock and zero oil stock.
2. Upload `data/demo_receipt.png`. Review extracted quantity 50 and total 12000. Create and approve the purchase proposal.
3. In Assistant enter `بعت 15 كرتونة زيت`. Show that price is missing and approval is blocked. Enter total revenue 4500, save reviewed fields, then approve.
4. Show oil stock 35 and gross profit 900. Explain why expenses and tax are excluded.
5. Describe a returns department in Workflows. Review its generated schema and activate it. Submit a return of 2 cartons against the sale, then approve. Stock becomes 37, net revenue 3900, gross profit 780.
6. Ask `ما هي سياسة المرتجعات؟` in Knowledge. Show exact document excerpts and citations.
7. Open AIOps and simulate a failed request. Explain its simulated label and unchanged business records.
8. Open Evidence. Explain the data source and limitations before reading each chart.

Do not run the automated integration test against your presentation database: it creates transactions. Use an isolated database for testing. `tests/integration.py` defaults to port5082 and assumes fresh seeded state. Full machine execution instructions are in docs/Study_Guide.md.

## Contents
- backend: all authentication, approvals, money/stock calculations, workflow execution, persistence and AIOps APIs in C#.
- frontend: editable React TypeScript source plus compiled UI.
- ai: inference and reproducible model-evaluation programs.
- data: authored utterances/policies, real retail CSV, selected CORU crops and FLEURS audio samples with source manifest, synthetic receipts.
- results: measured comparisons, confusion matrix, forecast series, trained selected lightweight intent model and test reports.
- docs: project explanation, architecture choices, business case, glossary, defense questions and PPTX.

Read docs/Study_Guide.html first. Results are small research pilots. The system supports three demo products and one generated returns workflow template. It does not safely generate arbitrary ERP programs or provide statutory accounting/tax compliance.
