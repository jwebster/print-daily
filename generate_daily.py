#!/usr/bin/env python3
"""
Daily newspaper PDF generator and printer.
Generates an A4 PDF with news, weather, and bible readings, then prints it.

Usage:
    python generate_daily.py              # Generate and print
    python generate_daily.py --preview    # Generate and open in Preview (no print)
    python generate_daily.py --save FILE  # Generate and save to file only
    python generate_daily.py --date DATE  # Generate for specific date (YYYY-MM-DD)
    python generate_daily.py --no-ai      # Skip AI curation, use raw Guardian articles
"""

import argparse
import logging
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

# Configure logging before any other imports
# Logs go to stderr so launchd captures them in stderr.log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from data_sources.weather import get_weather
from data_sources.guardian import get_news
from data_sources.bible_readings import get_todays_readings
from data_sources.bible_verse import get_daily_verse
from data_sources.readwise import get_random_highlight
from data_sources.claude_summarizer import (
    curate_and_summarize, CuratedStory, CuratedNews,
)
from pdf_generator import generate_pdf, DailyContent, Highlight


def main():
    parser = argparse.ArgumentParser(description="Generate daily newspaper PDF")
    parser.add_argument("--preview", action="store_true", help="Open in Preview instead of printing")
    parser.add_argument("--save", type=str, metavar="PATH", help="Save PDF to file instead of printing")
    parser.add_argument("--date", type=str, help="Generate for specific date (YYYY-MM-DD)")
    parser.add_argument("--no-ai", action="store_true", help="Skip AI curation, use raw Guardian articles")
    args = parser.parse_args()

    # Determine date
    if args.date:
        try:
            target_date = date.fromisoformat(args.date)
        except ValueError:
            print(f"Error: Invalid date format '{args.date}'. Expected YYYY-MM-DD (e.g., 2025-12-30)")
            sys.exit(1)
    else:
        target_date = date.today()

    # Note: %-d format is macOS/Linux only (no zero-padding). Windows would need %#d.
    print(f"Generating daily print for {target_date.strftime('%A %-d %B %Y')}...")

    # Fetch data in parallel (gracefully handle failures)
    print("  Fetching data in parallel...")

    def fetch_weather():
        return get_weather()

    def fetch_news():
        return get_news(count=15)

    def fetch_readings():
        return get_todays_readings(target_date)

    def fetch_verse():
        return get_daily_verse(target_date)

    def fetch_highlight():
        return get_random_highlight()

    # Run all fetches in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_weather = executor.submit(fetch_weather)
        future_news = executor.submit(fetch_news)
        future_readings = executor.submit(fetch_readings)
        future_verse = executor.submit(fetch_verse)
        future_highlight = executor.submit(fetch_highlight)

        # Collect results
        weather = future_weather.result()
        raw_news = future_news.result()
        readings = future_readings.result()
        verse = future_verse.result()
        rw_highlight = future_highlight.result()

    # Print results in order
    print("  Weather:")
    if weather:
        print(f"    {weather.temperature}°C, {weather.condition}")
    else:
        print("    Weather unavailable")

    print("  News from Guardian:")
    print(f"    {len(raw_news)} articles fetched")

    # Use Claude to curate and summarize (must wait for news)
    if not args.no_ai and raw_news:
        print("  Curating with Claude AI...")
        articles = [{"headline": n.headline, "summary": n.summary} for n in raw_news]
        news = curate_and_summarize(articles)
        third = "1 third" if news.third_story else "0 third"
        print(f"    {len(news.top_stories)} top, {third}, {len(news.headlines)} headlines")
    else:
        # Fallback to raw news without AI
        top_stories = [CuratedStory(headline=n.headline, summary=n.summary) for n in raw_news[:2]]
        third_story = CuratedStory(headline=raw_news[2].headline, summary=raw_news[2].summary) if len(raw_news) > 2 else None
        headlines = [n.headline for n in raw_news[3:7]]
        news = CuratedNews(top_stories=top_stories, third_story=third_story, headlines=headlines)

    print("  Bible readings:")
    if readings:
        valid = [r for r in readings if r]
        if valid:
            print(f"    {', '.join(valid)}")
        else:
            print("    End of reading plan")
    else:
        print("    No readings (weekend)")

    print("  Verse of the day:")
    print(f"    {verse[1]}")

    print("  Readwise highlight:")
    if rw_highlight:
        print(f"    From: {rw_highlight.title}")
        highlight = Highlight(text=rw_highlight.text, title=rw_highlight.title, author=rw_highlight.author)
    else:
        print("    No highlight available")
        highlight = None

    # Generate PDF
    print("  Generating PDF...")
    content = DailyContent(
        date=target_date,
        weather=weather,
        news=news,
        readings=readings,
        verse=verse,
        highlight=highlight,
    )
    pdf_bytes = generate_pdf(content)
    print(f"    {len(pdf_bytes)} bytes")

    # Output
    if args.save:
        output_path = Path(args.save)
        output_path.write_bytes(pdf_bytes)
        print(f"Saved to {output_path}")

    elif args.preview:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(pdf_bytes)
            temp_path = f.name
        print(f"Opening {temp_path} in Preview...")
        result = subprocess.run(["open", temp_path], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Preview failed: {result.stderr}")
            sys.exit(1)

    else:
        # Print to default printer
        print("  Sending to printer...")
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(pdf_bytes)
            temp_path = f.name

        result = subprocess.run(["lp", temp_path], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Printed: {result.stdout.strip()}")
            os.unlink(temp_path)  # Clean up after successful print
        else:
            print(f"Print failed: {result.stderr}")
            os.unlink(temp_path)  # Clean up on failure too
            sys.exit(1)

    print("Done!")


if __name__ == "__main__":
    main()
