import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

pdf_dir = os.getenv("PDF_DIR", "./pdfs")


@router.get("/list")
def list_files() -> dict[str, list[str]]:
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
    files = os.listdir(pdf_dir)

    return {
        "files": sorted(
            [f for f in files if f != ".gitkeep"],
            key=lambda x: os.path.getmtime(os.path.join(pdf_dir, x)),
            reverse=True,
        )
    }


@router.get("/download/{filename}")
def download_file(filename: str) -> FileResponse:
    file_path = os.path.join(pdf_dir, filename)

    return FileResponse(file_path, media_type="application/pdf", filename=filename)


@router.delete("/delete/{filename}")
async def delete_file(filename: str) -> dict[str, str]:
    file_path = os.path.join(pdf_dir, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    try:
        os.remove(file_path)
        return {"message": "Archivo eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {e}")
