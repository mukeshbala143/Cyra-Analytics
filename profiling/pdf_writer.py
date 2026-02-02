from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

import tempfile
import matplotlib.pyplot as plt


def generate_pdf_report(md_text, chart_paths):
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(
        temp_pdf.name,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    story = []

    # ---- Markdown → simple paragraphs ----
    for line in md_text.split("\n"):
        if line.strip():
            story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 8))

    story.append(Spacer(1, 20))

    # ---- Charts ----
    for path in chart_paths:
        story.append(Image(path, width=5*inch, height=3*inch))
        story.append(Spacer(1, 20))

    doc.build(story)
    return temp_pdf.name
