from datetime import date

from macrodata_norway.sources.fred import (
    FredClient,
    normalise_fred_observations,
)


def main() -> None:
    client = FredClient()

    payload = client.fetch_observations(
        series_id="DGS10",
        observation_start=date(2026, 1, 1),
    )

    observations = normalise_fred_observations(
        source_series_id="DGS10",
        payload=payload,
    )

    print(f"Observations fetched: {len(observations)}")
    print("First 5 observations:")
    for obs in observations[:5]:
        print(obs)

    print()
    print("Last 5 observations:")
    for obs in observations[-5:]:
        print(obs)


if __name__ == "__main__":
    main()
