# 📝 MICO: Sistema Local de Transcripción + Resumen + Notion (Cero Coste)

## 🎯 Objetivo

Grabar audio desde el móvil → Transcripción automática → Resumen estructurado → Guardar en Notion.

---

## 🏗️ Arquitectura General

```
PWA (Frontend Móvil) sveltekit + skeletonUI -> PWA
      ↓ (sube audio .webm / .wav)
FastAPI (Backend)
      ↓
Whisper (Local) → Transcripción a texto
      ↓
Ollama (Mistral 7B) → Resumen + Puntos Clave
      ↓
Notion API → Crear Página
```

---

## 🧱 Servicios a Montar en el VPS (con Portainer + Docker)

| Servicio          | Tecnología                | Motivo                                                              |
| ----------------- | ------------------------- | ------------------------------------------------------------------- |
| **Transcripción** | Whisper (`whisper-small`) | Autodetección de idioma, muy buena precisión en CPU, gratis.        |
| **Resumen**       | Ollama (`mistral:7b`)     | Modelo ligero capaz de estructurar bien los puntos clave.           |
| **API Backend**   | FastAPI                   | Simple, rápido y fácil de conectar con Notion.                      |
| **Frontend**      | Web App PWA               | Evita apps nativas, funciona en móvil, botón de grabación sencillo. |
| **Notas**         | Notion API                | Guarda los resúmenes organizados en tu espacio.                     |

---

## ⚙️ Modelos Recomendados

| Proceso       | Modelo                | Razón                                       |
| ------------- | --------------------- | ------------------------------------------- |
| Transcripción | `whisper-small`       | Mejor equilibrio velocidad/calidad sin GPU. |
| Resumen       | `mistral:7b` (Ollama) | Muy bueno para resumir y estructurar.       |

---

## 🕒 Rendimiento Estimado

- Reunión 1 hora → ~30–60 min de transcripción en CPU.
- Resumen → 5–20 segundos.

Esto es **cero coste** y **totalmente local**.

---

## 📂 Estructura del Proyecto

```
project-root/
│
├── docker-compose.yml
│
├── backend/
│   ├── main.py               # FastAPI endpoints
│   └── requirements.txt
│
└── frontend/
    ├── index.html            # UI simple
    ├── script.js             # Grabación + upload al backend
    └── manifest.json         # PWA config
```

---

## 🔌 Endpoints Propuestos (FastAPI)

| Método | Endpoint        | Acción                     |
| ------ | --------------- | -------------------------- |
| `POST` | `/upload-audio` | Recibe y guarda el audio.  |
| `POST` | `/transcribe`   | Llama a Whisper → texto.   |
| `POST` | `/summarize`    | Llama a Mistral → resumen. |
| `POST` | `/to-notion`    | Crea la nota en Notion.    |

---

## 🪄 Prompt Recomendado para el Resumen (Mistral 7B - Ollama)

```
Resume el siguiente texto en un formato claro y estructurado:

1. Resumen breve de la reunión.
2. Puntos clave tratados.
3. Decisiones tomadas.
4. Tareas acordadas y responsables.
Texto:
{{TRANSCRIPCIÓN}}
```

---

## ✅ MVP Funcional = Primera Versión

- PWA con botón “Grabar”.
- Subir audio al backend.
- Transcripción automática.
- Generar resumen automático.
- Crear página en Notion.

---

## 🚀 Mejoras Futuras (Opcionales)

- Multi-usuario / espacios por proyecto.
- Etiquetado automático con embeddings (Local).
- Envío automático por Telegram o Email.
- Resumen diario/semanal.
