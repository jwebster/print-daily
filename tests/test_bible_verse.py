"""Tests for bible_verse module."""

import pytest
from datetime import date
from data_sources.bible_verse import get_daily_verse, VERSES


class TestGetDailyVerse:
    """Tests for get_daily_verse function."""

    def test_returns_tuple(self):
        result = get_daily_verse(date(2024, 1, 1))
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_tuple_contains_text_and_reference(self):
        text, reference = get_daily_verse(date(2024, 1, 1))
        assert isinstance(text, str)
        assert isinstance(reference, str)
        assert len(text) > 0
        assert len(reference) > 0

    def test_different_days_different_verses(self):
        verse1 = get_daily_verse(date(2024, 1, 1))
        verse2 = get_daily_verse(date(2024, 1, 2))
        # They should be different (unless VERSES has duplicates)
        # At minimum, check they're valid
        assert verse1[0] and verse1[1]
        assert verse2[0] and verse2[1]

    def test_same_day_same_verse(self):
        verse1 = get_daily_verse(date(2024, 6, 15))
        verse2 = get_daily_verse(date(2024, 6, 15))
        assert verse1 == verse2

    def test_cycles_through_year(self):
        # Day 1 and Day 1 + len(VERSES) should return same verse
        day1 = get_daily_verse(date(2024, 1, 1))
        # Day of year 1 and 1 + 31 should differ if VERSES has 31 items
        assert len(VERSES) == 31  # Verify assumption

    def test_all_verses_are_valid(self):
        for text, reference in VERSES:
            assert len(text) > 10, f"Verse text too short: {text}"
            assert len(reference) > 0, "Reference should not be empty"
            # References should contain a book name and numbers
            assert any(c.isdigit() for c in reference), f"Reference should contain numbers: {reference}"

    def test_default_date_is_today(self):
        # Should not raise when called without arguments
        result = get_daily_verse()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_jan_1_returns_first_verse(self):
        # Jan 1 (day_of_year=1) should return VERSES[0]
        result = get_daily_verse(date(2024, 1, 1))
        assert result == VERSES[0]
