from datetime import datetime
import os
from fpdf import FPDF

pdf_dir = os.getenv("PDF_DIR", "./pdfs")


def generate_pdf(file_name, summary_text) -> str:
    os.makedirs(pdf_dir, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    pdf_file_path = os.path.join(
        pdf_dir,
        f"{date_str}.pdf",
    )

    pdf = FPDF()
    pdf.add_page()

    # Fuentes UTF-8
    pdf.add_font(
        "DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True
    )
    pdf.add_font(
        "DejaVu", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", uni=True
    )

    # Logo
    logo_path = os.path.join("./assets", "logo.png")
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=50)

    pdf.set_font("DejaVu", "B", 16)
    pdf.ln(25)
    pdf.cell(0, 10, "Resumen de Reunión", ln=True, align="C")

    pdf.set_font("DejaVu", "", 12)
    pdf.ln(5)
    pdf.multi_cell(0, 8, summary_text)

    pdf.set_font("DejaVu", "", 10)
    pdf.set_y(-15)
    pdf.cell(
        0,
        10,
        "Documento generado automáticamente por MICO AI & Ledmon Marketing",
        align="C",
    )

    pdf.output(pdf_file_path)
    return pdf_file_path
