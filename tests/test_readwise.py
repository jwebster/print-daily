"""Tests for readwise module."""

import pytest
from unittest.mock import patch, Mock
from data_sources.readwise import get_random_highlight, Highlight, MIN_HIGHLIGHT_LENGTH


class TestHighlight:
    """Tests for Highlight dataclass."""

    def test_creation(self):
        h = Highlight(
            text="This is a highlight",
            title="Book Title",
            author="Author Name"
        )
        assert h.text == "This is a highlight"
        assert h.title == "Book Title"
        assert h.author == "Author Name"


class TestMinHighlightLength:
    """Tests for MIN_HIGHLIGHT_LENGTH constant."""

    def test_is_reasonable_value(self):
        assert MIN_HIGHLIGHT_LENGTH > 0
        assert MIN_HIGHLIGHT_LENGTH < 100  # Not too restrictive


class TestGetRandomHighlight:
    """Tests for get_random_highlight function."""

    @patch('data_sources.readwise.READWISE_TOKEN', None)
    def test_returns_none_without_token(self):
        result = get_random_highlight()
        assert result is None

    @patch('data_sources.readwise.READWISE_TOKEN', 'test-token')
    @patch('data_sources.readwise.requests.get')
    def test_parses_export_response(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Test Book",
                    "author": "Test Author",
                    "highlights": [
                        {"text": "This is a longer highlight that should pass the minimum length check."}
                    ]
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_random_highlight()

        assert result is not None
        assert result.title == "Test Book"
        assert result.author == "Test Author"
        assert "longer highlight" in result.text

    @patch('data_sources.readwise.READWISE_TOKEN', 'test-token')
    @patch('data_sources.readwise.requests.get')
    def test_filters_short_highlights(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Book",
                    "author": "Author",
                    "highlights": [
                        {"text": "Short"},  # Too short
                        {"text": "This is a sufficiently long highlight for the test."}
                    ]
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_random_highlight()

        assert result is not None
        assert len(result.text) > MIN_HIGHLIGHT_LENGTH

    @patch('data_sources.readwise.READWISE_TOKEN', 'test-token')
    @patch('data_sources.readwise.requests.get')
    def test_handles_empty_results(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_random_highlight()

        assert result is None

    @patch('data_sources.readwise.READWISE_TOKEN', 'test-token')
    @patch('data_sources.readwise.requests.get')
    def test_handles_book_without_highlights(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Empty Book",
                    "author": "Author",
                    "highlights": []
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_random_highlight()

        assert result is None

    @patch('data_sources.readwise.READWISE_TOKEN', 'test-token')
    @patch('data_sources.readwise.requests.get')
    def test_handles_request_error(self, mock_get):
        import requests
        mock_get.side_effect = requests.RequestException("Network error")

        result = get_random_highlight()

        assert result is None

    @patch('data_sources.readwise.READWISE_TOKEN', 'test-token')
    @patch('data_sources.readwise.requests.get')
    def test_handles_missing_author(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Book Without Author",
                    "highlights": [
                        {"text": "This is a long enough highlight to be included in results."}
                    ]
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_random_highlight()

        assert result is not None
        assert result.author == "Unknown"

    @patch('data_sources.readwise.READWISE_TOKEN', 'test-token')
    @patch('data_sources.readwise.requests.get')
    @patch('data_sources.readwise.random.choice')
    def test_randomly_selects_highlight(self, mock_choice, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Book 1",
                    "author": "Author 1",
                    "highlights": [
                        {"text": "First highlight that is long enough to be included."},
                        {"text": "Second highlight that is also long enough to include."}
                    ]
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Mock random.choice to return the first item
        def return_first(items):
            return items[0]
        mock_choice.side_effect = return_first

        result = get_random_highlight()

        assert result is not None
        mock_choice.assert_called_once()
