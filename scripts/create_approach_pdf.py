from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


OUT = Path("deliverables/redrob_candidate_ranker_approach.pdf")
PAGE = (12.8 * inch, 7.2 * inch)

INK = colors.HexColor("#17212B")
MUTED = colors.HexColor("#5B6570")
BLUE = colors.HexColor("#2563EB")
GREEN = colors.HexColor("#16A34A")
ORANGE = colors.HexColor("#EA580C")
RED = colors.HexColor("#DC2626")
PAPER = colors.HexColor("#F8FAFC")
LINE = colors.HexColor("#CBD5E1")


def write_text(c, text, x, y, size=16, color=INK, bold=False, leading=None, max_width=90):
    font = "Helvetica-Bold" if bold else "Helvetica"
    c.setFont(font, size)
    c.setFillColor(color)
    leading = leading or size * 1.25
    words = text.split()
    line = ""
    for word in words:
        test = f"{line} {word}".strip()
        if c.stringWidth(test, font, size) <= max_width:
            line = test
        else:
            c.drawString(x, y, line)
            y -= leading
            line = word
    if line:
        c.drawString(x, y, line)
    return y - leading


def title(c, kicker, claim):
    c.setFillColor(BLUE)
    c.rect(52, 630, 8, 8, fill=1, stroke=0)
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(68, 627, kicker)
    write_text(c, claim, 52, 590, 30, INK, True, max_width=820)


def footer(c, n):
    c.setStrokeColor(LINE)
    c.line(52, 42, 870, 42)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawString(52, 25, "Redrob AI Candidate Ranker | deterministic offline CPU ranking")
    c.drawRightString(870, 25, str(n))


def box(c, x, y, w, h, label, body, color=BLUE):
    c.setFillColor(colors.white)
    c.setStrokeColor(LINE)
    c.roundRect(x, y, w, h, 6, fill=1, stroke=1)
    c.setFillColor(color)
    c.rect(x, y + h - 8, w, 8, fill=1, stroke=0)
    write_text(c, label, x + 16, y + h - 32, 13, INK, True, max_width=w - 32)
    write_text(c, body, x + 16, y + h - 58, 10.5, MUTED, max_width=w - 32, leading=14)


def metric(c, x, y, value, label, color):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(x, y, value)
    write_text(c, label, x, y - 22, 10.5, MUTED, max_width=130, leading=13)


def slide1(c):
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE[0], PAGE[1], fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.rect(52, 92, 210, 10, fill=1, stroke=0)
    write_text(c, "Career-first candidate ranking", 52, 520, 44, INK, True, max_width=680)
    write_text(c, "A deterministic AI recruiting ranker that reads career evidence, logistics, and behavioral availability before trusting skills keywords.", 56, 440, 18, MUTED, max_width=650, leading=25)
    metric(c, 620, 440, "100k", "candidate pool ranked offline", BLUE)
    metric(c, 620, 340, "<5 min", "CPU-only challenge constraint", GREEN)
    metric(c, 620, 240, "Top 100", "validated CSV with specific reasoning", ORANGE)
    footer(c, 1)


def slide2(c):
    title(c, "ROLE INTERPRETATION", "The JD is asking for shipped intelligence systems, not AI vocabulary.")
    write_text(c, "The hidden trap is obvious from the bundle: many candidates list AI skills, but the role needs a founding Senior AI Engineer who has deployed retrieval, ranking, search, and evaluation systems.", 52, 520, 15, MUTED, max_width=790, leading=22)
    box(c, 70, 310, 240, 120, "Must-have evidence", "Embeddings retrieval, vector or hybrid search, Python, production ranking evaluation.", BLUE)
    box(c, 340, 310, 240, 120, "Positive signals", "Product-company ML work, shipped systems, A/B tests, recommender/search ownership.", GREEN)
    box(c, 610, 310, 240, 120, "Risk signals", "Keyword stuffing, services-only history, pure CV/speech focus, inactive candidates.", RED)
    footer(c, 2)


