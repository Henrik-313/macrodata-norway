from macrodata_norway.repository.series import load_series


def main() -> None:
    for series_id in ["DGS2", "DGS10", "T10Y2Y", "FEDFUNDS"]:
        df = load_series(
            source_name="FRED",
            source_series_id=series_id,
        )

        print()
        print("=" * 80)
        print(series_id)
        print("=" * 80)
        print(df.tail)


if __name__ == "__main__":
    main()
