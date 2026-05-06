# 🎙️ MICO - Meeting Intelligence & Content Organizer

> Automatic meeting transcription and summarization system with local AI.

![Python](https://img.shields.io/badge/Python-3.13-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.121-green) ![Whisper](https://img.shields.io/badge/Whisper-small-orange) ![Ollama](https://img.shields.io/badge/Ollama-Mistral_7B-red) ![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)

## 📖 Description

**MICO** is a complete solution to digitize and analyze meetings automatically. It records audio, transcribes content, generates structured summaries, and creates professional PDF documents, all processed locally with no external API costs.

### ✨ Key Features

- 🎤 **Automatic transcription** with Whisper (OpenAI)
- 🤖 **Smart summaries** with Mistral 7B via Ollama
- 📄 **Professional PDF generation** with logo and formatting
- 🐳 **Containerized** with Docker for easy deployment
- 💰 **100% local** - No cloud API costs
- ⚡ **CPU-optimized** - No GPU required
- 🇪🇸 **Optimized for Spanish** (multi-language compatible)

---

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 8GB of available RAM
- ~2GB of disk space (for models)

### Quick Installation

```bash
# 1. Clone the repository
git clone <https://github.com/itssDavyd/mico-api.git>
cd mico

# 2. Start services
docker compose up -d

# 3. Download the Mistral model
docker exec -it ollama ollama pull mistral

# 4. API available at http://localhost:8000
```

### Test the System

```bash
# Using curl
curl -X POST "http://localhost:8000/process" \
  -F "file=@your_audio.wav"

# Or access interactive documentation
open http://localhost:8000/docs
```

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Audio Input    │  (mobile/desktop recording)
│  .wav/.mp3/etc  │
└────────┬────────┘
         ↓
┌────────────────────────────┐
│   FastAPI Backend          │
│   Port: 8000               │
└────────┬───────────────────┘
         ↓
┌────────────────────────────┐
│   Whisper (small)          │  Transcription
│   Language: ES             │  audio → text
└────────┬───────────────────┘
         ↓
┌────────────────────────────┐
│   Ollama + Mistral 7B      │  Summary
│   Port: 11434              │  generation
└────────┬───────────────────┘
         ↓
┌────────────────────────────┐
│   FPDF Generator           │  PDF document
│   + Logo                   │  creation
└────────┬───────────────────┘
         ↓
┌────────────────────────────┐
│   PDF Output               │
│   ./pdfs/summary.pdf       │
└────────────────────────────┘
```

---

## 📁 Project Structure

```
mico/
├── docker-compose.yml        # Service orchestration
├── README.md                 # This file
├── ROADMAP.md                # Planning and future features
├── WARP.md                   # Context for Warp AI
├── .gitignore
└── backend/
    ├── main.py               # FastAPI application
    ├── pyproject.toml        # Python dependencies (uv)
    ├── uv.lock               # Dependency lock file
    ├── Dockerfile            # Backend Docker image
    ├── .venv/                # Virtual environment (local dev)
    ├── audio/                # 📂 Uploaded audio files
    ├── pdfs/                 # 📂 Generated PDFs
    └── assets/
        └── logo.png          # Logo for PDFs
```

---

## 🔌 API Reference

### `POST /process`

Processes a full audio file: transcription + summary + PDF generation.

**Request:**

```bash
POST http://localhost:8000/process
Content-Type: multipart/form-data

file: <audio_file>
```

**Response:**

```json
{
  "summary": "1. Brief meeting summary.\n\nIn this meeting...",
  "pdf_path": "./pdfs/meeting_audio_summary.pdf"
}
```

**Supported audio formats:**

- `.wav` (recommended)
- `.mp3`
- `.m4a`
- `.webm`
- `.ogg`
- Any FFmpeg-compatible format

**Estimated processing time:**

- 5-minute audio → ~2-5 minutes
- 30-minute audio → ~15-30 minutes
- 1-hour audio → ~30-60 minutes

---

## 🛠️ Local Development

### Without Docker (development)

```bash
# Navigate to backend
cd backend

# Install uv (if you don't have it)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate

# Run development server
uv run python main.py
```

**Note:** For local development, you need Ollama installed:

```bash
# macOS
brew install ollama
ollama serve
ollama pull mistral
```

### Add New Dependencies

```bash
cd backend
uv add package-name
```

### Endpoint Testing

```bash
# Basic health check
curl http://localhost:8000

# Interactive documentation (Swagger)
open http://localhost:8000/docs

# Process test audio
curl -X POST "http://localhost:8000/process" \
  -F "file=@test_audio.wav" \
  -o response.json
```

---

## 🐳 Useful Docker Commands

```bash
# View real-time logs
docker compose logs -f

# View backend logs only
docker compose logs -f backend

# Restart a service
docker compose restart backend

# Rebuild backend image
docker compose up -d --build backend

# Stop all services
docker compose down

# Stop and remove volumes (full reset)
docker compose down -v

# Enter backend container
docker exec -it backend bash

# View installed Ollama models
docker exec -it ollama ollama list
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# docker-compose.yml (backend service)
OLLAMA_HOST=http://ollama:11434  # Ollama server URL
```

### Prompt Customization

You can modify the summary prompt in `backend/main.py` lines 28-49 to adapt the summary format to your needs.

### Change Whisper Model

In `backend/main.py` line 11:

```python
MODEL = whisper.load_model("small")  # Options: tiny, base, small, medium, large
```

**Available models:**

- `tiny` - Faster, lower accuracy (~1GB RAM)
- `base` - Basic balance (~1GB RAM)
- `small` - **Recommended** (~2GB RAM)
- `medium` - Higher accuracy (~5GB RAM)
- `large` - Maximum accuracy (~10GB RAM)

---

## 📊 Performance

### Hardware Requirements

| Component | Minimum    | Recommended |
| --------- | ---------- | ----------- |
| RAM       | 4GB        | 8GB+        |
| CPU       | 2 cores    | 4+ cores    |
| Disk      | 5GB        | 10GB+       |
| GPU       | Not required | Optional\* |

\*With an NVIDIA GPU (CUDA), processing can be 5-10x faster.

### Processing Times (CPU)

| Audio Duration | Transcription | Summary | Total      |
| -------------- | ------------- | ------- | ---------- |
| 5 minutes      | 2-5 min       | 5-10s   | ~3-6 min   |
| 30 minutes     | 15-30 min     | 10-20s  | ~16-31 min |
| 1 hour         | 30-60 min     | 15-30s  | ~31-61 min |

---

## 🎯 Use Cases

### 1️⃣ Work Meetings

```bash
# Record meeting → Transcribe → Generate automatic minutes
Result: PDF with decisions and assigned tasks
```

### 2️⃣ Interviews

```bash
# Record interview → Extract key points → Summary document
Result: Full transcript + executive summary
```

### 3️⃣ Training and Conferences

```bash
# Record session → Generate structured notes
Result: Organized study material
```

### 4️⃣ Voice Notes

```bash
# Record ideas → Convert to text → Organize in document
Result: Captured and structured ideas
```

---

## 🔜 Roadmap

See [ROADMAP.md](./ROADMAP.md) for the complete plan. Upcoming features:

- [ ] 📱 PWA for mobile recording
- [ ] 📝 Notion API integration
- [ ] 👥 Multi-user system
- [ ] 🏷️ Automatic tagging with embeddings
- [ ] 📧 Automatic sending via email/Telegram
- [ ] 📊 Analytics dashboard
- [ ] 🌍 Improved multi-language support
- [ ] 🔐 Authentication and authorization

---

## 🐛 Troubleshooting

### Problem: "Connection refused" to Ollama

```bash
# Verify Ollama is running
docker compose ps

# Check Ollama logs
docker compose logs ollama

# Restart Ollama
docker compose restart ollama
```

### Problem: Transcription is too slow

```bash
# Use a smaller model (in main.py)
MODEL = whisper.load_model("tiny")  # or "base"
```

### Problem: "Model not found" in Ollama

```bash
# Download model manually
docker exec -it ollama ollama pull mistral

# Verify installed models
docker exec -it ollama ollama list
```

### Problem: Out of Memory

```bash
# Increase available memory for Docker
# Docker Desktop → Settings → Resources → Memory: 8GB+

# Or use a smaller Whisper model
MODEL = whisper.load_model("tiny")
```

---

## 🤝 Contributing

Contributions are welcome. Please:

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Transcription model
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [Mistral AI](https://mistral.ai/) - Mistral 7B model
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [FPDF](http://www.fpdf.org/) - PDF generation

<p align="center">
  <strong>MICO</strong> - Meeting Intelligence & Content Organizer<br>
  Developer: David Fernandez <br>
  Company: Aitodetec
</p>
