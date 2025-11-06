# WARP.md - Contexto del Proyecto MICO

## 📋 Descripción General

**MICO** es un sistema local de transcripción, resumen y almacenamiento de reuniones. Permite grabar audio desde dispositivos móviles, transcribirlo automáticamente, generar resúmenes estructurados y guardarlos en formato PDF.

**Objetivo Principal**: Sistema de coste cero para procesar reuniones con IA local.

## 🏗️ Arquitectura

```
PWA Frontend (móvil)
    ↓ (sube audio)
FastAPI Backend
    ↓
Whisper (Local) → Transcripción
    ↓
Ollama (Mistral 7B) → Resumen
    ↓
FPDF → Generación PDF
```

## 🛠️ Stack Tecnológico

### Backend

- **Framework**: FastAPI (Python 3.13)
- **Gestor de dependencias**: `uv`
- **Servidor**: Uvicorn con hot-reload
- **IA Local**:
  - **Whisper** (modelo `small`) - Transcripción de audio
  - **Ollama** (Mistral 7B) - Generación de resúmenes
- **Librerías clave**:
  - `openai-whisper` - Transcripción de audio
  - `fpdf` - Generación de PDFs
  - `requests` - Comunicación con Ollama
  - `python-multipart` - Upload de archivos

### Infraestructura

- **Contenedores**: Docker + Docker Compose
- **Servicios**:
  - `ollama` - Servidor de modelos LLM (puerto 11434)
  - `backend` - API FastAPI (puerto 8000)
- **Almacenamiento**: Volúmenes Docker para persistencia de modelos

## 📂 Estructura del Proyecto

```
mico/
├── docker-compose.yml          # Orquestación de servicios
├── backend/
│   ├── main.py                 # FastAPI app principal
│   ├── pyproject.toml          # Dependencias (uv)
│   ├── uv.lock                 # Lock file de dependencias
│   ├── Dockerfile              # Imagen del backend
│   ├── .venv/                  # Virtual environment (local)
│   ├── audio/                  # Audios subidos
│   ├── pdfs/                   # PDFs generados
│   └── assets/                 # Recursos (logo, etc.)
├── .vscode/
│   └── settings.json           # Configuración Python interpreter
├── ROADMAP.md                  # Plan y arquitectura del proyecto
└── README.md                   # Documentación básica
```

## 🔌 API Endpoints

### `POST /process`

**Descripción**: Endpoint único que procesa audio completo (transcripción + resumen + PDF)

**Input**:

- `file`: UploadFile (audio en formato .webm, .wav, .mp3, etc.)

**Output**:

```json
{
  "summary": "Texto del resumen estructurado",
  "pdf_path": "./pdfs/archivo_resumen.pdf"
}
```

**Flujo**:

1. Guarda el archivo en `./audio/`
2. Transcribe con Whisper (idioma español, fp16=False para CPU)
3. Envía transcripción a Ollama con prompt estructurado
4. Genera PDF con logo y formato profesional
5. Retorna resumen y ruta del PDF

## 🤖 Configuración de IA

### Whisper

- **Modelo**: `small` (equilibrio velocidad/precisión sin GPU)
- **Idioma**: Español (`language="es"`)
- **Configuración**: `fp16=False` (compatible con CPU)

### Ollama / Mistral

- **Modelo**: `mistral` (Mistral 7B)
- **Endpoint**: `/v1/completions`
- **Parámetros**:
  - `max_tokens`: 500
  - `temperature`: 0.3 (respuestas más deterministas)

### Prompt del Resumen

El sistema usa un prompt profesional que solicita:

1. Resumen breve de la reunión
2. Puntos clave tratados
3. Decisiones tomadas
4. Tareas acordadas y responsables

**Restricciones importantes**:

- No inventar información no presente en la transcripción
- Mantener lenguaje profesional y formal
- Traducir a español si es necesario
- Indicar "No se especificó" si falta información

## 🐳 Docker y Desarrollo

### Comandos Docker

```bash
# Levantar servicios
docker compose up -d

# Ver logs
docker compose logs -f

# Reiniciar backend
docker compose restart backend

# Bajar servicios
docker compose down
```

### Desarrollo Local (sin Docker)

```bash
cd backend

# Instalar dependencias con uv
uv sync

# Activar virtual environment
source .venv/bin/activate

# Ejecutar en modo desarrollo
uv run python main.py
```

El servidor se levanta en: `http://0.0.0.0:8000`

### Variables de Entorno

- `OLLAMA_HOST`: URL del servidor Ollama (default: `http://ollama:11434`)

## 📝 Gestión de Dependencias

El proyecto usa **uv** en lugar de pip/poetry:

```bash
# Añadir dependencia
uv add <paquete>

# Actualizar dependencias
uv sync

# Ejecutar comando en el entorno
uv run <comando>
```

## ⚠️ Consideraciones Importantes

### Rendimiento

- Transcripción de 1 hora → ~30-60 min en CPU
- Resumen → 5-20 segundos
- **No requiere GPU** (optimizado para CPU)

### Limitaciones Actuales

- No hay frontend PWA implementado aún
- No hay integración con Notion (planificada)
- No hay autenticación/multi-usuario
- Los archivos se guardan localmente sin gestión de limpieza

### Próximos Pasos (según ROADMAP.md)

1. Implementar PWA con botón de grabación
2. Añadir integración con Notion API
3. Multi-usuario / espacios por proyecto
4. Etiquetado automático con embeddings
5. Envío por Telegram/Email
6. Resúmenes diarios/semanales

## 🎯 Casos de Uso

1. **Reuniones de trabajo**: Grabar y generar actas automáticas
2. **Entrevistas**: Transcribir y resumir entrevistas
3. **Formaciones**: Capturar puntos clave de sesiones
4. **Notas de voz**: Convertir ideas habladas en documentos estructurados

## 🔧 Testing y Validación

### Testing Local

```bash
# Usar curl para probar el endpoint
curl -X POST "http://localhost:8000/process" \
  -F "file=@audio_prueba.wav"
```

### Verificar Servicios

```bash
# Ollama
curl http://localhost:11434/api/tags

# Backend
curl http://localhost:8000/docs  # Swagger UI
```

## 🎨 Estilo de Código

- **Python**: PEP 8
- **Type hints**: Usados donde es apropiado
- **Factory pattern**: `create_app()` para mejor testing
- **Async/await**: Endpoints async para mejor rendimiento

## 📦 Entregables

El sistema genera PDFs profesionales con:

- Logo de Ledmon Marketing
- Título "Resumen de Reunión"
- Contenido estructurado del resumen
- Footer: "Documento generado automáticamente por MICO AI & Ledmon Marketing"

## 🔐 Seguridad

- Sin autenticación implementada (MVP)
- Sin validación de tipos de archivo
- Sin límites de tamaño de archivo
- **⚠️ No usar en producción sin implementar seguridad**

---

**Última actualización**: Noviembre 2025
**Versión**: 0.1.0 (MVP)
**Mantenedor**: Ledmon Marketing
