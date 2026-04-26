from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import uuid
import os


def _safe_list(data, key):
    value = data.get(key, [])
    return value if isinstance(value, list) else []


def _score_color(score):
    if score >= 85:
        return colors.HexColor("#0F766E")
    if score >= 70:
        return colors.HexColor("#D97706")
    return colors.HexColor("#B91C1C")


def _score_color_hex(score):
    color = _score_color(score)
    red, green, blue = color.rgb()
    return "#%02X%02X%02X" % (int(red * 255), int(green * 255), int(blue * 255))


def _build_bullet_paragraphs(items, style):
    return [Paragraph(f"• {item}", style) for item in items] or [Paragraph("• No items available", style)]

def generate_pdf(data):
    file_name = f"reports/generated/report_{uuid.uuid4()}.pdf"

    os.makedirs("reports/generated", exist_ok=True)

    doc = SimpleDocTemplate(file_name)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="DashboardTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#111827"),
    ))
    styles.add(ParagraphStyle(
        name="SectionLabel",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#111827"),
    ))
    styles.add(ParagraphStyle(
        name="InsightText",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#374151"),
    ))
    styles.add(ParagraphStyle(
        name="Callout",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1F2937"),
    ))

    content = []
    score = int(data.get("score", 0))
    score_color = _score_color(score)
    strengths = _safe_list(data, "strengths")
    weaknesses = _safe_list(data, "weaknesses")
    suggestions = _safe_list(data, "suggestions")
    action_message = data.get("message") or "Try this: focus on measurable achievements, stronger keywords, and a sharper headline."

    content.append(Paragraph("LinkedIn Profile Dashboard", styles["DashboardTitle"]))
    content.append(Spacer(1, 8))
    content.append(Paragraph("A structured snapshot of your profile health, strongest signals, and next actions.", styles["BodyText"]))
    content.append(Spacer(1, 18))

    kpi_data = [
        [Paragraph("<b>Profile Score</b>", styles["BodyText"]), Paragraph("<b>Strengths</b>", styles["BodyText"]), Paragraph("<b>Weaknesses</b>", styles["BodyText"]), Paragraph("<b>Suggestions</b>", styles["BodyText"])],
        [Paragraph(f"<font color='{_score_color_hex(score)}' size='20'><b>{score}/100</b></font>", styles["BodyText"]), Paragraph(f"<b>{len(strengths)}</b>", styles["BodyText"]), Paragraph(f"<b>{len(weaknesses)}</b>", styles["BodyText"]), Paragraph(f"<b>{len(suggestions)}</b>", styles["BodyText"])],
    ]
    kpi_table = Table(kpi_data, colWidths=[130, 110, 110, 110])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
        ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#F0FDF4")),
        ("BACKGROUND", (1, 1), (1, 1), colors.HexColor("#EFF6FF")),
        ("BACKGROUND", (2, 1), (2, 1), colors.HexColor("#FEF2F2")),
        ("BACKGROUND", (3, 1), (3, 1), colors.HexColor("#FFF7ED")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    content.append(kpi_table)
    content.append(Spacer(1, 18))

    dashboard_rows = [
        [Paragraph("<b>Headline</b>", styles["BodyText"]), Paragraph(data.get("improved_headline", ""), styles["InsightText"])],
        [Paragraph("<b>About section</b>", styles["BodyText"]), Paragraph(data.get("improved_about", ""), styles["InsightText"])],
    ]
    dashboard_table = Table(dashboard_rows, colWidths=[110, 380])
    dashboard_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    content.append(Paragraph("Dashboard Summary", styles["SectionLabel"]))
    content.append(Spacer(1, 6))
    content.append(dashboard_table)
    content.append(Spacer(1, 16))

    content.append(Paragraph("Strengths", styles["SectionLabel"]))
    content.extend(_build_bullet_paragraphs(strengths, styles["InsightText"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph("Needs Attention", styles["SectionLabel"]))
    content.extend(_build_bullet_paragraphs(weaknesses, styles["InsightText"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph("Try This Next", styles["SectionLabel"]))
    content.append(Paragraph(action_message, styles["Callout"]))
    content.extend(_build_bullet_paragraphs(suggestions, styles["InsightText"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph("Advanced Recommendations", styles["SectionLabel"]))
    content.append(Paragraph(
        "Use the headline and about section above as a direct rewrite template. Keep the score visible, use numbers in achievements, and repeat your target role keywords naturally.",
        styles["InsightText"],
    ))

    doc.build(content)

    return file_name