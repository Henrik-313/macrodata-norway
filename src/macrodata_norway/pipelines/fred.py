from datetime import timedelta
from typing import Any

from macrodata_norway.registry.fred import FRED_SERIES
from macrodata_norway.repository.ingestion import (
    failed_ingestion_run,
    finish_ingestion_run,
    start_ingestion_run,
)
from macrodata_norway.repository.series import get_latest_observation_date
from macrodata_norway.repository.write import (
    ensure_data_source,
    ensure_series,
    upsert_observations,
)
from macrodata_norway.sources.fred import FredClient, normalise_fred_observations


def ensure_fred_source() -> int:
    """
    Ensure that the FRED data source exists and return its database id
    """

    return ensure_data_source(name="FRED")


def ensure_fred_series(source_id: int, series_config: dict[str, any]) -> int:

    return ensure_series(
        source_id=source_id,
        source_series_id=series_config["source_series_id"],
        name=series_config["name"],
        category=series_config["category"],
        geography=series_config["geography"],
        unit=series_config["unit"],
        frequency=series_config["frequency"],
        maturity=series_config["maturity"],
        description=series_config["description"],
    )


def backfill_fred() -> dict[str, Any]:
    """
    Fetch full history for all configured FRED series.

    Returns
    -------
    Summary of backfill operation as dict
    """

    source_id = ensure_fred_source()

    run_id = start_ingestion_run(source_id=source_id, run_type="historical_backfill")

    client = FredClient()

    total_fetched = 0

    total_changed = 0
    errors: list[str] = []

    try:
        for series_config in FRED_SERIES:
            source_series_id = series_config["source_series_id"]

            try:
                print(f"Backfilling {source_series_id}")

                series_id = ensure_fred_series(
                    source_id=source_id, series_config=series_config
                )

                payload = client.fetch_observations(series_id=source_series_id)

                observations = normalise_fred_observations(
                    source_series_id=source_series_id, payload=payload
                )

                changed_rows = upsert_observations(
                    series_id=series_id, observations=observations
                )

                print(f"Fetched observations: {len(observations)}")
                print(f"Inserted/Updated: {changed_rows}")

                total_fetched += len(observations)
                total_changed += changed_rows

            except Exception as exc:
                errors.append(f"{source_series_id}: {exc}")

            status = "partial" if errors else "success"
            error_message = "\n".join(errors) if errors else None

            finish_ingestion_run(
                run_id=run_id,
                status=status,
                rows_fetched=total_fetched,
                rows_inserted=total_changed,
                rows_skipped=max(total_fetched - total_changed, 0),
                error_message=error_message,
            )

            return {
                "status": status,
                "rows_fetched": total_fetched,
                "rows_changed": total_changed,
                "rows_updated": max(total_fetched - total_changed, 0),
                "errors": errors,
            }
    except Exception as exc:
        failed_ingestion_run(
            run_id=run_id,
            error_message=str(exc),
            rows_fetched=total_fetched,
            rows_updated=total_changed,
            rows_skipped=max(total_fetched - total_changed, 0),
        )

        raise


def update_fred() -> dict[str, Any]:
    """
    Incrementally update all configured FRED series.

    For each series:
    - find the latest locally stored observation date
    - subtract the configured time period safety buffer
    - fetch only recent data from FRED
    - upsert new or changed observations

    Returns
    -------
    Summary of update operation as dict
    """

    source_id = ensure_fred_source()

    run_id = start_ingestion_run(source_id=source_id, run_type="incremental_update")

    client = FredClient()

    total_fetched = 0
    total_changed = 0
    errors: list[str] = []

    try:
        for series_config in FRED_SERIES:
            source_series_id = series_config["source_series_id"]
            safety_buffer = series_config["safety_buffer_days"]

            print()
            print(f"Updating {source_series_id}: {series_config['name']}")

            try:
                series_id = ensure_fred_series(
                    source_id=source_id, series_config=series_config
                )

                latest_date = get_latest_observation_date(
                    source_name="FRED", source_series_id=source_series_id
                )

                if latest_date is None:
                    observation_start = None
                    print("No local observations found. Fetching full history")

                else:
                    observation_start = latest_date - timedelta(days=safety_buffer)
                    print(f"Latest local observation: {latest_date}")
                    print(f"Fetching from: {observation_start}")

                payload = client.fetch_observations(
                    series_id=source_series_id, observation_start=observation_start
                )

                observations = normalise_fred_observations(
                    source_series_id=source_series_id, payload=payload
                )

                changed_rows = upsert_observations(
                    series_id=series_id, observations=observations
                )

                total_fetched += len(observations)
                total_changed += changed_rows

                print(f"Fetched observations: {len(observations)}")
                print(f"Inserted or updated rows: {changed_rows}")

            except Exception as exc:
                error = f"{source_series_id}: {exc}"
                errors.append(error)
                print(f"ERROR: {error}")
                continue

        status = "partial" if errors else "success"
        error_message = "\n".join(errors) if errors else None

        finish_ingestion_run(
            run_id=run_id,
            status=status,
            rows_fetched=total_fetched,
            rows_updated=total_changed,
            rows_skipped=max(total_fetched - total_changed, 0),
            error_message=error_message,
        )

        return {
            "status": status,
            "rows_fetched": total_fetched,
            "rows_changed": total_changed,
            "rows_skipped": max(total_fetched - total_changed, 0),
            "errors": errors,
        }

    except Exception as exc:
        failed_ingestion_run(
            run_id=run_id,
            error_message=str(exc),
            rows_fetched=total_fetched,
            rows_updated=total_changed,
            rows_skipped=max(total_fetched - total_changed, 0),
        )
        raise
