import os
from typing import Any
from fastapi import APIRouter, UploadFile, File
from services.pdf_generator import generate_pdf
from services.summarize import summarize_text
from services.transcription import transcribe_audio
from background import process_status, start_background_task, create_process_id

router = APIRouter()

audio_dir = os.getenv("AUDIO_DIR", "./audio")


def background_job(file_path, filename, process_id) -> None:
    try:
        text = transcribe_audio(file_path)
        summary = summarize_text(text)
        pdf_path = generate_pdf(filename, summary)

        process_status[process_id]["status"] = "done"
        process_status[process_id]["pdf_path"] = pdf_path

    except Exception as e:
        process_status[process_id]["status"] = "error"
        process_status[process_id]["pdf_path"] = None
        print(f"Error en proceso {process_id}:", e)


@router.post("/process")
async def process_audio(file: UploadFile = File(...)) -> dict[str, str]:
    os.makedirs(audio_dir, exist_ok=True)

    process_id = create_process_id()
    file_path = os.path.join(audio_dir, f"{process_id}_{file.filename}")

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    start_background_task(background_job, file_path, file.filename, process_id)

    return {"process_id": process_id, "status": "processing"}


@router.get("/status/{process_id}")
async def check_status(process_id: str) -> dict[str, str] | Any:
    if process_id not in process_status:
        return {"error": "Invalid process_id"}

    return process_status[process_id]
