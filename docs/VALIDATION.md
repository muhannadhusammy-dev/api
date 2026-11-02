# Delivery validation — 2 November 2026

The uploaded TajerOS source was imported into `muhannadhusammy-dev/api` and validated on Linux with Python 3.12.14, .NET SDK 10.0.403 and Node 24.19.0.

## Current verified results

| Check | Outcome | Evidence / command |
|---|---|---|
| Native backend Release build | Passed; 0 warnings, 0 errors | `dotnet build backend -c Release` |
| TypeScript + Vite production UI | Passed | `cd frontend && npm ci && npm run build` |
| Python dependency consistency | Passed | `.venv/bin/python -m pip check` |
| Frontend production dependency audit | 0 reported vulnerabilities | `npm audit --omit=dev` at delivery time |
| Business integration | 27 checks passed using temporary SQLite DB | `tests/run.sh`; `results/integration_tests.json` |
| Dashboard regression tests | 4 tests passed | `tests/test_dashboard.py` |
| Chromium browser smoke | 13 checks passed | `tests/browser_smoke.py`; `results/browser_smoke.json` |
| Real OCR/AI HTTP checks | 11 checks passed | `tests/media_smoke.py`; `results/media_smoke.json` |
| Reusable Linux setup script | Passed end to end on prepared instance | `scripts/setup.sh` |
| Startup script | Both health endpoints passed | `scripts/start.sh`; `scripts/readiness.py` |
| PowerPoint | 19 editable slides, speaker notes on all slides; ZIP/XML reopened successfully and all shapes within bounds | `scripts/build_presentation.py` |

Browser checks cover owner login and loaded dashboard, all seven additional screens, OCR quantity/total, Arabic RTL, mobile width, JavaScript exceptions, live Streamlit dashboard and forecasting. They are smoke checks, not exhaustive usability or accessibility certification.

Business checks cover denied anonymous access, invalid credentials, Arabic compound command extraction, missing selling price, staff/owner permissions, pending/approved inventory behavior, weighted costs, gross profit, repeat-safe approvals, stale edits, returns, cumulative over-return prevention, unusual-price acknowledgment, cited policy excerpts, insufficient sales history, operational health and audit records.

Dashboard tests exercise all four pages, store filtering, a 12-week forecast, nonnegative output, infinite input removal, irregular weekly dates, missing columns and invalid data. Media checks compare quantity/total on all eight **synthetic** receipts, reject an invalid image, report the selected speech model and verify the explicit 503 response when optional voice weights are absent.

## Delivery fixes and additions

- Infinite sales values are removed before model fitting instead of crashing forecasts.
- Gaps in weekly observations disable forecasting instead of silently misaligning the 52-week baseline.
- Advisor chat state resets on a content-based dataset fingerprint, currency, store or horizon change.
- Replaced deprecated Streamlit width parameters; pinned tested dashboard dependencies.
- Null/empty login fields produce a validation error instead of a possible password-hasher exception.
- AI health reports the selected speech model, rather than checking an unrelated base-model folder.
- Model downloads verify checksums before replacing the final artifact; failed temporary downloads are removed.
- Added setup/startup scripts, health readiness checks, first-run guide, dashboard/browser/media tests and a CI workflow.
- Integration launcher checks for occupied ports and forces an isolated SQLite database with a known test password.
- Added a final presentation based on the prior deck's business narrative and supplied photos, with current app screenshots, technical detail and speaker notes. Team/supervisor names follow the supplied deck.

## What is not claimed

- No software can be guaranteed free of every possible error. The checks above establish the tested workflows and their limits.
- **External LLM provider calls were not executed:** no API key was supplied. Dashboards, forecasts, OCR, text commands and extractive document answers work without one. The optional provider paths remain available for the user to configure.
- **Speech transcription was not executed:** external Whisper weights are not in the uploaded archive. The unavailable-state response was tested. `scripts/download_optional_models.py --voice` installs the selected model, with recorded hash checks.
- **Docker/PostgreSQL and Windows launchers were not executed.** The native Linux/SQLite stack was verified. PostgreSQL and Windows paths remain supplied alternatives.
- Original `results/benchmarks.json`, `ocr.json`, `speech.json`, `receipt_fields.json`, `outage_tests.json`, `ui_tests.json` and other research reports came with the upload. They are retained as original evidence, **not represented as newly recomputed measurements**. Current delivery reports have the filenames listed above.
- The sales dataset is historical 2010–2012 monetary sales, not live inventory or Egyptian unit demand. Forecast selection uses a recent chronological holdout, not an independent final test of the selected winner.
- The system remains a local academic demonstration: three seeded products, one constrained returns template, no production multi-tenant or statutory-accounting claim.
- GitHub Actions configuration is supplied; a remote CI result is not claimed by this document.
- The PPTX was structurally checked; Office/LibreOffice rendering was not available. Rendering may vary with installed fonts.

## Reproduce

Read `QUICKSTART.md`. Run Linux setup, install `requirements-dev.txt`, run dashboard tests, stop any local servers, then run `tests/run.sh`. Start both applications for browser tests; Chromium defaults to `/usr/bin/chromium`, override with `CHROMIUM_PATH`. Run `tests/media_smoke.py` while the AI service is running. Rebuild the presentation with `.venv/bin/python scripts/build_presentation.py`.

Snapshots retain dependencies and files, but live processes must be restarted. Environment startup instructions must be saved separately. Publishing and validation in a newly restored task are separate platform steps.
