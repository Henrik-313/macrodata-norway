SELECT
    s.id,
    ds.name AS source, -- AS renames the column, in this case from name to source
    s.source_series_id,
    s.name,
    s.category,
    s.geography,
    s.unit,
    s.frequency,
    s.maturity
FROM series s -- Gives the table the alias s
JOIN data_source ds
    ON ds.id = s.source_id;