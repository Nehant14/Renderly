# Renderly backend (FastAPI + MongoDB + Gemini + Manim)

## Stack

- **FastAPI** + **Uvicorn**
- **MongoDB** via **Motor** + **Beanie** ODM
- **Google Gemini** (`google-generativeai`) for Manim code generation / edits / auto-fix
- **Manim Community** (CLI on `PATH`) for rendering
- **MoviePy** for merging shot videos on export

## Environment

Copy `.env.example` to `.env` and set:

- `MONGODB_URL` — e.g. `mongodb://localhost:27017`
- `DATABASE_NAME` — e.g. `animcursor`
- `GEMINI_API_KEY` — from Google AI Studio
- `GEMINI_MODEL` — e.g. `gemini-1.5-flash` or `gemini-2.0-flash`
- `STORAGE_PATH` — root for `projects/...` media (default `./storage`)

## Run

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Ensure **MongoDB** is running and **Manim** + **FFmpeg** are installed for render/export.

## API

Same as the React client: `/api/health`, `/api/projects`, `/api/projects/{id}/shots`, `/api/shots/...`, `/api/projects/{id}/export`, static media at `/media/...`.

Resource IDs are MongoDB **ObjectId strings** in JSON.
