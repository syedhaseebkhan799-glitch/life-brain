"""
Turn your filled-in template into a PDF.

    python samples/make_my_pdf.py

Reads  samples/my_life_template.txt
Writes samples/my_life_profile.pdf

The PDF is optional -- the app reads .txt directly, so you can upload the
template itself and skip this entirely. This exists because a PDF is easier to
keep, print or move between machines.

Nothing here is uploaded anywhere. Both files stay on this computer, and both
are gitignored so they cannot be committed by accident.
"""
import sys
from pathlib import Path

from fpdf import FPDF

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "my_life_template.txt"
OUT = HERE / "my_life_profile.pdf"

# The how-to block is prose for the person filling this in, and it mentions the
# "->" marker in passing -- which is enough to make its own instructions look
# like answers. Dropped by name so it survives being reworded.
SKIP_SECTIONS = ("HOW TO USE", "MY LIFE PROFILE")


def _is_heading(line: str) -> bool:
    """A section title: short, all caps, no answer on it."""
    stripped = line.strip()
    return (bool(stripped) and stripped.isupper() and len(stripped) < 60
            and "->" not in stripped)


def clean(raw: str):
    """Template text -> the lines worth keeping.

    Two things get dropped, and both matter more than they look. The prose
    instructions at the top are advice to the person filling this in, not facts
    about them -- left in, the model reads "rough notes are fine" as something
    the person said. And a heading with nothing under it is a section they
    chose to skip; carrying "MONEY" followed by silence into every future
    question is noise the model has to wade through to reach the real answers.
    """
    lines = raw.splitlines()

    # Everything before the first section heading is the how-to preamble.
    start = next((i for i, l in enumerate(lines) if _is_heading(l)), 0)

    sections, current, answers = [], None, []
    for line in lines[start:]:
        if _is_heading(line):
            if current and answers:
                sections.append((current, answers))
            current, answers = line.strip(), []
            continue
        if "->" not in line:
            continue  # underlines, blanks, and the parenthetical hints

        label, _, answer = line.partition("->")
        answer = answer.strip()
        if not answer:
            continue  # a blank they left on purpose
        # "Born in (city, country) -> Lahore" reads better to the model as
        # "Born in: Lahore" than with the arrow and the prompt still attached.
        label = label.split("(")[0].strip()
        answers.append(f"{label}: {answer}" if label else answer)

    if current and answers:
        sections.append((current, answers))

    kept = []
    for heading, answer_lines in sections:
        if any(skip in heading for skip in SKIP_SECTIONS):
            continue
        kept.append(heading)
        kept.extend(answer_lines)
        kept.append("")
    return kept


def build() -> Path:
    if not SOURCE.exists():
        sys.exit(f"Fill in {SOURCE.name} first — it is not there.")

    raw = SOURCE.read_text(encoding="utf-8", errors="replace")
    lines = clean(raw)

    answers = [l for l in lines if ":" in l and not _is_heading(l)]
    if len(answers) < 3:
        sys.exit(
            f"{SOURCE.name} looks like it hasn't been filled in yet — I found "
            f"almost no answers. Add some text after the '->' marks and rerun."
        )

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    width = pdf.w - pdf.l_margin - pdf.r_margin

    for line in lines:
        if not line.strip():
            pdf.ln(3)
            continue

        heading = _is_heading(line)
        pdf.set_font("Helvetica", "B" if heading else "", 13 if heading else 11)
        pdf.set_x(pdf.l_margin)
        if heading and pdf.get_y() > 250:
            pdf.add_page()
        # fpdf's core fonts are latin-1 only; a smart quote or emoji pasted
        # from elsewhere would otherwise abort the whole build.
        pdf.multi_cell(width, 8 if heading else 6,
                       line.encode("latin-1", "replace").decode("latin-1"))
        if heading:
            pdf.ln(1)

    pdf.output(str(OUT))
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"wrote {path} ({path.stat().st_size:,} bytes)")
    print("Upload it at http://localhost:8502")
