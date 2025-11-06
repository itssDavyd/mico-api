import os
import requests

OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://ollama:11434")


def summarize_text(text) -> str:
    prompt = f""" Eres un asistente profesional que genera resúmenes ejecutivos de reuniones en español. A partir del siguiente texto de transcripción, crea un documento claro, completo y organizado, listo para entregar a un cliente. Prioriza la **precisión**, manteniendo todos los conceptos clave que se mencionan. 
    
    Instrucciones: 
    1. Traduce todo a español si no lo está. 
    2. Mantén un lenguaje profesional y formal. 
    3. Resume fielmente únicamente la información que aparece en la transcripción. 
    4. Nunca inventes nombres, fechas, lugares u otra información que no esté presente en el texto. 
    5. Estructura el resumen en secciones numeradas: 
        1. Resumen breve de la reunión. 
        2. Puntos clave tratados. 
        3. Decisiones tomadas. 
        4. Tareas acordadas y responsables. 
        5. Si algún dato no está presente, indícalo de forma neutra ("No se especificó") en lugar de inventarlo. 
        6. Mantén claridad y concisión, pero no elimines detalles importantes de la reunión. 
        
        Texto de transcripción: {text} """

    response = requests.post(
        f"{OLLAMA_URL}/v1/completions",
        json={
            "model": "mistral",
            "prompt": prompt,
            "max_tokens": 500,
            "temperature": 0.3,
        },
    )

    data = response.json()
    summary_text = data.get("choices", [{}])[0].get("text", "")
    return summary_text or "⚠️ Error: no se generó texto"
