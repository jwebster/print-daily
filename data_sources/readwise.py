# Readwise highlights API integration

import json
import logging
import os
import random
import time
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)


def _retry_request(func, max_retries=3, delay=1):
    """Retry a function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise
            logger.debug(
                "Request failed (attempt %d/%d): %s",
                attempt + 1, max_retries, e
            )
            time.sleep(delay * (2 ** attempt))
    return None


READWISE_TOKEN = os.environ.get("READWISE_TOKEN")
MIN_HIGHLIGHT_LENGTH = 20  # Skip very short highlights
MAX_PAGES = 5  # Limit pagination to avoid excessive API calls
MAX_RANDOM_PAGE_OFFSET = 10  # Maximum random page offset for coverage


@dataclass
class Highlight:
    text: str
    title: str  # Book/article title
    author: str


def _skip_pages(start_page: int, headers: dict, timeout: int) -> str | None:
    """Skip to a specific page by following cursor chain.

    Returns cursor for target page.
    """
    if start_page <= 1:
        return None

    cursor = None
    for _ in range(start_page - 1):
        params = {}
        if cursor:
            params["pageCursor"] = cursor

        response = _retry_request(
            lambda p=params: requests.get(
                "https://readwise.io/api/v2/export/",
                headers=headers,
                params=p,
                timeout=timeout,
            )
        )
        response.raise_for_status()
        data = response.json()

        cursor = data.get("nextPageCursor")
        if not cursor:
            # Ran out of pages, return None to start from beginning
            return None

    return cursor


def get_random_highlight() -> Highlight | None:
    """Fetch a random highlight from Readwise using export endpoint.

    Uses random page offset for more even coverage across all highlights
    over time.
    """
    if not READWISE_TOKEN:
        return None

    headers = {"Authorization": f"Token {READWISE_TOKEN}"}
    timeout = 15

    try:
        # Random starting page for more even coverage over time
        start_page = random.randint(1, MAX_RANDOM_PAGE_OFFSET)
        logger.debug("Starting from page %d", start_page)

        # Skip to the random starting page
        try:
            next_cursor = _skip_pages(start_page, headers, timeout)
        except requests.RequestException:
            # If skipping fails, start from beginning
            next_cursor = None
            start_page = 1

        all_highlights = []
        pages_fetched = 0

        while pages_fetched < MAX_PAGES:
            # Build request params
            params = {}
            if next_cursor:
                params["pageCursor"] = next_cursor

            response = _retry_request(
                lambda p=params: requests.get(
                    "https://readwise.io/api/v2/export/",
                    headers=headers,
                    params=p,
                    timeout=timeout,
                )
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

    except (requests.RequestException, json.JSONDecodeError) as e:
        logger.warning("Readwise fetch failed: %s", e)
        return None
