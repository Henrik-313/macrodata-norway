import pandas as pd
from sqlalchemy import text

from macrodata_norway.db.engine import get_engine


def main() -> None:
    engine = get_engine()

    query = text(
        """
        SELECT
            ds.name AS source,
            s.source_series_id,
            s.name AS series_name,
            o.observation_date,
            o.value,
            s.unit
        FROM observation o
        JOIN series s
            ON s.id = o.series_id
        JOIN data_source ds
            ON ds.id = s.source_id
        WHERE ds.name = 'FRED'
          AND s.source_series_id = 'DGS10'
        ORDER BY o.observation_date;
        """
    )

    df = pd.read_sql(query, engine)

    print(df)


if __name__ == "__main__":
    main()
