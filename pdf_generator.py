# PDF generator for daily print using ReportLab
# Magazine/modern style with Montserrat typography

import io
import logging
import os
from datetime import date
from reportlab.lib.colors import HexColor

logger = logging.getLogger(__name__)
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import simpleSplit

from dataclasses import dataclass
from typing import TYPE_CHECKING

from data_sources.readwise import Highlight
from data_sources.weather import LOCATION_NAME, WeatherData

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
    registered_count = 0
    for font_name, font_filename in fonts:
        try:
            font_path = get_font_path(font_filename)
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            registered_count += 1
        except Exception as e:
            logger.error(f"Could not register font {font_name}: {e}")

    if registered_count == 0:
        raise RuntimeError(
            f"No fonts could be registered. PDF generation requires at least one "
            f"Montserrat font in the 'fonts' directory. Expected fonts: "
            f"{', '.join(f[1] for f in fonts)}"
        )


def draw_text(
    c: canvas.Canvas,
    x: float,
    y: float,
    text: str,
    font: str = "Montserrat-Medium",
    size: int = 10,
    colour: str = "#1A1D21",
    align: str = "left",
    max_width: float | None = None,
) -> float:
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


def draw_divider(c: canvas.Canvas, x1: float, x2: float, y: float, colour: str = "#E2E8F0") -> None:
    """Draw a subtle horizontal divider."""
    c.setStrokeColor(HexColor(colour))
    c.setLineWidth(0.5)
    c.line(x1, y, x2, y)


def truncate_text(text: str, max_length: int) -> str:
    """Truncate text at word boundary, adding ellipsis if truncated."""
    if len(text) <= max_length:
        return text
    # Find last space before limit, leaving room for "..."
    truncated = text[:max_length - 3]
    last_space = truncated.rfind(' ')
    if last_space > max_length // 2:  # Only use word boundary if reasonable
        truncated = truncated[:last_space]
    return truncated + "..."


def measure_text_height(
    text: str,
    font: str = "Montserrat-Medium",
    size: int = 10,
    max_width: float | None = None,
) -> float:
    """Calculate the height text will occupy when rendered (with wrapping)."""
    if not text:
        return 0
    line_height = size * 1.3
    if max_width and stringWidth(text, font, size) > max_width:
        lines = simpleSplit(text, font, size, max_width)
        return line_height * len(lines)
    return line_height


def _measure_news_height(news: "CuratedNews", content_width: float) -> dict:
    """
    Measure the height requirements for news content.

    Returns dict with heights for each section and total.
    """
    heights = {"top_stories": [], "third_story": 0, "headlines": 0, "header": 8 * mm}
    col_width = (content_width - 8 * mm) / 2

    # Top stories (full width)
    for story in news.top_stories:
        headline_h = measure_text_height(
            story.headline, FONTS["semibold"], 11, content_width
        )
        summary_h = measure_text_height(
            story.summary, FONTS["medium"], 8, content_width
        )
        # headline + gap + summary + gap
        story_height = headline_h + 5 * mm + summary_h + 8 * mm
        heights["top_stories"].append(story_height)

    # Third story (left column)
    if news.third_story:
        headline_h = measure_text_height(
            news.third_story.headline, FONTS["semibold"], 10, col_width
        )
        summary_h = measure_text_height(
            news.third_story.summary, FONTS["medium"], 8, col_width
        )
        heights["third_story"] = headline_h + 4 * mm + summary_h

    # Headlines (right column) - estimate
    if news.headlines:
        heights["headlines"] = 5 * mm  # "IN BRIEF" header
        for headline in news.headlines:
            h = measure_text_height(headline, FONTS["medium"], 8, col_width - 3 * mm)
            heights["headlines"] += h + 4 * mm

    # Total height
    heights["total"] = (
        heights["header"]
        + sum(heights["top_stories"])
        + max(heights["third_story"], heights["headlines"])
    )

    return heights


