# PDF generator for daily print using ReportLab
# Magazine/modern style with Montserrat typography

import io
import os
from datetime import date
from dataclasses import dataclass

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import simpleSplit

from typing import TYPE_CHECKING
from data_sources.weather import WeatherData

if TYPE_CHECKING:
    from data_sources.claude_summarizer import CuratedNews


# Typography
COLOURS = {
    "primary": "#1A1D21",
    "secondary": "#4A5568",
    "muted": "#718096",
    "divider": "#E2E8F0",
}

FONTS = {
    "bold": "Montserrat-Bold",
    "semibold": "Montserrat-SemiBold",
    "medium": "Montserrat-Medium",
    "light": "Montserrat-Light",
}


def get_font_path(font_filename: str) -> str:
    """Find font file in fonts directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(current_dir, "fonts", font_filename)
    if os.path.exists(font_path):
        return font_path
    raise FileNotFoundError(f"Font file '{font_filename}' not found")


def register_fonts():
    """Register Montserrat fonts with ReportLab."""
    fonts = [
        ("Montserrat-Medium", "Montserrat-Medium.ttf"),
        ("Montserrat-SemiBold", "Montserrat-SemiBold.ttf"),
        ("Montserrat-Bold", "Montserrat-Bold.ttf"),
        ("Montserrat-Light", "Montserrat-Light.ttf"),
    ]
    for font_name, font_filename in fonts:
        try:
            font_path = get_font_path(font_filename)
            pdfmetrics.registerFont(TTFont(font_name, font_path))
        except Exception as e:
            print(f"Warning: Could not register font {font_name}: {e}")


def draw_text(c, x, y, text, font="Montserrat-Medium", size=10, colour="#1A1D21", align="left", max_width=None):
    """Draw text with optional wrapping."""
    c.setFillColor(HexColor(colour))
    c.setFont(font, size)

    if max_width and stringWidth(text, font, size) > max_width:
        line_height = size * 1.3
        lines = simpleSplit(text, font, size, max_width)
        for line in lines:
            c.drawString(x, y, line)
            y -= line_height
        return y + line_height  # Return final y position
    else:
        if align == "right":
            x = x - stringWidth(text, font, size)
        elif align == "center":
            x = x - stringWidth(text, font, size) / 2
        c.drawString(x, y, text)
        return y


def draw_divider(c, x1, x2, y, colour="#E2E8F0"):
    """Draw a subtle horizontal divider."""
    c.setStrokeColor(HexColor(colour))
    c.setLineWidth(0.5)
    c.line(x1, y, x2, y)


@dataclass
class Highlight:
    """A Readwise highlight."""
    text: str
    title: str
    author: str


@dataclass
class DailyContent:
    """All content for the daily print."""
    date: date
    weather: WeatherData | None
    news: "CuratedNews"
    readings: list[str] | None  # None on weekends
    verse: tuple[str, str] | None = None  # (text, reference)
    highlight: Highlight | None = None


def generate_pdf(content: DailyContent) -> bytes:
    """Generate the daily PDF and return as bytes."""
    register_fonts()

    buffer = io.BytesIO()
    page_width, page_height = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    # Margins
    margin_left = 2 * cm
    margin_right = page_width - 2 * cm
    margin_top = page_height - 1.5 * cm
    content_width = margin_right - margin_left

    y = margin_top

    # === HEADER: Date on left, Weather on right ===
    day_name = content.date.strftime("%A").upper()
    date_str = content.date.strftime("%-d %B %Y")

    # Date (left side)
    draw_text(c, margin_left, y, day_name,
              font=FONTS["bold"], size=28, colour=COLOURS["primary"])

    # Weather (right side, same line as day name)
    if content.weather:
        w = content.weather
        temp_text = f"{int(w.temperature)}°C"
        draw_text(c, margin_right, y, temp_text,
                  font=FONTS["semibold"], size=28, colour=COLOURS["primary"], align="right")

        # Condition below temp
        draw_text(c, margin_right, y - 8 * mm, w.condition,
                  font=FONTS["medium"], size=10, colour=COLOURS["secondary"], align="right")

        # High/Low below condition
        hi_lo = f"H {int(w.high)}°  L {int(w.low)}°"
        draw_text(c, margin_right, y - 14 * mm, hi_lo,
                  font=FONTS["light"], size=8, colour=COLOURS["muted"], align="right")

    y -= 9 * mm

    # Date and location (below day name)
    draw_text(c, margin_left, y, date_str,
              font=FONTS["medium"], size=12, colour=COLOURS["secondary"])
    y -= 5 * mm

    draw_text(c, margin_left, y, "Witney, Oxfordshire",
              font=FONTS["light"], size=9, colour=COLOURS["muted"])
    y -= 8 * mm

    # Divider
    draw_divider(c, margin_left, margin_right, y)
    y -= 8 * mm

    # === NEWS SECTION ===
    # Define safe zones
    inspiration_top = 7 * cm  # Don't go below this for news

    draw_text(c, margin_left, y, "THE GUARDIAN",
              font=FONTS["bold"], size=9, colour=COLOURS["secondary"])
    y -= 8 * mm

    news = content.news
    if news and (news.top_stories or news.third_story or news.headlines):
        # Top 2 stories with detailed summaries (full width)
        for item in news.top_stories:
            if y < inspiration_top + 3 * cm:
                break

            # Headline
            y = draw_text(c, margin_left, y, item.headline,
                          font=FONTS["semibold"], size=11, colour=COLOURS["primary"],
                          max_width=content_width)
            y -= 5 * mm

            # Detailed summary
            y = draw_text(c, margin_left, y, item.summary,
                          font=FONTS["medium"], size=8, colour=COLOURS["secondary"],
                          max_width=content_width)
            y -= 8 * mm

        # Two-column section: 3rd story (left) + In Brief (right)
        if y > inspiration_top + 1 * cm and (news.third_story or news.headlines):
            col_width = (content_width - 8 * mm) / 2
            left_x = margin_left
            right_x = margin_left + col_width + 8 * mm
            two_col_y = y

            # LEFT COLUMN: Third story (shorter)
            if news.third_story:
                two_col_y_left = two_col_y
                two_col_y_left = draw_text(c, left_x, two_col_y_left, news.third_story.headline,
                                            font=FONTS["semibold"], size=10, colour=COLOURS["primary"],
                                            max_width=col_width)
                two_col_y_left -= 4 * mm
                draw_text(c, left_x, two_col_y_left, news.third_story.summary,
                          font=FONTS["medium"], size=8, colour=COLOURS["secondary"],
                          max_width=col_width)

            # RIGHT COLUMN: In Brief headlines
            if news.headlines:
                two_col_y_right = two_col_y
                draw_text(c, right_x, two_col_y_right, "IN BRIEF",
                          font=FONTS["bold"], size=8, colour=COLOURS["muted"])
                two_col_y_right -= 5 * mm

                for headline in news.headlines:
                    if two_col_y_right < inspiration_top:
                        break
                    draw_text(c, right_x, two_col_y_right, "•",
                              font=FONTS["medium"], size=8, colour=COLOURS["muted"])
                    two_col_y_right = draw_text(c, right_x + 3 * mm, two_col_y_right, headline,
                                                 font=FONTS["medium"], size=8, colour=COLOURS["primary"],
                                                 max_width=col_width - 3 * mm)
                    two_col_y_right -= 4 * mm
    else:
        draw_text(c, margin_left, y, "News unavailable",
                  font=FONTS["medium"], size=10, colour=COLOURS["muted"])
        y -= 12 * mm

    # === INSPIRATION SECTION (highlight above footer) ===
    if content.highlight:
        h = content.highlight
        inspiration_y = 6.5 * cm

        draw_divider(c, margin_left, margin_right, inspiration_y + 10 * mm)

        # Quote text - larger, italicized feel
        text = h.text if len(h.text) <= 250 else h.text[:247] + "..."
        inspiration_y = draw_text(c, margin_left + 5 * mm, inspiration_y, f'"{text}"',
                                   font=FONTS["light"], size=10, colour=COLOURS["primary"],
                                   max_width=content_width - 10 * mm)
        inspiration_y -= 6 * mm

        # Attribution - right aligned
        draw_text(c, margin_right, inspiration_y, f"— {h.author}",
                  font=FONTS["semibold"], size=9, colour=COLOURS["secondary"], align="right")
        draw_text(c, margin_right, inspiration_y - 4 * mm, h.title,
                  font=FONTS["light"], size=8, colour=COLOURS["muted"], align="right")

    # === FOOTER SECTION (verse + readings) ===
    footer_y = 3 * cm

    draw_divider(c, margin_left, margin_right, footer_y + 8 * mm)

    # Bible verse and readings side by side
    mid_x = page_width / 2

    # Verse (left side)
    if content.verse:
        verse_text, verse_ref = content.verse
        # Shorter verse display
        short_verse = verse_text if len(verse_text) <= 80 else verse_text[:77] + "..."
        footer_y_left = draw_text(c, margin_left, footer_y, f'"{short_verse}"',
                                   font=FONTS["light"], size=9, colour=COLOURS["primary"],
                                   max_width=mid_x - margin_left - 10 * mm)
        draw_text(c, margin_left, footer_y_left - 4 * mm, f"— {verse_ref}",
                  font=FONTS["medium"], size=8, colour=COLOURS["muted"])

    # Readings (right side)
    draw_text(c, mid_x + 5 * mm, footer_y, "TODAY'S READINGS",
              font=FONTS["bold"], size=8, colour=COLOURS["secondary"])

    if content.readings:
        valid_readings = [r for r in content.readings if r]
        if valid_readings:
            readings_text = "  ·  ".join(valid_readings)
            draw_text(c, mid_x + 5 * mm, footer_y - 5 * mm, readings_text,
                      font=FONTS["medium"], size=10, colour=COLOURS["primary"])
        else:
            draw_text(c, mid_x + 5 * mm, footer_y - 5 * mm, "End of year",
                      font=FONTS["light"], size=9, colour=COLOURS["muted"])
    else:
        draw_text(c, mid_x + 5 * mm, footer_y - 5 * mm, "Weekend",
                  font=FONTS["light"], size=9, colour=COLOURS["muted"])

    # Finish
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()
