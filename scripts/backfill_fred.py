from macrodata_norway.registry.fred import FRED_SERIES
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

    # Ensure data source is registeder in main table

    source_id = ensure_data_source(
        name="FRED",
        base_url="https://fred.stlouisfed.org",
        description="US Federal Reserve Economic Data",
    )

    client = FredClient()

    total_fetched = 0

    total_changed = 0

    for series_config in FRED_SERIES:
        source_series_id = series_config["source_series_id"]

        # Ensure series exist in the databse

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

        print(f"Backfilling {source_series_id}")

        payload = client.fetch_observations(series_id=source_series_id)

        observations = normalise_fred_observations(
            source_series_id=source_series_id, payload=payload
        )

        changed_rows = upsert_observations(
            series_id=series_id,
            observations=observations,
        )

        print(f"Fetched observations: {len(observations)}")
        print(f"Inserted/Updated: {changed_rows}")
        print("Completed bakfilling - moving to next series")

        total_fetched += len(observations)
        total_changed += changed_rows

    print()
    print("FRED backfill complete.")
    print(f"Total observations fetched: {total_fetched}")
    print(f"Total inserted or updated rows: {total_changed}")


if __name__ == "__main__":
    main()
