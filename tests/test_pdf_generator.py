"""Tests for pdf_generator module."""

import pytest
from datetime import date
from pdf_generator import (
    generate_pdf,
    DailyContent,
    Highlight,
    get_font_path,
    register_fonts,
)
from data_sources.weather import WeatherData
from data_sources.claude_summarizer import CuratedNews, CuratedStory


class TestGetFontPath:
    """Tests for get_font_path function."""

    def test_finds_existing_font(self):
        path = get_font_path("Montserrat-Medium.ttf")
        assert path.endswith("Montserrat-Medium.ttf")

    def test_raises_for_missing_font(self):
        with pytest.raises(FileNotFoundError):
            get_font_path("NonExistentFont.ttf")


class TestHighlight:
    """Tests for Highlight dataclass."""

    def test_creation(self):
        h = Highlight(
            text="Great quote",
            title="Book Title",
            author="Author Name"
        )
        assert h.text == "Great quote"
        assert h.title == "Book Title"
        assert h.author == "Author Name"


class TestDailyContent:
    """Tests for DailyContent dataclass."""

    def test_creation_minimal(self):
        content = DailyContent(
            date=date(2024, 1, 15),
            weather=None,
            news=CuratedNews(top_stories=[], third_story=None, headlines=[]),
            readings=None,
        )
        assert content.date == date(2024, 1, 15)
        assert content.weather is None
        assert content.readings is None
        assert content.verse is None
        assert content.highlight is None

    def test_creation_full(self):
        weather = WeatherData(
            temperature=12,
            condition="Sunny",
            high=15,
            low=8,
            sunrise="07:30",
            sunset="17:00"
        )
        news = CuratedNews(
            top_stories=[CuratedStory("Headline", "Summary")],
            third_story=None,
            headlines=["Brief headline"]
        )
        content = DailyContent(
            date=date(2024, 1, 15),
            weather=weather,
            news=news,
            readings=["Gen. 1", "Ps. 1", "Luke 1"],
            verse=("Verse text", "Reference"),
            highlight=Highlight("Quote", "Book", "Author"),
        )
        assert content.weather.temperature == 12
        assert len(content.news.top_stories) == 1
        assert len(content.readings) == 3
        assert content.verse[0] == "Verse text"


class TestGeneratePdf:
    """Tests for generate_pdf function."""

    def test_generates_pdf_bytes(self):
        content = DailyContent(
            date=date(2024, 1, 15),
            weather=None,
            news=CuratedNews(top_stories=[], third_story=None, headlines=[]),
            readings=None,
        )

        result = generate_pdf(content)

        assert isinstance(result, bytes)
        assert len(result) > 0
        # PDF files start with %PDF
        assert result[:4] == b'%PDF'

    def test_generates_pdf_with_all_content(self):
        weather = WeatherData(
            temperature=12,
            condition="Partly cloudy",
            high=15,
            low=8,
            sunrise="07:30",
            sunset="17:00"
        )
        news = CuratedNews(
            top_stories=[
                CuratedStory("Big News Story", "This is a detailed summary."),
                CuratedStory("Another Story", "More details here."),
            ],
            third_story=CuratedStory("Third Story", "Brief summary."),
            headlines=["Headline One", "Headline Two", "Headline Three"]
        )
        content = DailyContent(
            date=date(2024, 1, 15),
            weather=weather,
            news=news,
            readings=["Gen. 1", "Ps. 1", "Luke 1"],
            verse=("Trust in the LORD with all your heart.", "Proverbs 3:5"),
            highlight=Highlight(
                "A great quote from a book",
                "The Book Title",
                "Author Name"
            ),
        )

        result = generate_pdf(content)

        assert isinstance(result, bytes)
        assert len(result) > 1000  # Should be larger with content
        assert result[:4] == b'%PDF'

    def test_handles_long_highlight(self):
        # Test that long highlights get truncated without error
        long_text = "A" * 300  # Longer than 250 char limit
        content = DailyContent(
            date=date(2024, 1, 15),
            weather=None,
            news=CuratedNews(top_stories=[], third_story=None, headlines=[]),
            readings=None,
            highlight=Highlight(long_text, "Book", "Author"),
        )

        result = generate_pdf(content)

        assert isinstance(result, bytes)
        assert result[:4] == b'%PDF'

    def test_handles_weekend_readings(self):
        # Weekend should show "Weekend" instead of readings
        content = DailyContent(
            date=date(2024, 1, 13),  # Saturday
            weather=None,
            news=CuratedNews(top_stories=[], third_story=None, headlines=[]),
            readings=None,  # None indicates weekend
        )

        result = generate_pdf(content)

        assert isinstance(result, bytes)
        assert result[:4] == b'%PDF'

    def test_handles_empty_readings(self):
        # End of year might have empty readings
        content = DailyContent(
            date=date(2024, 12, 31),
            weather=None,
            news=CuratedNews(top_stories=[], third_story=None, headlines=[]),
            readings=["", "", ""],  # Empty strings = end of plan
        )

        result = generate_pdf(content)

        assert isinstance(result, bytes)
        assert result[:4] == b'%PDF'
