from macrodata_norway.repository.series import load_series


def main() -> None:
    df = load_series(source_name="FRED", source_series_id="DGS10")

    print(df)

    print()
    print("Number of observations", len(df))

    if not df.empty:
        print("First date:", df["observation_date"].min())
        print("Last date:", df["observation_date"].max())


if __name__ == "__main__":
    main()
