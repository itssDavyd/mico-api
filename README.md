# MICO API

Sales visit audio → structured commercial report PDF.

Uses shared **thor-stt** (transcription) and **Ollama** (summarization) on Jetson Thor. No extra models loaded by MICO.

## Flow

```
PWA (Svelte)
  │
  ├─ Long recording (recommended)
  │    POST /audio/sessions
  │    POST /audio/sessions/{id}/parts   (every 5–10 min)
  │    POST /audio/sessions/{id}/finalize
  │
  └─ Short recording
       POST /audio/process               (single file)
  │
  ▼
GET /audio/status/{id}  →  poll until done
GET /file/download/{filename}
```

## Chunked sessions (no duration cap)

| Step | Endpoint | Body |
|------|----------|------|
| 1 | `POST /audio/sessions` | `filename` (form, optional) |
| 2 | `POST /audio/sessions/{id}/parts` | `part_index` (0,1,2…), `file` |
| 3 | `POST /audio/sessions/{id}/finalize` | — |
| 4 | `GET /audio/status/{id}` | — |

Status returns `parts_uploaded`, `parts_transcribed`, `parts_total`, `progress_pct`, `download_url`.

Re-uploading the same `part_index` overwrites the chunk (safe retry).

Record in **webm/opus ~48 kbps** on the client. Default chunk limit: **50 MB** (`MAX_CHUNK_MB`).

## Single upload

`POST /audio/process` with one `file` — for short visits only.

## Auth

`POST /auth/login` → session cookie. Required when `AUTH_ENABLED=true`.

## Run (NVIDIA Thor)

Production deployment against shared **thor-stt** and **Ollama** on Thor:

```bash
cp .env.example .env   # configure STT_BASE_URL, OLLAMA_HOST, THOR_NETWORK, secrets
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Optional local Ollama for testing without Thor:

```bash
docker compose --profile dev up -d
```

## Key env vars

| Variable | Production |
|----------|------------|
| `STT_BASE_URL` | `http://thor-stt:8090` |
| `OLLAMA_HOST` | `http://ollama:11434` |
| `OLLAMA_MODEL` | `qwen2.5:7b-instruct-q4_K_M` |
| `MAX_CHUNK_MB` | `50` |
| `THOR_NETWORK` | Docker network of thor-rag-api |
| `COOKIE_SECURE` | `true` (keep `true` behind HTTPS) |

## Stack

FastAPI · Redis · ARQ · thor-stt · Ollama · fpdf2
