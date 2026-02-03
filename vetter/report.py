import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def render_pdf(report_path: str, decision: str, summary: str, findings: list, docs: list):
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    c = canvas.Canvas(report_path, pagesize=A4)
    width, height = A4

    y = height - 60
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "AtlasZA Document Vetting Report")
    y -= 30

    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Decision: {decision}")
    y -= 20
    c.drawString(50, y, f"Summary: {summary[:140]}")
    y -= 30

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Findings:")
    y -= 18
    c.setFont("Helvetica", 10)
    if findings:
        for f in findings[:30]:
            c.drawString(60, y, f"- {f[:120]}")
            y -= 14
            if y < 80:
                c.showPage()
                y = height - 60
    else:
        c.drawString(60, y, "- None")
        y -= 14

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Documents:")
    y -= 18
    c.setFont("Helvetica", 10)

    for d in docs:
        line = f"{d.filename} | {d.doc_type} | {d.decision}"
        c.drawString(60, y, line[:120])
        y -= 14
        if d.missing_fields:
            c.drawString(70, y, f"Missing: {', '.join(d.missing_fields)[:110]}")
            y -= 14
        if y < 80:
            c.showPage()
            y = height - 60

    c.save()
