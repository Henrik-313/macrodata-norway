from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from macrodata_norway.config import get_settings

FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"


def parse_fred_value(raw_value: str) -> Decimal | None:
    """
    Convert a FRED value string into a Decimal.

    FRED uses "." for some missing observations.
    """

    raw_value = raw_value.strip()

    if raw_value in {"", " ", "NaN", "nan"}:
        return None

    try:
        return Decimal(
            raw_value
        )  # Use Decimal instead of float to aviod floating-point rounding issues

    except InvalidOperation:
        return None


def normalise_fred_observations(
    source_series_id: str,
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Convert raw FRED API JSON into our database observation format.

    FRED gives observations like:
        {
            "realtime_start": "2024-01-01",
            "realtime_end": "2024-01-01",
            "date": "2024-01-02",
            "value": "3.95"
        }

    We convert that into dictionaries for upsert_obsertvation()
    """

    observations: list[dict[str, Any]] = []

    for item in payload["observations"]:
        raw_value = item["value"]
        parsed_value = parse_fred_value(raw_value=raw_value)

        # Normalisation step
        observations.append(
            {
                "source_series_id": source_series_id,
                "observation_date": date.fromisoformat(item["date"]),
                "value": parsed_value,
                "value_text": raw_value if parsed_value is None else None,
                "realtime_start": date.fromisoformat(item["realtime_start"])
                if item.get("realtime_start")
                else None,
                "realtime_end": date.fromisoformat(item["realtime_end"])
                if item.get("realtime_end")
                else None,
            }
        )

    return observations


class FredClient:
    """
    Small client for the official FRED series observations API.
    """

    def __init__(self, api_key: str | None = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.fred_api_key

        if not self.api_key:
            raise RuntimeError(
                "FRED API KEY is missing. Supply it directly or add it to .env file"
            )

    def fetch_observations(
        self,
        series_id: str,
        observation_start: date | None = None,
        observation_end: date | None = None,
    ) -> dict[str, Any]:
        """
        Fetch observations for one FRED series.

        Parameters
        ----------
        series_id:
            FRED series ID, for example "DGS10".

        observation_start:
            Optional start date.

        observation_end:
            Optional end date.
        """

        params: dict[str, Any] = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
        }

        if observation_start is not None:
            params["observation_start"] = observation_start.isoformat()

        if observation_end is not None:
            params["observation_end"] = observation_end.isoformat()

        response = httpx.get(FRED_OBSERVATIONS_URL, params=params, timeout=30)

        response.raise_for_status()

        return response.json()
