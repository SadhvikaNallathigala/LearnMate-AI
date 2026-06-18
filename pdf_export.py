"""
pdf_export.py
-------------
Converts Markdown content to a downloadable PDF using fpdf2.
Falls back gracefully if fpdf2 is not installed.
"""

import re
from typing import Optional


def markdown_to_plain(md: str) -> str:
    """Strip Markdown and unicode for PDF-safe plain text (latin-1 only)."""
    text = re.sub(r"#{1,6}\s*", "", md)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    for src, dst in {
        "\u2014": "-", "\u2013": "-", "\u2012": "-",
        "\u2019": "'", "\u2018": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2022": "-", "\u00b7": "-",
        "\u2192": "->", "\u2190": "<-",
        "\u2713": "OK", "\u2714": "OK",
        "\u2705": "[YES]", "\u274c": "[NO]", "\u2717": "[NO]",
        "\u26a0": "(!)",
    }.items():
        text = text.replace(src, dst)
    text = text.encode("latin-1", errors="ignore").decode("latin-1")
    text = re.sub(r"^[-*]\s+", "- ", text, flags=re.MULTILINE)
    return text.strip()


def generate_pdf(title: str, content: str) -> Optional[bytes]:
    """
    Generate a PDF from a title and Markdown content string.
    Returns PDF bytes on success, or None on failure/missing dependency.
    """
    try:
        from fpdf import FPDF

        class PDF(FPDF):
            def header(self):
                self.set_font("Helvetica", "B", 12)
                self.set_text_color(30, 30, 80)
                self.cell(
                    0, 8, "AI Student Learning Assistant",
                    align="C", new_x="LMARGIN", new_y="NEXT"
                )
                self.ln(2)

            def footer(self):
                self.set_y(-12)
                self.set_font("Helvetica", "I", 8)
                self.set_text_color(150, 150, 150)
                self.cell(0, 8, f"Page {self.page_no()}", align="C")

        pdf = PDF("P", "mm", "A4")
        pdf.set_margins(20, 20, 20)
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=25)

        # Title
        safe_title = title.encode("latin-1", errors="ignore").decode("latin-1")
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(20, 20, 100)
        pdf.multi_cell(0, 8, safe_title)
        pdf.ln(4)

        # Body content
        plain = markdown_to_plain(content)
        for line in plain.split("\n"):
            stripped = line.strip()
            if not stripped:
                pdf.ln(2)
                continue
            pdf.set_x(pdf.l_margin)  # always reset x before each cell
            if stripped.isupper() and len(stripped) < 60:
                pdf.set_font("Helvetica", "B", 11)
                pdf.set_text_color(30, 30, 100)
                pdf.multi_cell(0, 6, stripped)
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(40, 40, 40)
            else:
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(40, 40, 40)
                pdf.multi_cell(0, 6, stripped)

        return bytes(pdf.output())
    except ImportError:
        return None
    except Exception:
        return None
