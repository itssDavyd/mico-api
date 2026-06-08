import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from config import get_settings

router = APIRouter()


def _safe_filename(filename: str) -> str:
    name = Path(filename).name
    if name != filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Nombre de archivo inválido")
    if not name.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
    return name


@router.get("/list")
def list_files() -> dict[str, list[str]]:
    settings = get_settings()
    os.makedirs(settings.pdf_dir, exist_ok=True)
    files = os.listdir(settings.pdf_dir)

    return {
        "files": sorted(
            [f for f in files if f.endswith(".pdf")],
            key=lambda x: os.path.getmtime(os.path.join(settings.pdf_dir, x)),
            reverse=True,
        )
    }


@router.get("/download/{filename}")
def download_file(filename: str) -> FileResponse:
    settings = get_settings()
    safe_name = _safe_filename(filename)
    file_path = os.path.join(settings.pdf_dir, safe_name)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=safe_name,
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )


@router.delete("/delete/{filename}")
async def delete_file(filename: str) -> dict[str, str]:
    settings = get_settings()
    safe_name = _safe_filename(filename)
    file_path = os.path.join(settings.pdf_dir, safe_name)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    try:
        os.remove(file_path)
        return {"message": "Documento eliminado correctamente"}
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {exc}") from exc
