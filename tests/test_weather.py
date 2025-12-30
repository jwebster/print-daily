"""Tests for weather module."""

import pytest
from unittest.mock import patch, Mock
from data_sources.weather import get_weather, WeatherData, WMO_CODES


class TestWmoCodes:
    """Tests for WMO weather code mapping."""

    def test_common_codes_exist(self):
        assert 0 in WMO_CODES  # Clear sky
        assert 3 in WMO_CODES  # Overcast
        assert 61 in WMO_CODES  # Rain
        assert 71 in WMO_CODES  # Snow

    def test_codes_have_descriptions(self):
        for code, description in WMO_CODES.items():
            assert isinstance(description, str)
            assert len(description) > 0


class TestWeatherData:
    """Tests for WeatherData dataclass."""

    def test_creation(self):
        weather = WeatherData(
            temperature=15.5,
            condition="Partly cloudy",
            high=18.0,
            low=10.0,
            sunrise="07:30",
            sunset="17:45"
        )
        assert weather.temperature == 15.5
        assert weather.condition == "Partly cloudy"
        assert weather.high == 18.0
        assert weather.low == 10.0
        assert weather.sunrise == "07:30"
        assert weather.sunset == "17:45"
        assert weather.feels_like is None

    def test_optional_feels_like(self):
        weather = WeatherData(
            temperature=15.0,
            condition="Clear",
            high=18.0,
            low=10.0,
            sunrise="07:30",
            sunset="17:45",
            feels_like=13.0
        )
        assert weather.feels_like == 13.0


class TestGetWeather:
    """Tests for get_weather function."""

    @patch('data_sources.weather.requests.get')
    def test_parses_api_response(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "current": {
                "temperature_2m": 12.5,
                "apparent_temperature": 10.2,
                "weather_code": 2
            },
            "daily": {
                "temperature_2m_max": [15.0],
                "temperature_2m_min": [8.0],
                "sunrise": ["2024-01-15T07:45"],
                "sunset": ["2024-01-15T16:30"]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_weather()

        assert result is not None
        assert result.temperature == 12  # rounded
        assert result.condition == "Partly cloudy"
        assert result.high == 15
        assert result.low == 8
        assert result.sunrise == "07:45"
        assert result.sunset == "16:30"
        assert result.feels_like == 10

    @patch('data_sources.weather.requests.get')
    def test_handles_unknown_weather_code(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "current": {
                "temperature_2m": 10.0,
                "weather_code": 999  # Unknown code
            },
            "daily": {
                "temperature_2m_max": [12.0],
                "temperature_2m_min": [8.0],
                "sunrise": ["2024-01-15T07:00"],
                "sunset": ["2024-01-15T17:00"]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_weather()

        assert result is not None
        assert result.condition == "Unknown"

    @patch('data_sources.weather.requests.get')
    def test_handles_request_error(self, mock_get):
        import requests
        mock_get.side_effect = requests.RequestException("Network error")

        result = get_weather()

        assert result is None

    @patch('data_sources.weather.requests.get')
    def test_handles_missing_data(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "current": {},
            "daily": {}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_weather()

        assert result is not None
        assert result.temperature == 0
        assert result.condition == "Clear sky"  # WMO code 0 default
