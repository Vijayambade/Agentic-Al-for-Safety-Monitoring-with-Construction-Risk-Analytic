from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER


def generate_pdf(report_title, report_content):
    """
    Generate a PDF report and return it as bytes.
    """

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    title_style = styles["Heading1"]
    title_style.alignment = TA_CENTER

    heading = styles["Heading2"]

    body = styles["BodyText"]

    story = []

    story.append(Paragraph(report_title, title_style))
    story.append(Paragraph("<br/><br/>", body))

    sections = report_content.split("\n")

    for line in sections:

        line = line.strip()

        if line == "":
            continue

        if line.endswith(":"):

            story.append(Paragraph(f"<b>{line}</b>", heading))

        else:

            story.append(Paragraph(line, body))

    doc.build(story)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf