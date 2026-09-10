# Documind (free)

Lab FastAPI app: upload PDF / CSV / Excel, extract text/tables locally, then optionally send that text to **Groq** (`llama-3.3-70b-versatile`) for structured markdown.

**Works without API keys** in extract-only mode (shows extracted text/tables). Set `GROQ_API_KEY` on the host to enable LLM structuring.

Images are accepted by the UI but **not OCR'd** — upload PDF/CSV/Excel instead.

## Try it

1. Open the live demo URL
2. Drop a PDF, CSV, or Excel file
3. Click an example chip (or write a task) and hit **Process Documents**

## Stack

- FastAPI + Uvicorn
- Local extract: pdfplumber, pandas, openpyxl
- Optional LLM: Groq API (`GROQ_API_KEY`), model `llama-3.3-70b-versatile`

## Env vars

| Variable | Required? | Purpose |
|----------|-----------|---------|
| `GROQ_API_KEY` | Optional | Enables Llama 3.3 structuring; without it the app returns local extraction only |
| `PORT` | Set by host | Uvicorn listen port (Railway sets this) |

## Run locally

```bash
pip install -r requirements.txt
# optional: export GROQ_API_KEY=your_key
uvicorn app:app --reload
```

Open http://localhost:8000

## API

- `GET /` — web UI
- `POST /process` — form fields `task` + `files`
- `GET /health` — `{ status, model, api_key_set, mode }`

## Deploy

`Procfile` + `railway.toml`. Deploy to Railway; set `GROQ_API_KEY` only if you want LLM mode.

## Author

Harsha Nandhan Reddy Gajulapalli  
https://github.com/Harshanandhan
