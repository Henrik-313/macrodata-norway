from typing import Any

from sqlalchemy import text

from macrodata_norway.db.engine import get_engine


def ensure_data_source(
    name: str, base_url: str | None = None, description: str | None = None
) -> int:
    """
    Ensure that a data source exists.

    If the source does not exist, insert it.

    If it already exists, return the existing id.

    Returns
    -------
    int
        The id of the data_source_row
    """

    engine = get_engine()

    query = text(
        """
        INSERT INTO data_source (
            name,
            base_url,
            description
        )
        VALUES (
            :name,
            :base_url,
            :description
        )
        ON CONFLICT (name)
        DO UPDATE SET 
            base_url = COALESCE(EXCLUDED.base_url, data_source.base_url),
            description = COALESCE(EXCLUDED.description, data_source.description)
        RETURNING id;
        """
    )
    # RETURNING id: after inserting or updating row, give back the ID.
    # COALESCE means use a if NOT NULL, otherwise use b to ensure that if nothing is passed, the existing value is used

    with (
        engine.begin() as conn
    ):  # This pattern opens a database transaction, meaning that the sql query will only run if the code succeeds. If something fails SQLalchemy rolls back
        result = conn.execute(
            query,
            {"name": name, "base_url": base_url, "description": description},
        )

        source_id = result.scalar_one()  # Gets the ID of the inserted or updated row

        return source_id


def ensure_series(
    source_id: int,
    source_series_id: str,
    name: str,
    category: str,
    geography: str | None = None,
    unit: str | None = None,
    frequency: str | None = None,
    maturity: str | None = None,
    description: str | None = None,
    seasonal_adjustment: str | None = None,
    currency: str | None = None,
) -> int:
    """
    Ensure that a time series exists.

    If the series does not exist, insert it.
    If it already exists, update metadata and return the existing id.

    Returns
    -------

    int
        The id of the series row
    """

    engine = get_engine()

    query = text(
        """
        INSERT INTO series (
            source_id,
            source_series_id,
            name,
            description,
            category,
            geography,
            unit,
            frequency,
            seasonal_adjustment,
            currency,
            maturity
        )
        VALUES (
            :source_id,
            :source_series_id,
            :name,
            :description,
            :category,
            :geography,
            :unit,
            :frequency,
            :seasonal_adjustment,
            :currency,
            :maturity
        )
        ON CONFLICT (source_id, source_series_id)
        DO UPDATE SET 
            name = EXCLUDED.name,
            description = EXCLUDED.description,
            category = EXCLUDED.category,
            geography = EXCLUDED.geography,
            unit = EXCLUDED.unit,
            frequency = EXCLUDED.frequency,
            seasonal_adjustment = EXCLUDED.seasonal_adjustment,
            currency = EXCLUDED.currency,
            maturity = EXCLUDED.maturity,
            updated_at = now()
        RETURNING id;
        """
    )

    with engine.begin() as conn:
        result = conn.execute(
            query,
            {
                "source_id": source_id,
                "source_series_id": source_series_id,
                "name": name,
                "description": description,
                "category": category,
                "geography": geography,
                "unit": unit,
                "frequency": frequency,
                "seasonal_adjustment": seasonal_adjustment,
                "currency": currency,
                "maturity": maturity,
            },
        )

        series_id = result.scalar_one()

        return series_id


def upsert_observations(
    series_id: int,
    observations: list[dict[str, Any]],
) -> int:
    """
    Insert or update observations for one series.

    Each observation dictionary should contain:

        {
            "observation_date": date(...),
            "value": Decimal(...) or None,
            "value_text": str or None,
        }

    Returns
    -------
    int
        Number of rows inserted or updated according to PostgreSQL
    """

    if not observations:
        return 0

    engine = get_engine()

    query = text(
        """
        INSERT INTO observation (
            series_id,
            observation_date,
            value,
            value_text,
            retrieved_at,
            updated_at
        )
        VALUES (
            :series_id,
            :observation_date,
            :value,
            :value_text,
            now(),
            now()
        )
        ON CONFLICT (series_id, observation_date)
        DO UPDATE SET
            value = EXCLUDED.value,
            value_text = EXCLUDED.value_text,
            retrieved_at = now(),
            updated_at = now()
        WHERE observation.value IS DISTINCT FROM EXCLUDED.value
            OR observation.value_text IS DISTINCT FROM EXCLUDED.value_text;
        """
    )
    # IS DISTINCT FROM ensures that rows are only updated if the actual value changed

    rows = [
        {
            "series_id": series_id,
            "observation_date": obs["observation_date"],
            "value": obs.get("value"),
            "value_text": obs.get("value_text"),
        }
        for obs in observations
    ]

    with engine.begin() as conn:
        result = conn.execute(query, rows)

        return result.rowcount or 0
