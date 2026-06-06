from macrodata_norway.repository.series import list_series


def main() -> None:

    df = list_series()

    if df.empty:
        print("No series found")
        return

    print(df)


if __name__ == "__main__":
    main()
