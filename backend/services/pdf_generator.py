import os
from datetime import datetime
from uuid import UUID

from fpdf import FPDF

from config import get_settings
from models.schemas import MeetingSummary, TranscriptionResult

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _safe_section(pdf: FPDF, title: str, items: list[str], bullet: bool = True) -> None:
    if not items:
        return

    pdf.set_font("DejaVu", "B", 12)
    pdf.ln(4)
    pdf.cell(0, 8, title, ln=True)
    pdf.set_font("DejaVu", "", 11)

    for item in items:
        prefix = "• " if bullet else ""
        pdf.multi_cell(0, 7, f"{prefix}{item}")


def generate_pdf(
    process_id: UUID,
    original_filename: str,
    summary: MeetingSummary,
    transcript: TranscriptionResult | None = None,
    include_transcript: bool = False,
) -> str:
    settings = get_settings()
    os.makedirs(settings.pdf_dir, exist_ok=True)

    base_name = os.path.splitext(original_filename)[0]
    safe_base = "".join(c if c.isalnum() or c in "-_" else "_" for c in base_name)[:60]
    pdf_filename = f"{process_id}_{safe_base}.pdf"
    pdf_path = os.path.join(settings.pdf_dir, pdf_filename)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.add_font("DejaVu", "", FONT_REGULAR, uni=True)
    pdf.add_font("DejaVu", "B", FONT_BOLD, uni=True)

    logo_path = os.path.join("./assets", "logo.png")
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=45)
        pdf.ln(22)
    else:
        pdf.ln(5)

    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "Acta de Visita Comercial", ln=True, align="C")

    pdf.set_font("DejaVu", "", 10)
    pdf.cell(
        0,
        6,
        f"Origen: {original_filename}  |  Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        ln=True,
        align="C",
    )
    pdf.ln(6)

    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 8, "1. Resumen de la visita", ln=True)
    pdf.set_font("DejaVu", "", 11)
    pdf.multi_cell(0, 7, summary.brief)

    _safe_section(pdf, "2. Productos y servicios tratados", summary.products_discussed)
    _safe_section(pdf, "3. Necesidades del cliente", summary.customer_needs)
    _safe_section(pdf, "4. Objeciones y dudas", summary.objections)
    _safe_section(pdf, "5. Puntos clave de la conversación", summary.key_points)
    _safe_section(pdf, "6. Acuerdos alcanzados", summary.agreements)

    if summary.action_items:
        pdf.set_font("DejaVu", "B", 12)
        pdf.ln(4)
        pdf.cell(0, 8, "7. Próximos pasos", ln=True)
        pdf.set_font("DejaVu", "", 11)
        for item in summary.action_items:
            responsible = item.responsible or "No especificado"
            pdf.multi_cell(0, 7, f"• {item.task} (Responsable: {responsible})")

    _safe_section(pdf, "8. Oportunidades comerciales", summary.opportunities)

    if summary.missing_info:
        _safe_section(pdf, "9. Información no especificada", summary.missing_info)

    if include_transcript and transcript and transcript.text:
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 10, "Anexo: Transcripción", ln=True)
        pdf.set_font("DejaVu", "", 10)
        pdf.multi_cell(0, 6, transcript.text)

    pdf.set_font("DejaVu", "", 9)
    pdf.set_y(-15)
    pdf.cell(
        0,
        10,
        "Documento generado automáticamente por MICO AI",
        align="C",
    )

    pdf.output(pdf_path)
    return pdf_filename
