-- Creation of the tables/schema is in the core folder

--Insert dummy data into the source table
INSERT INTO data_source (
    name,
    base_url,
    description
)
VALUES (
    'FRED',
    'https://fred.stlouisfed.org',
    'Federal Reserve Economic Data'
)
ON CONFLICT (name) DO NOTHING; --Include this so that the query can be run again without creating duplicates

--Insert dummy data into the series table
/*
Insert a new series called DGS10, and get its source_id by looking up the row in data_source where name = 'FRED'.


*/

INSERT INTO series ( -- The order of the columns here matters
    source_id,
    source_series_id,
    name,
    category,
    geography,
    unit,
    frequency,
    maturity
)
SELECT /*Use SELECT to ensure correct columns are passed? Could have used VALUES (1, 'DGS10', ...), 
        but source_id for FRED might be 1, 2 stc. 
        Instead of hardcoding the ID, use WHERE to select the row where the source name is FRED. 
        
        SELECT provides the values 

        */
    id, -- This value is taken from the data_sorce table. This is important because it is used in the CONFLICT statement later to ensure unique observations
        -- The UNIQUE constraint stems from how the table is created. source_id and source_series_id combination must be unique
    'DGS10', -- The order here must match the order of the columns above
    'US 10-year Treasury yield',
    'rates',
    'US',
    'percent',
    'daily',
    '10Y'
FROM data_source
WHERE name = 'FRED'
ON CONFLICT (source_id, source_series_id) DO NOTHING; -- Ensuers uniqueness and instead of raising error just does nothing


-- Inserting some fake values

/*

1. Finds the correct series ID for FRED / DGS10.
2. Creates three temporary date-value rows.
3. Combines the series ID with each date-value row.
4. Inserts them into observation, or updates them if they already exist.

*/

INSERT INTO observation (
    series_id,
    observation_date,
    value
)
SELECT
    s.id, --The observations.series_id must point to the relevant row in the series table
    v.observation_date::date, -- The :: suntax means cast this data to a specific type. The table expects specific types, see the schema for the tables
    v.value::numeric
FROM series s
JOIN data_source ds -- Point to the data_source table. The table series.source_id points to data_source_id. This allows the filter WHERE ds.name = 'FRED', as seen earlier
    ON ds.id = s.source_id
    CROSS JOIN ( --CROSS JOIN combines every row from the left side with every row from the right side. Here, the left side is the selected series, and the right side is the temp table v
    VALUES
        ('2024-01-02', 3.95),
        ('2024-01-03', 3.91),
        ('2024-01-04', 4.10)
) AS v(observation_date, value) -- This creates a small temporary table caleld v, with column names so they can be referred to (see the SELECT statement). Same idea as with aliases, but now with a table
WHERE ds.name = 'FRED' -- Filter on both the ds.name and s.source_series_id to ensure uniqueness. There might be a case where anothyer series ID is also called DGS10. 
  AND s.source_series_id = 'DGS10'
ON CONFLICT (series_id, observation_date)
DO UPDATE SET
    value = EXCLUDED.value,
    retrieved_at = now(),
    updated_at = now();

/* 

Tips for building complicated sql queries as above:

Start with SELECT, and finding the targeted series, in this case FRED DGS10.

SELECT
    s.id,
    ds.name,
    s.source_series_id,
    s.name
FROM series s
JOIN data_source ds
    ON ds.id = s.source_id
WHERE ds.name = 'FRED'
  AND s.source_series_id = 'DGS10';

SELECT *
FROM (
    VALUES
        ('2024-01-02', 3.95),
        ('2024-01-03', 3.91),
        ('2024-01-04', 3.99)
) AS v(observation_date, value);

Combined:

SELECT
    s.id AS series_id,
    v.observation_date,
    v.value
FROM series s
JOIN data_source ds
    ON ds.id = s.source_id
CROSS JOIN (
    VALUES
        ('2024-01-02', 3.95),
        ('2024-01-03', 3.91),
        ('2024-01-04', 3.99)
) AS v(observation_date, value)
WHERE ds.name = 'FRED'
  AND s.source_series_id = 'DGS10';

  Add type casts and then wrap it in the INSERT statement

  INSERT INTO observation (
    series_id,
    observation_date,
    value
)

Then add conflict handling

ON CONFLICT (series_id, observation_date)
DO UPDATE SET --In an ON CONFLICT DO UPDATE clause, EXCLUDED means: he row you tried to insert, but which caused a conflict. Now it updates the existing values int he table
    value = EXCLUDED.value,
    retrieved_at = now(),
    updated_at = now();

*/