def slide3(c):
    title(c, "SYSTEM DESIGN", "A two-stage offline pipeline keeps quality high and runtime predictable.")
    labels = [
        ("Candidate JSONL", "stream 100k profiles"),
        ("Feature Extractor", "career, skills, signals, risks"),
        ("Career Rubric", "JD evidence scoring"),
        ("Behavior Modifier", "availability and logistics"),
        ("Reasoning Writer", "specific CSV explanations"),
    ]
    x = 55
    for i, (head, body) in enumerate(labels):
        box(c, x, 325, 145, 105, head, body, [BLUE, GREEN, ORANGE, BLUE, GREEN][i])
        if i < len(labels) - 1:
            c.setStrokeColor(MUTED)
            c.setLineWidth(2)
            c.line(x + 145, 378, x + 175, 378)
        x += 175
    write_text(c, "The ranking step uses no hosted LLM calls and no GPU. Semantic intent is represented through explicit evidence categories aligned to the JD.", 72, 245, 15, MUTED, max_width=760, leading=22)
    footer(c, 3)


def slide4(c):
    title(c, "SCORING RUBRIC", "Career evidence carries the ranking; skills only corroborate it.")
    items = [
        ("Career evidence", 35, BLUE),
        ("Role/title fit", 15, GREEN),
        ("Product company fit", 10, ORANGE),
        ("Logistics", 10, BLUE),
        ("Behavioral signals", 20, GREEN),
        ("Skill validation", 10, ORANGE),
    ]
    y = 480
    for label, value, color in items:
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 12)
        c.drawString(80, y + 5, label)
        c.setFillColor(colors.HexColor("#E2E8F0"))
        c.rect(250, y, 420, 20, fill=1, stroke=0)
        c.setFillColor(color)
        c.rect(250, y, 420 * value / 35, 20, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(720, y + 5, f"{value}%")
        y -= 50
    write_text(c, "Penalties subtract risk for services-only careers, non-target titles with inflated AI skills, inactivity, long notice periods, and honeypot-like skill contradictions.", 80, 135, 14, MUTED, max_width=760, leading=20)
    footer(c, 4)


def slide5(c):
    title(c, "TRAP RESISTANCE", "The system down-ranks profiles that look perfect only to keyword filters.")
    box(c, 70, 390, 250, 120, "Keyword stuffing", "Many AI skills but weak career evidence or non-technical title triggers a strong penalty.", RED)
    box(c, 340, 390, 250, 120, "Honeypot signals", "Advanced/expert skills with near-zero duration are treated as profile-risk evidence.", ORANGE)
    box(c, 610, 390, 250, 120, "Availability gaps", "Inactive profiles, slow responses, and 90-120 day notice periods reduce rank.", BLUE)
    write_text(c, "This mirrors how a strong recruiter reads: the profile must show actual shipped work, not just a dense skill inventory.", 86, 270, 18, INK, True, max_width=720, leading=24)
    footer(c, 5)


def slide6(c):
    title(c, "OUTPUT", "The deliverable is reproducible, validated, and recruiter-readable.")
    metric(c, 90, 470, "100", "rows in final submission.csv", BLUE)
    metric(c, 310, 470, "valid", "passes the official validator", GREEN)
    metric(c, 530, 470, "specific", "reasoning cites fit and concerns", ORANGE)
    write_text(c, "Run command: python rank.py --candidates ./data/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl --out ./submission.csv", 92, 310, 13, INK, max_width=735, leading=18)
    write_text(c, "The repo is intentionally small: feature extraction, scoring, reasoning, and CLI are separated so the methodology is easy to defend in review.", 92, 220, 15, MUTED, max_width=735, leading=22)
    footer(c, 6)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=PAGE)
    for slide in [slide1, slide2, slide3, slide4, slide5, slide6]:
        slide(c)
        c.showPage()
    c.save()
    print(OUT)


if __name__ == "__main__":
    main()

