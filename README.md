# Documind (free)

Lab FastAPI app: upload PDF / CSV / Excel, extract text/tables locally, then optionally send that text to **Groq** (`llama-3.3-70b-versatile`) for structured markdown (vendor, dates, line items, totals).

Images are accepted by the UI but **not OCR'd** — upload PDF/CSV/Excel instead.

## Stack

- FastAPI + Uvicorn
- Local extract: pdfplumber, pandas, openpyxl
- Optional LLM: Groq API (`GROQ_API_KEY`), model `llama-3.3-70b-versatile`

## Run locally

```bash
pip install -r requirements.txt
set GROQ_API_KEY=your_key
uvicorn app:app --reload
```

Open http://localhost:8000

On Linux/macOS use `export GROQ_API_KEY=your_key`.

## API

- `GET /` — web UI (`static/index.html`)
- `POST /process` — form fields `task` + `files` (needs valid `GROQ_API_KEY` for LLM step)
- `GET /health` — `{ status, model, api_key_set }`

## Evidence (2026-09-09)

On Windows (Python 3.13), after `pip install -r requirements.txt`:

```text
import processor, app  → imports_ok
extract_csv_excel(sample.csv) → markdown table (vendor Acme, amount 12.5)
```

**Proven:** local CSV/Excel/PDF extract path and app imports.
**Not proven this run:** end-to-end Groq `/process` (no key exercised). Treat generation as optional/config-dependent.
**Not claimed:** OCR, production SLA, or Gemini (older docstring was wrong; code uses Groq).

## Deploy

`Procfile` + `railway.toml` for Railway-style hosts. Set `GROQ_API_KEY` in the host environment. Live URL not verified in this evidence pass.

## Author

Harsha Nandhan Reddy Gajulapalli  
https://github.com/Harshanandhan
