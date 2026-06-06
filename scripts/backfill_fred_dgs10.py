from macrodata_norway.repository.series import load_series
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
        description="US Federal Reserve Economic Data",
    )

    series_id = ensure_series(
        source_id=source_id,  # Source id returns the series ID so we can use it directly here when inserting new data :)
        source_series_id="DGS10",
        name="Market Yield on U.S treasury Securities at 10-year Constant Maturity",
        description="10-year Treasury constant maturity rate from FRED",
        category="rates",
        geography="US",
        unit="percent",
        frequency="daily",
        maturity="10Y",
    )

    client = FredClient()

    payload = client.fetch_observations(series_id="DGS10")

    observations = normalise_fred_observations(
        source_series_id="DGS10", payload=payload
    )

    changed_rows = upsert_observations(series_id=series_id, observations=observations)

    df = load_series(source_name="FRED", source_series_id="DGS10")

    print(f"Fetched observations: {len(observations)}")
    print(f"Inserted or updated rows: {changed_rows}")
    print()
    print(df.tail)


if __name__ == "__main__":
    main()
