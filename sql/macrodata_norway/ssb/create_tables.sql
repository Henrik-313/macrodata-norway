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
