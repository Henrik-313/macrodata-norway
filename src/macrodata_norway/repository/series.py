import pandas as pd
from sqlalchemy import text

from macrodata_norway.db.engine import get_engine


def load_series(source_name: str, source_series_id: str) -> pd.DataFrame:
    """
    Load one time series from the database.

    Parameters
    ----------
    source_name:
        Name of the data source, for example "FRED".

    source_series_id:
        Series ID used by the original data source, for example "DGS10".

    Returns
    --------
    pd.DataFrame
        A dataframe with observation_date, value, unit, and metadata
    """
    engine = get_engine()

    query = text(
        """
        SELECT
            ds.name AS source,
            s.source_series_id ,
            s.name AS series_name,
            s.category,
            s.geography,
            s.unit,
            s.frequency,
            s.maturity,
            o.observation_date,
            o.value
        FROM observation o
        JOIN series s
            ON s.id = o.series_id
        JOIN data_source ds
            ON ds.id = source_id
        WHERE ds.name = :source_name
            AND s.source_series_id = :source_series_id -- These are parameters that can be passed later. Better compared to f-strings as they are volulnerable to sql-injections
        ORDER BY o.observation_date;
        """
    )

    return pd.read_sql(
        query,
        engine,
        params={"source_name": source_name, "source_series_id": source_series_id},
    )
