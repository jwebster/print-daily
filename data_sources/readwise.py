# Readwise highlights API integration

import os
import random
import requests
from dataclasses import dataclass

READWISE_TOKEN = os.environ.get("READWISE_TOKEN")


@dataclass
class Highlight:
    text: str
    title: str  # Book/article title
    author: str


def get_random_highlight() -> Highlight | None:
    """Fetch a random highlight from Readwise using export endpoint."""
    if not READWISE_TOKEN:
        return None

    try:
        # Use export endpoint which includes book details
        response = requests.get(
            "https://readwise.io/api/v2/export/",
            headers={"Authorization": f"Token {READWISE_TOKEN}"},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        if not results:
            return None

        # Collect all highlights with their book info
        all_highlights = []
        for book in results:
            title = book.get("title", "Unknown")
            author = book.get("author", "Unknown")
            for h in book.get("highlights", []):
                text = h.get("text", "")
                if text and len(text) > 20:  # Skip very short highlights
                    all_highlights.append(Highlight(
                        text=text,
                        title=title,
                        author=author,
                    ))

        if not all_highlights:
            return None

        return random.choice(all_highlights)

    except Exception as e:
        print(f"Readwise fetch failed: {e}")
        return None
