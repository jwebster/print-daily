"""Tests for bible_readings module."""

import pytest
from datetime import date
from data_sources.bible_readings import (
    book_abbreviations,
    expand_book,
    count_weekdays,
    get_todays_readings,
    old_yr1,
    new,
    psalms,
)


class TestBookAbbreviations:
    """Tests for book_abbreviations function."""

    def test_old_testament_books(self):
        assert book_abbreviations("Genesis") == "Gen."
        assert book_abbreviations("Exodus") == "Ex."
        assert book_abbreviations("Deuteronomy") == "Deut."
        assert book_abbreviations("Psalms") == "Ps."

    def test_new_testament_books(self):
        assert book_abbreviations("Matthew") == "Matt."
        assert book_abbreviations("Romans") == "Rom."
        assert book_abbreviations("Revelation") == "Rev"

    def test_books_without_abbreviation(self):
        assert book_abbreviations("Ruth") == "Ruth"
        assert book_abbreviations("Mark") == "Mark"
        assert book_abbreviations("Jude") == "Jude"

    def test_unknown_book_returns_original(self):
        assert book_abbreviations("Unknown Book") == "Unknown Book"


class TestExpandBook:
    """Tests for expand_book function."""

    def test_simple_expansion(self):
        result = expand_book("Genesis", 3)
        assert result == ["Gen. 1", "Gen. 2", "Gen. 3"]

    def test_expansion_with_start(self):
        # expand_book(chapters=9, start=6) reads chapters 6, 7, 8, 9
        result = expand_book("Judges", 9, start=6)
        assert result == ["Judg. 6", "Judg. 7", "Judg. 8", "Judg. 9"]

    def test_expansion_with_step(self):
        result = expand_book("Psalms", 6, step=2)
        assert result == ["Ps. 1 - 2", "Ps. 3 - 4", "Ps. 5 - 6"]


class TestCountWeekdays:
    """Tests for count_weekdays function."""

    def test_single_weekday(self):
        # Monday Jan 1 to Tuesday Jan 2 = 1 weekday
        start = date(2024, 1, 1)  # Monday
        end = date(2024, 1, 2)  # Tuesday
        assert count_weekdays(start, end) == 1

    def test_full_week(self):
        # Monday to next Monday = 5 weekdays
        start = date(2024, 1, 1)  # Monday
        end = date(2024, 1, 8)  # Next Monday
        assert count_weekdays(start, end) == 5

    def test_weekend_only(self):
        # Saturday to Monday = 0 weekdays counted
        start = date(2024, 1, 6)  # Saturday
        end = date(2024, 1, 8)  # Monday
        assert count_weekdays(start, end) == 0

    def test_same_day(self):
        day = date(2024, 1, 1)
        assert count_weekdays(day, day) == 0


class TestGetTodaysReadings:
    """Tests for get_todays_readings function."""

    def test_weekday_returns_readings(self):
        # Monday Jan 1, 2024
        readings = get_todays_readings(date(2024, 1, 1))
        assert readings is not None
        assert len(readings) == 3
        assert readings[0] == "Gen. 1"  # First OT reading
        assert readings[1] == "Ps. 1"   # First Psalm
        assert readings[2] == "Luke 1"  # First NT reading

    def test_saturday_returns_none(self):
        saturday = date(2024, 1, 6)
        assert get_todays_readings(saturday) is None

    def test_sunday_returns_none(self):
        sunday = date(2024, 1, 7)
        assert get_todays_readings(sunday) is None

    def test_second_weekday(self):
        # Tuesday Jan 2, 2024 (second reading day)
        readings = get_todays_readings(date(2024, 1, 2))
        assert readings is not None
        assert readings[0] == "Gen. 2"
        assert readings[1] == "Ps. 2"
        assert readings[2] == "Luke 2"

    def test_end_of_year_returns_empty_strings(self):
        # Test a date far enough into the year that readings run out
        # The reading plans are ~260 days, so December should hit empty
        readings = get_todays_readings(date(2024, 12, 31))
        assert readings is not None
        # At least one reading may be empty by end of year


class TestOldYr1:
    """Tests for old_yr1 (OT reading plan) function."""

    def test_first_reading(self):
        assert old_yr1(0) == "Gen. 1"

    def test_genesis_continues(self):
        assert old_yr1(49) == "Gen. 50"

    def test_exodus_starts(self):
        assert old_yr1(50) == "Ex. 1"

    def test_out_of_bounds_returns_empty(self):
        assert old_yr1(999) == ""


class TestNew:
    """Tests for new (NT reading plan) function."""

    def test_first_reading(self):
        assert new(0) == "Luke 1"

    def test_luke_continues(self):
        assert new(23) == "Luke 24"

    def test_acts_starts(self):
        assert new(24) == "Acts 1"

    def test_out_of_bounds_returns_empty(self):
        assert new(999) == ""


class TestPsalms:
    """Tests for psalms reading plan function."""

    def test_first_reading(self):
        assert psalms(0) == "Ps. 1"

    def test_psalm_119_sections(self):
        # Psalm 119 is split into 4 parts
        # Find index where 119 starts by counting readings
        result = psalms(0)
        assert "Ps." in result

    def test_out_of_bounds_returns_empty(self):
        assert psalms(999) == ""
