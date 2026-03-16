"""Solar battery schedule from the solar dashboard API."""

import logging
import os
from dataclasses import dataclass, field

import requests

logger = logging.getLogger(__name__)

SOLAR_API_URL = os.environ.get(
    "SOLAR_API_URL", "https://solar.james-webster.co.uk/api/plan"
)


@dataclass
class SolarSummary:
    """Key facts from today's solar/battery plan."""
    solar_kwh: float | None = None
    solar_source: str | None = None
    projected_cost: float | None = None
    saving: float | None = None
    cfg_on: bool = False
    dtg_on: bool = False
    plan_time: str | None = None
    battery_soc: int | None = None
    agile_low: int | None = None
    agile_high: int | None = None
    cheapest_slots: list[dict] = field(default_factory=list)
    best_solar_window: dict | None = None


def get_solar_summary() -> SolarSummary | None:
    """Fetch the solar plan summary from the dashboard API."""
    try:
        resp = requests.get(SOLAR_API_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.warning("Failed to fetch solar plan: %s", e)
        return None

    plan = data.get("plan", {})
    s = SolarSummary(
        solar_kwh=plan.get("solar_kwh"),
        solar_source=plan.get("solar_source"),
        projected_cost=plan.get("cost"),
        saving=plan.get("saving"),
        cfg_on=plan.get("cfg_on", False),
        dtg_on=plan.get("dtg_on", False),
        plan_time=plan.get("plan_time"),
        battery_soc=plan.get("battery_soc"),
        agile_low=plan.get("agile_low"),
        agile_high=plan.get("agile_high"),
        cheapest_slots=data.get("cheapest_slots", []),
        best_solar_window=data.get("best_solar_window"),
    )
    return s
