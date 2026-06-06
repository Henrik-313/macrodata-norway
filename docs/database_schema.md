# Core schema

Stored in sql/macrodata_norway/core/create_core_tables.sql

```sql 
CREATE TABLE IF NOT EXISTS data_source (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    base_url TEXT,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS series (
    id SERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES data_source(id),
    source_series_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    geography TEXT,
    unit TEXT,
    frequency TEXT,
    seasonal_adjustment TEXT,
    currency TEXT,
    maturity TEXT,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_series_source_series_id
        UNIQUE (source_id, source_series_id)
);

CREATE TABLE IF NOT EXISTS observation (
    id BIGSERIAL PRIMARY KEY,
    series_id INTEGER NOT NULL REFERENCES series(id) ON DELETE CASCADE,
    observation_date DATE NOT NULL,
    value NUMERIC,
    value_text TEXT,
    realtime_start DATE,
    realtime_end DATE,
    source_updated_at TIMESTAMPTZ,
    retrieved_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_observation_series_date
        UNIQUE (series_id, observation_date)
);

CREATE TABLE IF NOT EXISTS ingestion_run (
    id BIGSERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES data_source(id),
    run_type TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    rows_fetched INTEGER DEFAULT 0,
    rows_inserted INTEGER DEFAULT 0,
    rows_updated INTEGER DEFAULT 0,
    rows_skipped INTEGER DEFAULT 0,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_series_source_id
ON series (source_id);

CREATE INDEX IF NOT EXISTS idx_observation_series_id
ON observation (series_id);

CREATE INDEX IF NOT EXISTS idx_observation_date
ON observation (observation_date);

CREATE INDEX IF NOT EXISTS idx_observation_series_date;
```
# SSB specific schema
Stored in file: sql/macrodata/create_tables.sql

```sql
CREATE TABLE IF NOT EXISTS ssb_tables (
	table_id TEXT PRIMARY KEY,
	title TEXT NOT NULL,
	short_title TEXT,
	source TEXT,
	last_update TIMESTAMPTZ,
	note TEXT,
	created_at TIMESTAMPTZ DEFAULT now()
	);

CREATE TABLE IF NOT EXISTS ssb_dimensions (
	id BIGSERIAL PRIMARY KEY,
	table_id TEXT NOT NULL REFERENCES ssb_tables(table_id) ON DELETE CASCADE,
	dimension_name TEXT NOT NULL,
	dimension_label TEXT,
	position INTEGER NOT NULL,
	UNIQUE (table_id, dimension_name)
	);

CREATE TABLE IF NOT EXISTS ssb_dimension_categories (
    id BIGSERIAL PRIMARY KEY,
    table_id TEXT NOT NULL REFERENCES ssb_tables(table_id) ON DELETE CASCADE,
    dimension_name TEXT NOT NULL,
    category_code TEXT NOT NULL,
    category_label TEXT,
    category_position INTEGER,
    UNIQUE (table_id, dimension_name, category_code)
);

CREATE TABLE IF NOT EXISTS ssb_observations (
    id BIGSERIAL PRIMARY KEY,
    table_id TEXT NOT NULL REFERENCES ssb_tables(table_id) ON DELETE CASCADE,
    dimension_key JSONB NOT NULL,
    value NUMERIC,
    fetched_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (table_id, dimension_key)
);

CREATE INDEX IF NOT EXISTS idx_ssb_observations_table_id
ON ssb_observations (table_id);

CREATE INDEX IF NOT EXISTS idx_ssb_observations_dimension_key
ON ssb_observations
USING GIN (dimension_key);
``` 