from datetime import timedelta

from macrodata_norway.registry.fred import FRED_SERIES
from macrodata_norway.repository.series import get_latest_observation_date
from macrodata_norway.repository.write import (
    ensure_data_source,
    ensure_series,
    upsert_observations,
)
from macrodata_norway.sources.fred import (
    FredClient,
    normalise_fred_observations,
)


def main() -> None:
    source_id = ensure_data_source(
        name="FRED",
        base_url="https://fred.stlouisfed.org",
        description="Federal Reserve Economic Data",
    )

    client = FredClient()

    total_fetched = 0
    total_changed = 0

    for series_config in FRED_SERIES:
        source_series_id = series_config["source_series_id"]
        safety_buffer_days = series_config["safety_buffer_days"]

        print()
        print(f"Updating {source_series_id}: {series_config['name']}")

        series_id = ensure_series(
            source_id=source_id,
            source_series_id=source_series_id,
            name=series_config["name"],
            description=series_config["description"],
            category=series_config["category"],
            geography=series_config["geography"],
            unit=series_config["unit"],
            frequency=series_config["frequency"],
            maturity=series_config["maturity"],
        )

        latest_date = get_latest_observation_date(
            source_name="FRED",
            source_series_id=source_series_id,
        )

        if latest_date is None:
            observation_start = None
            print("No local observations found. Fetching full history.")
        else:
            observation_start = latest_date - timedelta(days=safety_buffer_days)
            print(f"Latest local observation: {latest_date}")
            print(f"Fetching from: {observation_start}")

        payload = client.fetch_observations(
            series_id=source_series_id,
            observation_start=observation_start,
        )

        observations = normalise_fred_observations(
            source_series_id=source_series_id,
            payload=payload,
        )

        changed_rows = upsert_observations(
            series_id=series_id,
            observations=observations,
        )

        total_fetched += len(observations)
        total_changed += changed_rows

        print(f"Fetched observations: {len(observations)}")
        print(f"Inserted or updated rows: {changed_rows}")

    print()
    print("FRED update complete.")
    print(f"Total observations fetched: {total_fetched}")
    print(f"Total inserted or updated rows: {total_changed}")


if __name__ == "__main__":
    main()
