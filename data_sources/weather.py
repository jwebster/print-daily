# Weather data from Open-Meteo API (free, no key required)

import logging
import requests
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

# Witney, Oxfordshire coordinates
WITNEY_LAT = 51.7856
WITNEY_LON = -1.4857

# WMO weather codes to descriptions
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


@dataclass
class WeatherData:
    temperature: float
    condition: str
    high: float
    low: float
    sunrise: str
    sunset: str
    feels_like: float | None = None


def get_weather() -> WeatherData | None:
    """Fetch today's weather for Witney from Open-Meteo."""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": WITNEY_LAT,
            "longitude": WITNEY_LON,
            "current": "temperature_2m,apparent_temperature,weather_code",
            "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset",
            "timezone": "Europe/London",
            "forecast_days": 1,
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})
        daily = data.get("daily", {})

        weather_code = current.get("weather_code", 0)
        condition = WMO_CODES.get(weather_code, "Unknown")

        # Parse sunrise/sunset times (format: "2025-12-30T08:12")
        sunrise_raw = daily.get("sunrise", [""])[0]
        sunset_raw = daily.get("sunset", [""])[0]

        sunrise = ""
        sunset = ""
        if sunrise_raw:
            sunrise = datetime.fromisoformat(sunrise_raw).strftime("%H:%M")
        if sunset_raw:
            sunset = datetime.fromisoformat(sunset_raw).strftime("%H:%M")

        return WeatherData(
            temperature=round(current.get("temperature_2m", 0)),
            feels_like=round(current.get("apparent_temperature", 0)) if current.get("apparent_temperature") else None,
            condition=condition,
            high=round(daily.get("temperature_2m_max", [0])[0]),
            low=round(daily.get("temperature_2m_min", [0])[0]),
            sunrise=sunrise,
            sunset=sunset,
        )

    except requests.RequestException as e:
        logger.warning("Weather fetch failed: %s", e)
        return None
