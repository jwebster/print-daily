"""Tests for claude_summarizer module."""

import pytest
from unittest.mock import patch, Mock
from data_sources.claude_summarizer import (
    curate_and_summarize,
    _fallback,
    CuratedStory,
    CuratedNews,
)


class TestCuratedStory:
    """Tests for CuratedStory dataclass."""

    def test_creation(self):
        story = CuratedStory(
            headline="Test Headline",
            summary="Test summary text"
        )
        assert story.headline == "Test Headline"
        assert story.summary == "Test summary text"


class TestCuratedNews:
    """Tests for CuratedNews dataclass."""

    def test_creation(self):
        news = CuratedNews(
            top_stories=[CuratedStory("H1", "S1")],
            third_story=CuratedStory("H3", "S3"),
            headlines=["Headline A", "Headline B"]
        )
        assert len(news.top_stories) == 1
        assert news.third_story is not None
        assert len(news.headlines) == 2

    def test_optional_third_story(self):
        news = CuratedNews(
            top_stories=[],
            third_story=None,
            headlines=[]
        )
        assert news.third_story is None


class TestFallback:
    """Tests for _fallback function."""

    def test_with_multiple_articles(self):
        articles = [
            {"headline": "Article 1", "summary": "Summary 1"},
            {"headline": "Article 2", "summary": "Summary 2"},
            {"headline": "Article 3", "summary": "Summary 3"},
            {"headline": "Article 4", "summary": "Summary 4"},
            {"headline": "Article 5", "summary": "Summary 5"},
        ]

        result = _fallback(articles)

        assert len(result.top_stories) == 2
        assert result.top_stories[0].headline == "Article 1"
        assert result.top_stories[1].headline == "Article 2"
        assert result.third_story.headline == "Article 3"
        assert len(result.headlines) == 2
        assert result.headlines[0] == "Article 4"

    def test_with_few_articles(self):
        articles = [
            {"headline": "Article 1", "summary": "Summary 1"},
            {"headline": "Article 2", "summary": "Summary 2"},
        ]

        result = _fallback(articles)

        assert len(result.top_stories) == 2
        assert result.third_story is None
        assert len(result.headlines) == 0

    def test_with_empty_list(self):
        result = _fallback([])

        assert len(result.top_stories) == 0
        assert result.third_story is None
        assert len(result.headlines) == 0


class TestCurateAndSummarize:
    """Tests for curate_and_summarize function."""

    def test_empty_articles_returns_empty(self):
        result = curate_and_summarize([])

        assert len(result.top_stories) == 0
        assert result.third_story is None
        assert len(result.headlines) == 0

    @patch('data_sources.claude_summarizer.CLAUDE_API_KEY', None)
    def test_no_api_key_uses_fallback(self):
        articles = [
            {"headline": "Article 1", "summary": "Summary 1"},
            {"headline": "Article 2", "summary": "Summary 2"},
        ]

        result = curate_and_summarize(articles)

        # Should use fallback
        assert len(result.top_stories) == 2
        assert result.top_stories[0].headline == "Article 1"

    @patch('data_sources.claude_summarizer.CLAUDE_API_KEY', 'test-key')
    @patch('data_sources.claude_summarizer.requests.post')
    def test_parses_claude_response(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [{
                "text": '''{
                    "top_stories": [
                        {"headline": "Curated Story 1", "summary": "Detailed summary 1"},
                        {"headline": "Curated Story 2", "summary": "Detailed summary 2"}
                    ],
                    "third_story": {"headline": "Third Story", "summary": "Brief summary"},
                    "headlines": ["Headline A", "Headline B"]
                }'''
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        articles = [{"headline": "Test", "summary": "Test"}]
        result = curate_and_summarize(articles)

        assert len(result.top_stories) == 2
        assert result.top_stories[0].headline == "Curated Story 1"
        assert result.third_story.headline == "Third Story"
        assert len(result.headlines) == 2

    @patch('data_sources.claude_summarizer.CLAUDE_API_KEY', 'test-key')
    @patch('data_sources.claude_summarizer.requests.post')
    def test_handles_markdown_wrapped_json(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [{
                "text": '''```json
{
    "top_stories": [{"headline": "Story", "summary": "Summary"}],
    "third_story": null,
    "headlines": []
}
```'''
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        articles = [{"headline": "Test", "summary": "Test"}]
        result = curate_and_summarize(articles)

        assert len(result.top_stories) == 1
        assert result.top_stories[0].headline == "Story"

    @patch('data_sources.claude_summarizer.CLAUDE_API_KEY', 'test-key')
    @patch('data_sources.claude_summarizer.requests.post')
    def test_handles_api_error(self, mock_post):
        import requests
        mock_post.side_effect = requests.RequestException("API error")

        articles = [
            {"headline": "Article 1", "summary": "Summary 1"},
            {"headline": "Article 2", "summary": "Summary 2"},
        ]

        result = curate_and_summarize(articles)

        # Should fall back to raw articles
        assert len(result.top_stories) == 2
        assert result.top_stories[0].headline == "Article 1"

    @patch('data_sources.claude_summarizer.CLAUDE_API_KEY', 'test-key')
    @patch('data_sources.claude_summarizer.requests.post')
    def test_handles_invalid_json(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [{"text": "This is not valid JSON"}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        articles = [
            {"headline": "Article 1", "summary": "Summary 1"},
        ]

        result = curate_and_summarize(articles)

        # Should fall back to raw articles
        assert len(result.top_stories) == 1

    @patch('data_sources.claude_summarizer.CLAUDE_API_KEY', 'test-key')
    @patch('data_sources.claude_summarizer.requests.post')
    def test_handles_empty_content(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"content": []}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        articles = [{"headline": "Test", "summary": "Test"}]
        result = curate_and_summarize(articles)

        # Should fall back
        assert len(result.top_stories) == 1
