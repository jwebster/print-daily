# Readwise highlights API integration

import logging
import os
import random
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)

READWISE_TOKEN = os.environ.get("READWISE_TOKEN")
MIN_HIGHLIGHT_LENGTH = 20  # Skip very short highlights
MAX_PAGES = 5  # Limit pagination to avoid excessive API calls


@dataclass
class Highlight:
    text: str
    title: str  # Book/article title
    author: str


def get_random_highlight() -> Highlight | None:
    """Fetch a random highlight from Readwise using export endpoint with pagination."""
    if not READWISE_TOKEN:
        return None

    try:
        all_highlights = []
        next_cursor = None
        pages_fetched = 0

        while pages_fetched < MAX_PAGES:
            # Build request params
            params = {}
            if next_cursor:
                params["pageCursor"] = next_cursor

            response = requests.get(
                "https://readwise.io/api/v2/export/",
                headers={"Authorization": f"Token {READWISE_TOKEN}"},
                params=params,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
            pages_fetched += 1

            # Process results from this page
            results = data.get("results", [])
            for book in results:
                title = book.get("title", "Unknown")
                author = book.get("author", "Unknown")
                for h in book.get("highlights", []):
                    text = h.get("text", "")
                    if text and len(text) > MIN_HIGHLIGHT_LENGTH:
                        all_highlights.append(Highlight(
                            text=text,
                            title=title,
                            author=author,
                        ))

            # Check for more pages
            next_cursor = data.get("nextPageCursor")
            if not next_cursor:
                break

        if not all_highlights:
            return None

        return random.choice(all_highlights)

    except requests.RequestException as e:
        logger.warning("Readwise fetch failed: %s", e)
        return None
