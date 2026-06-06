from datetime import date
from decimal import Decimal

from macrodata_norway.repository.series import load_series
from macrodata_norway.repository.write import (
    ensure_data_source,
    ensure_series,
    upsert_observations,
)


def main() -> None:
    source_id = ensure_data_source(
        name="FRED",
        base_url="https://fred.stlouisfed.org",
        description="Federal Reserve Economic Data",
    )

    series_id = ensure_series(
        source_id=source_id,
        source_series_id="DGS10",
        name="US 10-year Treasury yield",
        category="rates",
        geography="US",
        unit="percent",
        frequency="daily",
        maturity="10Y",
    )

    observations = [
        {
            "observation_date": date(2024, 1, 2),
            "value": Decimal("3.95"),
        },
        {
            "observation_date": date(2024, 1, 3),
            "value": Decimal("3.91"),
        },
        {
            "observation_date": date(2024, 1, 4),
            "value": Decimal("3.995"),
        },
    ]

    changed_rows = upsert_observations(
        series_id=series_id,
        observations=observations,
    )

    print(f"Source id: {source_id}")
    print(f"Series id: {series_id}")
    print(f"Rows inserted or updated: {changed_rows}")

    df = load_series(source_name="FRED", source_series_id="DGS10")
    print()
    print(df)


if __name__ == "__main__":
    main()
