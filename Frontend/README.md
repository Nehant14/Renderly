# Renderly — Manim animation studio

React + Vite frontend with a FastAPI backend. Flow: **prompt → Google Gemini → Manim code → render → MP4 preview**, plus conversational edits and project export (MoviePy merge).

## Prerequisites

- **Node 18+**
- **Python 3.11+**
- **Manim Community** (`manim` on PATH) — [install guide](https://docs.manim.community/en/stable/installation.html)
- **FFmpeg** on PATH (encoding / MoviePy)
- **MongoDB** (local or Atlas)
- **Google Gemini API key** for code generation

## Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
copy .env.example .env      # set MONGODB_URL, DATABASE_NAME, GEMINI_API_KEY, STORAGE_PATH
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API: `http://127.0.0.1:8000/api/health` — static videos under `/media/...`.

## Frontend

```bash
npm install
npm run dev
```

Vite proxies `/api` and `/media` to the backend (see `vite.config.js`). Optional: set `VITE_API_URL` in `.env` if the API is not on the same origin.

## Usage

1. Open the app, expand the sidebar (**menu** icon).
2. **New project** → select it.
3. **New shot** (optional — a shot is auto-created when you send a prompt).
4. Type an animation description and send — code is generated, then **rendered** automatically; the video appears when ready.
5. Use **Render**, **Render + AI fix**, **Regenerate**, and **Export project** in the main panel as needed.

## Security note

Generated code is validated (AST, import allow/deny) and Manim runs in a **per-shot working directory** with a subprocess (no shell). This reduces risk but is **not** a full OS-level sandbox; run the backend with least privilege in production.