def fit_news_to_space(
    news: "CuratedNews",
    available_height: float,
    content_width: float,
) -> "CuratedNews":
    """
    Adjust news content to fit within available vertical space.

    Strategy: Keep stories complete. If overflow, ask AI to rewrite ONE story
    shorter. Only truncate as an absolute fallback.

    Returns a new CuratedNews object with adjusted summaries.
    """
    from data_sources.claude_summarizer import (
        CuratedNews, CuratedStory, shorten_summary
    )

    if not news.top_stories and not news.third_story:
        return news

    # Make mutable copies
    top_stories = [
        CuratedStory(headline=s.headline, summary=s.summary)
        for s in news.top_stories
    ]
    third_story = (
        CuratedStory(
            headline=news.third_story.headline,
            summary=news.third_story.summary
        )
        if news.third_story else None
    )
    headlines = list(news.headlines)

    # Create working news object
    adjusted = CuratedNews(
        top_stories=top_stories,
        third_story=third_story,
        headlines=headlines
    )

    # Measure current height
    heights = _measure_news_height(adjusted, content_width)

    if heights["total"] <= available_height:
        logger.debug(
            "News fits: %.1fmm needed, %.1fmm available",
            heights["total"] / mm, available_height / mm
        )
        return adjusted

    overflow_mm = (heights["total"] - available_height) / mm
    logger.info(
        "News overflow: %.1fmm needed, %.1fmm available (%.1fmm over)",
        heights["total"] / mm, available_height / mm, overflow_mm
    )

    # Strategy: Shorten ONE story more aggressively rather than multiple stories
    # Estimate needed reduction and be aggressive upfront to minimize API calls

    stories_to_try = []
    if adjusted.third_story:
        # For large overflow (>20mm), go straight to 1 sentence for third story
        if overflow_mm > 20:
            stories_to_try.append(("third", 1))
        else:
            stories_to_try.append(("third", 2))
    if len(adjusted.top_stories) > 1:
        # Second top story: be aggressive if still large overflow expected
        stories_to_try.append(("top_1", 3))
    if adjusted.top_stories:
        # Last resort: shorten first top story
        stories_to_try.append(("top_0", 4))

    for story_id, target_sentences in stories_to_try:
        if story_id == "third" and adjusted.third_story:
            logger.info("Asking AI to shorten third story to %d sentences", target_sentences)
            shorter = shorten_summary(
                adjusted.third_story.headline,
                adjusted.third_story.summary,
                target_sentences
            )
            if shorter:
                adjusted.third_story = CuratedStory(
                    headline=adjusted.third_story.headline,
                    summary=shorter
                )
        elif story_id == "top_1" and len(adjusted.top_stories) > 1:
            logger.info("Asking AI to shorten second top story to %d sentences", target_sentences)
            shorter = shorten_summary(
                adjusted.top_stories[1].headline,
                adjusted.top_stories[1].summary,
                target_sentences
            )
            if shorter:
                adjusted.top_stories[1] = CuratedStory(
                    headline=adjusted.top_stories[1].headline,
                    summary=shorter
                )
        elif story_id == "top_0" and adjusted.top_stories:
            logger.info("Asking AI to shorten first top story to %d sentences", target_sentences)
            shorter = shorten_summary(
                adjusted.top_stories[0].headline,
                adjusted.top_stories[0].summary,
                target_sentences
            )
            if shorter:
                adjusted.top_stories[0] = CuratedStory(
                    headline=adjusted.top_stories[0].headline,
                    summary=shorter
                )

        # Check if we fit now
        heights = _measure_news_height(adjusted, content_width)
        if heights["total"] <= available_height:
            logger.info(
                "News fits after shortening %s (%.1fmm)",
                story_id, heights["total"] / mm
            )
            return adjusted

    # Still doesn't fit - drop headlines progressively
    while adjusted.headlines and heights["total"] > available_height:
        dropped = adjusted.headlines.pop()
        logger.info("Dropping headline: %s", dropped[:50])
        heights = _measure_news_height(adjusted, content_width)

    if heights["total"] <= available_height:
        logger.info("News fits after dropping headlines (%.1fmm)", heights["total"] / mm)
        return adjusted

    # Absolute fallback: truncate third story summary
    if adjusted.third_story and heights["total"] > available_height:
        logger.warning("Fallback: truncating third story summary")
        adjusted.third_story = CuratedStory(
            headline=adjusted.third_story.headline,
            summary=truncate_text(adjusted.third_story.summary, 200)
        )
        heights = _measure_news_height(adjusted, content_width)

    if heights["total"] > available_height:
        logger.warning(
            "News still overflows after all adjustments: %.1fmm > %.1fmm",
            heights["total"] / mm, available_height / mm
        )

    return adjusted


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
    # Note: %-d format is macOS/Linux only (no zero-padding). Windows would need %#d.
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

    draw_text(c, margin_left, y, LOCATION_NAME,
              font=FONTS["light"], size=9, colour=COLOURS["muted"])
    y -= 8 * mm

    # Divider
    draw_divider(c, margin_left, margin_right, y)
    y -= 8 * mm

    # === NEWS SECTION ===
    # Define safe zones
    inspiration_top = 7 * cm  # Don't go below this for news

    # Calculate available height for news and fit content
    news_available_height = y - inspiration_top - 1 * cm  # 1cm safety margin
    news = fit_news_to_space(content.news, news_available_height, content_width)

    draw_text(c, margin_left, y, "THE GUARDIAN",
              font=FONTS["bold"], size=9, colour=COLOURS["secondary"])
    y -= 8 * mm
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
        footer_y = 3 * cm

        draw_divider(c, margin_left, margin_right, inspiration_y + 10 * mm)

        # Calculate max quote length based on available space
        # Space available: inspiration_y down to footer_y + margin
        available_quote_height = inspiration_y - footer_y - 1 * cm
        # Estimate chars that fit: ~10 chars per line, ~13pt line height
        quote_max_width = content_width - 10 * mm
        chars_per_line = int(quote_max_width / (10 * 0.5))  # rough estimate
        max_lines = int(available_quote_height / (10 * 1.3))
        max_quote_chars = min(250, chars_per_line * max_lines)

        # Quote text - larger, italicized feel
        text = truncate_text(h.text, max_quote_chars)
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
        short_verse = truncate_text(verse_text, 80)
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
