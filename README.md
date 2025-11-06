# 🎙️ MICO - Meeting Intelligence & Content Organizer

> Sistema de transcripción y resumen automático de reuniones con IA local.

![Python](https://img.shields.io/badge/Python-3.13-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.121-green) ![Whisper](https://img.shields.io/badge/Whisper-small-orange) ![Ollama](https://img.shields.io/badge/Ollama-Mistral_7B-red) ![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)

## 📖 Descripción

**MICO** es una solución completa para digitalizar y analizar reuniones de forma automática. Graba audio, transcribe el contenido, genera resúmenes estructurados y crea documentos PDF profesionales, todo procesado localmente sin costes de APIs externas.

### ✨ Características principales

- 🎤 **Transcripción automática** con Whisper (OpenAI)
- 🤖 **Resúmenes inteligentes** con Mistral 7B via Ollama
- 📄 **Generación de PDFs** profesionales con logo y formato
- 🐳 **Containerizado** con Docker para fácil despliegue
- 💰 **100% local** - Sin costes de APIs cloud
- ⚡ **Optimizado para CPU** - No requiere GPU
- 🇪🇸 **Optimizado para español** (multi-idioma compatible)

---

## 🚀 Quick Start

### Prerrequisitos

- Docker y Docker Compose instalados
- Al menos 8GB de RAM disponible
- ~2GB de espacio en disco (para modelos)

### Instalación rápida

```bash
# 1. Clonar el repositorio
git clone <https://github.com/Ledmon-Marketing-y-Multimedia/mico-api.git>
cd mico

# 2. Levantar servicios
docker compose up -d

# 3. Descargar el modelo Mistral
docker exec -it ollama ollama pull mistral

# 4. API disponible en http://localhost:8000
```

### Probar el sistema

```bash
# Usando curl
curl -X POST "http://localhost:8000/process" \
  -F "file=@tu_audio.wav"

# O accede a la documentación interactiva
open http://localhost:8000/docs
```

---

## 🏗️ Arquitectura

```
┌─────────────────┐
│  Audio Input    │  (grabación móvil/desktop)
│  .wav/.mp3/etc  │
└────────┬────────┘
         ↓
┌────────────────────────────┐
│   FastAPI Backend          │
│   Puerto: 8000             │
└────────┬───────────────────┘
         ↓
┌────────────────────────────┐
│   Whisper (small)          │  Transcripción
│   Idioma: ES               │  audio → texto
└────────┬───────────────────┘
         ↓
┌────────────────────────────┐
│   Ollama + Mistral 7B      │  Generación
│   Puerto: 11434            │  de resumen
└────────┬───────────────────┘
         ↓
┌────────────────────────────┐
│   FPDF Generator           │  Creación
│   + Logo Ledmon            │  documento PDF
└────────┬───────────────────┘
         ↓
┌────────────────────────────┐
│   PDF Output               │
│   ./pdfs/resumen.pdf       │
└────────────────────────────┘
```

---

## 📁 Estructura del Proyecto

```
mico/
├── docker-compose.yml        # Orquestación de servicios
├── README.md                 # Este archivo
├── ROADMAP.md                # Planificación y futuras features
├── WARP.md                   # Contexto para Warp AI
├── .gitignore
└── backend/
    ├── main.py               # FastAPI application
    ├── pyproject.toml        # Dependencias Python (uv)
    ├── uv.lock               # Lock file de dependencias
    ├── Dockerfile            # Imagen Docker del backend
    ├── .venv/                # Virtual environment (dev local)
    ├── audio/                # 📂 Audios subidos
    ├── pdfs/                 # 📂 PDFs generados
    └── assets/
        └── logo.png          # Logo para PDFs
```

---

## 🔌 API Reference

### `POST /process`

Procesa un archivo de audio completo: transcripción + resumen + generación de PDF.

**Request:**

```bash
POST http://localhost:8000/process
Content-Type: multipart/form-data

file: <audio_file>
```

**Response:**

```json
{
  "summary": "1. Resumen breve de la reunión.\n\nEn esta reunión...",
  "pdf_path": "./pdfs/audio_reunión_resumen.pdf"
}
```

**Formatos de audio soportados:**

- `.wav` (recomendado)
- `.mp3`
- `.m4a`
- `.webm`
- `.ogg`
- Cualquier formato compatible con FFmpeg

**Tiempo estimado de procesamiento:**

- Audio de 5 min → ~2-5 minutos
- Audio de 30 min → ~15-30 minutos
- Audio de 1 hora → ~30-60 minutos

---

## 🛠️ Desarrollo Local

### Sin Docker (desarrollo)

```bash
# Navegar al backend
cd backend

# Instalar uv (si no lo tienes)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalar dependencias
uv sync

# Activar entorno virtual
source .venv/bin/activate

# Ejecutar servidor de desarrollo
uv run python main.py
```

**Nota:** Para desarrollo local necesitas tener Ollama instalado:

```bash
# macOS
brew install ollama
ollama serve
ollama pull mistral
```

### Añadir nuevas dependencias

```bash
cd backend
uv add nombre-del-paquete
```

### Testing del endpoint

```bash
# Healthcheck básico
curl http://localhost:8000

# Documentación interactiva (Swagger)
open http://localhost:8000/docs

# Procesar audio de prueba
curl -X POST "http://localhost:8000/process" \
  -F "file=@test_audio.wav" \
  -o response.json
```

---

## 🐳 Comandos Docker Útiles

```bash
# Ver logs en tiempo real
docker compose logs -f

# Ver solo logs del backend
docker compose logs -f backend

# Reiniciar un servicio
docker compose restart backend

# Reconstruir imagen del backend
docker compose up -d --build backend

# Parar todos los servicios
docker compose down

# Parar y eliminar volúmenes (reset completo)
docker compose down -v

# Entrar al contenedor del backend
docker exec -it backend bash

# Ver modelos instalados en Ollama
docker exec -it ollama ollama list
```

---

## ⚙️ Configuración

### Variables de Entorno

```bash
# docker-compose.yml (backend service)
OLLAMA_HOST=http://ollama:11434  # URL del servidor Ollama
```

### Personalización del Prompt

Puedes modificar el prompt de resumen en `backend/main.py` líneas 28-49 para adaptar el formato del resumen a tus necesidades.

### Cambiar el modelo de Whisper

En `backend/main.py` línea 11:

```python
MODEL = whisper.load_model("small")  # Opciones: tiny, base, small, medium, large
```

**Modelos disponibles:**

- `tiny` - Más rápido, menor precisión (~1GB RAM)
- `base` - Balance básico (~1GB RAM)
- `small` - **Recomendado** (~2GB RAM)
- `medium` - Mayor precisión (~5GB RAM)
- `large` - Máxima precisión (~10GB RAM)

---

## 📊 Rendimiento

### Requisitos de Hardware

| Componente | Mínimo       | Recomendado |
| ---------- | ------------ | ----------- |
| RAM        | 4GB          | 8GB+        |
| CPU        | 2 cores      | 4+ cores    |
| Disco      | 5GB          | 10GB+       |
| GPU        | No requerida | Opcional\*  |

\*Con GPU NVIDIA (CUDA) el procesamiento puede ser 5-10x más rápido.

### Tiempos de Procesamiento (CPU)

| Duración Audio | Transcripción | Resumen | Total      |
| -------------- | ------------- | ------- | ---------- |
| 5 minutos      | 2-5 min       | 5-10s   | ~3-6 min   |
| 30 minutos     | 15-30 min     | 10-20s  | ~16-31 min |
| 1 hora         | 30-60 min     | 15-30s  | ~31-61 min |

---

## 🎯 Casos de Uso

### 1️⃣ Reuniones de Trabajo

```bash
# Grabar reunión → Transcribir → Generar acta automática
Resultado: PDF con decisiones y tareas asignadas
```

### 2️⃣ Entrevistas

```bash
# Grabar entrevista → Extraer puntos clave → Documento resumen
Resultado: Transcripción completa + resumen ejecutivo
```

### 3️⃣ Formaciones y Conferencias

```bash
# Grabar sesión → Generar apuntes estructurados
Resultado: Material de estudio organizado
```

### 4️⃣ Notas de Voz

```bash
# Grabar ideas → Convertir a texto → Organizar en documento
Resultado: Ideas capturadas y estructuradas
```

---

## 🔜 Roadmap

Ver [ROADMAP.md](./ROADMAP.md) para el plan completo. Próximas features:

- [ ] 📱 PWA para grabación desde móvil
- [ ] 📝 Integración con Notion API
- [ ] 👥 Sistema multi-usuario
- [ ] 🏷️ Etiquetado automático con embeddings
- [ ] 📧 Envío automático por email/Telegram
- [ ] 📊 Dashboard de analytics
- [ ] 🌍 Soporte multi-idioma mejorado
- [ ] 🔐 Autenticación y autorización

---

## 🐛 Troubleshooting

### Problema: "Connection refused" a Ollama

```bash
# Verificar que Ollama esté corriendo
docker compose ps

# Ver logs de Ollama
docker compose logs ollama

# Reiniciar Ollama
docker compose restart ollama
```

### Problema: Transcripción muy lenta

```bash
# Usar un modelo más pequeño (en main.py)
MODEL = whisper.load_model("tiny")  # o "base"
```

### Problema: "Model not found" en Ollama

```bash
# Descargar el modelo manualmente
docker exec -it ollama ollama pull mistral

# Verificar modelos instalados
docker exec -it ollama ollama list
```

### Problema: Out of Memory

```bash
# Aumentar memoria disponible para Docker
# Docker Desktop → Settings → Resources → Memory: 8GB+

# O usar modelo Whisper más pequeño
MODEL = whisper.load_model("tiny")
```

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit de cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo desarrollo por **Ledmon Marketing**.

---

## 🙏 Agradecimientos

- [OpenAI Whisper](https://github.com/openai/whisper) - Modelo de transcripción
- [Ollama](https://ollama.ai/) - Runtime de modelos LLM local
- [Mistral AI](https://mistral.ai/) - Modelo Mistral 7B
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web
- [FPDF](http://www.fpdf.org/) - Generación de PDFs

---

## 📞 Contacto

**Ledmon Marketing**

Proyecto desarrollado para optimizar la gestión de reuniones y contenido organizacional.

---

<p align="center">
  <strong>MICO</strong> - Meeting Intelligence & Content Organizer<br>
  Desarrollador: David Fernandez <br>
  Empresa: Ledmon Marketing
</p>
