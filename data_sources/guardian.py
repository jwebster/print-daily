# Guardian news headlines from Guardian Open Platform API

import html
import logging
import os
import re
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# API key from environment (get one at https://open-platform.theguardian.com/)
GUARDIAN_API_KEY = os.environ.get("GUARDIAN_API_KEY")


@dataclass
class NewsItem:
    headline: str
    summary: str
    section: str


def clean_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


def get_news(count: int = 15) -> list[NewsItem]:
    """Fetch top news headlines from The Guardian for curation."""
    if not GUARDIAN_API_KEY:
        logger.warning("GUARDIAN_API_KEY not set")
        return []

    try:
        url = "https://content.guardianapis.com/search"
        params = {
            "section": "uk-news|politics|world|technology|science|business|environment",
            "show-fields": "trailText",
            "page-size": count,
            "order-by": "newest",
            "api-key": GUARDIAN_API_KEY,
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = data.get("response", {}).get("results", [])
        news_items = []

        for item in results:
            headline = item.get("webTitle", "")
            fields = item.get("fields", {})
            summary = clean_html(fields.get("trailText", ""))
            section = item.get("sectionName", "")

            if headline:
                news_items.append(NewsItem(
                    headline=headline,
                    summary=summary,
                    section=section,
                ))

        return news_items

    except requests.RequestException as e:
        logger.warning("Guardian news fetch failed: %s", e)
        return []
