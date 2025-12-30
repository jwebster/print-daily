# Claude AI for news curation and summarization

import json
import logging
import os
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)

CLAUDE_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")

SYSTEM_PROMPT = """You are a news curator for a daily printed newspaper. Your reader is interested in:
- UK and world politics
- Climate and environment
- Technology and AI
- Significant world events

NOT interested in: sport, celebrities, entertainment, royal family gossip.

From the articles provided, create a curated selection:

1. TOP STORIES (2): The two most important stories that deserve deep coverage.
   Write 7-10 COMPLETE sentences covering key facts, context, why it matters, and implications.

2. THIRD STORY (1): Another interesting story with a SHORTER summary.
   Write 3-4 COMPLETE sentences - just the essential facts and why it matters.

3. HEADLINES (4-5): Other noteworthy stories where the headline tells the story.
   Keep the headline only, no summary needed. Pick ones that are self-explanatory.

IMPORTANT: Write full, complete sentences. Never trail off with ellipsis.

Respond with valid JSON only:
{
  "top_stories": [
    {"headline": "Headline", "summary": "7-10 sentence detailed summary."}
  ],
  "third_story": {"headline": "Headline", "summary": "3-4 sentence brief summary."},
  "headlines": ["Headline 1", "Headline 2"]
}"""


@dataclass
class CuratedStory:
    headline: str
    summary: str


@dataclass
class CuratedNews:
    top_stories: list[CuratedStory]  # 2 detailed stories
    third_story: CuratedStory | None  # 1 shorter story
    headlines: list[str]  # 4-5 headline-only items


def curate_and_summarize(articles: list[dict]) -> CuratedNews:
    """
    Use Claude to select and summarize the most interesting stories.

    Args:
        articles: List of dicts with 'headline' and 'summary' keys

    Returns:
        CuratedNews with featured stories and headline-only items
    """
    if not articles:
        return CuratedNews(top_stories=[], third_story=None, headlines=[])

    # Format articles for Claude
    articles_text = "\n\n".join(
        f"HEADLINE: {a['headline']}\nORIGINAL SUMMARY: {a['summary']}"
        for a in articles
    )

    if not CLAUDE_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not set, skipping AI curation")
        return _fallback(articles)

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": CLAUDE_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": CLAUDE_MODEL,
                "max_tokens": 2048,
                "system": SYSTEM_PROMPT,
                "messages": [
                    {
                        "role": "user",
                        "content": f"Here are today's news articles. Select 3-4 and provide detailed summaries:\n\n{articles_text}"
                    }
                ]
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()

        # Extract text content
        content = data.get("content", [])
        if not content:
            logger.warning("Claude returned empty content")
            return _fallback(articles)

        first_content = content[0] if content else {}
        text = first_content.get("text", "") if isinstance(first_content, dict) else ""

        # Handle markdown code blocks (Claude sometimes wraps JSON)
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        text = text.strip()

        # Parse JSON response
        result = json.loads(text)

        top_stories = [
            CuratedStory(headline=s.get("headline", ""), summary=s.get("summary", ""))
            for s in result.get("top_stories", [])
            if isinstance(s, dict) and s.get("headline")
        ]

        third = result.get("third_story")
        if third and isinstance(third, dict) and third.get("headline"):
            third_story = CuratedStory(headline=third.get("headline", ""), summary=third.get("summary", ""))
        else:
            third_story = None

        headlines = [h for h in result.get("headlines", []) if isinstance(h, str) and h]

        return CuratedNews(top_stories=top_stories, third_story=third_story, headlines=headlines)

    except json.JSONDecodeError as e:
        logger.warning("Failed to parse Claude response: %s", e)
        return _fallback(articles)
    except requests.RequestException as e:
        logger.warning("Claude API error: %s", e)
        return _fallback(articles)
    except (KeyError, TypeError, IndexError) as e:
        logger.warning("Unexpected Claude response structure: %s", e)
        return _fallback(articles)


def _fallback(articles: list[dict]) -> CuratedNews:
    """Fallback to original articles if Claude fails."""
    top_stories = [
        CuratedStory(headline=a["headline"], summary=a["summary"])
        for a in articles[:2]
    ]
    third_story = CuratedStory(headline=articles[2]["headline"], summary=articles[2]["summary"]) if len(articles) > 2 else None
    headlines = [a["headline"] for a in articles[3:7]]
    return CuratedNews(top_stories=top_stories, third_story=third_story, headlines=headlines)
