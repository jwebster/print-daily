"""Tests for guardian module."""

import pytest
from unittest.mock import patch, Mock
from data_sources.guardian import clean_html, get_news, NewsItem


class TestCleanHtml:
    """Tests for clean_html function."""

    def test_removes_html_tags(self):
        assert clean_html("<p>Hello</p>") == "Hello"
        assert clean_html("<strong>Bold</strong>") == "Bold"
        assert clean_html("<a href='url'>Link</a>") == "Link"

    def test_handles_nested_tags(self):
        assert clean_html("<p><strong>Nested</strong></p>") == "Nested"

    def test_decodes_html_entities(self):
        assert clean_html("&amp;") == "&"
        assert clean_html("&lt;") == "<"
        assert clean_html("&gt;") == ">"
        assert clean_html("&quot;") == '"'
        assert clean_html("&#39;") == "'"

    def test_handles_empty_string(self):
        assert clean_html("") == ""

    def test_handles_none(self):
        assert clean_html(None) == ""

    def test_strips_whitespace(self):
        assert clean_html("  <p>  text  </p>  ") == "text"

    def test_preserves_plain_text(self):
        assert clean_html("Plain text") == "Plain text"


class TestNewsItem:
    """Tests for NewsItem dataclass."""

    def test_creation(self):
        item = NewsItem(
            headline="Test Headline",
            summary="Test summary",
            section="Politics"
        )
        assert item.headline == "Test Headline"
        assert item.summary == "Test summary"
        assert item.section == "Politics"


class TestGetNews:
    """Tests for get_news function."""

    @patch('data_sources.guardian.GUARDIAN_API_KEY', None)
    def test_returns_empty_without_api_key(self):
        result = get_news()
        assert result == []

    @patch('data_sources.guardian.GUARDIAN_API_KEY', 'test-key')
    @patch('data_sources.guardian.requests.get')
    def test_parses_api_response(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "results": [
                    {
                        "webTitle": "Test Article",
                        "fields": {"trailText": "<p>Summary text</p>"},
                        "sectionName": "Politics"
                    }
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_news(count=1)

        assert len(result) == 1
        assert result[0].headline == "Test Article"
        assert result[0].summary == "Summary text"
        assert result[0].section == "Politics"

    @patch('data_sources.guardian.GUARDIAN_API_KEY', 'test-key')
    @patch('data_sources.guardian.requests.get')
    def test_handles_missing_fields(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "results": [
                    {
                        "webTitle": "Article Without Summary",
                        "sectionName": "News"
                    }
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_news(count=1)

        assert len(result) == 1
        assert result[0].headline == "Article Without Summary"
        assert result[0].summary == ""

    @patch('data_sources.guardian.GUARDIAN_API_KEY', 'test-key')
    @patch('data_sources.guardian.requests.get')
    def test_handles_request_error(self, mock_get):
        import requests
        mock_get.side_effect = requests.RequestException("Network error")

        result = get_news()

        assert result == []

    @patch('data_sources.guardian.GUARDIAN_API_KEY', 'test-key')
    @patch('data_sources.guardian.requests.get')
    def test_skips_items_without_headline(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "results": [
                    {"webTitle": "", "sectionName": "News"},
                    {"webTitle": "Valid Article", "sectionName": "News"}
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_news()

        assert len(result) == 1
        assert result[0].headline == "Valid Article"
