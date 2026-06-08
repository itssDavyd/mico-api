import json
import logging

import httpx
from pydantic import ValidationError

from config import get_settings
from models.schemas import MeetingSummary

logger = logging.getLogger(__name__)

SUMMARY_SCHEMA = MeetingSummary.model_json_schema()

CHUNK_PROMPT = """Eres un asistente comercial experto. Analiza este fragmento de una conversación de venta en español.
Extrae SOLO información explícita del texto. No inventes productos, precios, nombres ni compromisos.

Responde en JSON con estas claves:
- brief: resumen breve del fragmento
- products_discussed: productos o servicios mencionados
- customer_needs: necesidades o requisitos del cliente
- objections: objeciones, dudas o resistencias del cliente
- key_points: puntos importantes de la conversación
- agreements: acuerdos o confirmaciones explícitas
- action_items: lista de {{"task": "...", "responsible": "..." o null}}
- opportunities: oportunidades de venta o aspectos positivos
- missing_info: datos relevantes no mencionados

Fragmento:
{text}"""

MERGE_PROMPT = """Eres un asistente comercial experto. Consolida estos resúmenes parciales de una misma visita de venta
en un único acta comercial en español, sin duplicados y sin inventar información.

Responde en JSON con:
- brief: resumen ejecutivo de la visita comercial
- products_discussed: productos/servicios tratados
- customer_needs: necesidades del cliente detectadas
- objections: objeciones o dudas planteadas
- key_points: puntos clave de la conversación
- agreements: acuerdos alcanzados
- action_items: próximos pasos con {{"task": "...", "responsible": "..." o null}}
- opportunities: oportunidades comerciales detectadas
- missing_info: información relevante no especificada

Resúmenes parciales:
{partials}"""


def _split_text(text: str, chunk_size: int) -> list[str]:
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            split_at = text.rfind(". ", start, end)
            if split_at > start + chunk_size // 2:
                end = split_at + 1
        chunks.append(text[start:end].strip())
        start = end

    return [c for c in chunks if c]


def _call_ollama(prompt: str) -> dict:
    settings = get_settings()
    url = f"{settings.ollama_host.rstrip('/')}/api/chat"

    payload = {
        "model": settings.ollama_model,
        "messages": [{"role": "user", "content": prompt}],
        "format": SUMMARY_SCHEMA,
        "stream": False,
        "options": {
            "temperature": settings.ollama_temperature,
            "num_predict": settings.ollama_num_predict,
        },
    }

    with httpx.Client(timeout=settings.ollama_timeout) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    content = data.get("message", {}).get("content", "")
    if not content:
        raise ValueError("Ollama returned empty response")

    return json.loads(content)


def _parse_summary(data: dict) -> MeetingSummary:
    try:
        return MeetingSummary.model_validate(data)
    except ValidationError as exc:
        logger.warning("Invalid summary JSON from Ollama: %s", exc)
        return MeetingSummary(
            brief=data.get("brief", "Resumen no disponible"),
            products_discussed=data.get("products_discussed", []),
            customer_needs=data.get("customer_needs", []),
            objections=data.get("objections", []),
            key_points=data.get("key_points", []),
            agreements=data.get("agreements", data.get("decisions", [])),
            action_items=data.get("action_items", []),
            opportunities=data.get("opportunities", data.get("strengths", [])),
            missing_info=data.get("missing_info", []),
        )


def _merge_summaries(partials: list[MeetingSummary]) -> MeetingSummary:
    if len(partials) == 1:
        return partials[0]

    partials_text = json.dumps(
        [p.model_dump() for p in partials],
        ensure_ascii=False,
        indent=2,
    )
    merged = _call_ollama(MERGE_PROMPT.format(partials=partials_text))
    return _parse_summary(merged)


def summarize_text(text: str) -> MeetingSummary:
    if not text.strip():
        raise ValueError("Empty transcript cannot be summarized")

    settings = get_settings()
    chunks = _split_text(text, settings.ollama_chunk_chars)

    partials: list[MeetingSummary] = []
    for i, chunk in enumerate(chunks, start=1):
        logger.info("Summarizing chunk %d/%d", i, len(chunks))
        raw = _call_ollama(CHUNK_PROMPT.format(text=chunk))
        partials.append(_parse_summary(raw))

    return _merge_summaries(partials)
