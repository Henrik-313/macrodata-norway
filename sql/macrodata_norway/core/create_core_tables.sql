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

CREATE INDEX IF NOT EXISTS idx_observation_series_date
ON observation (series_id, observation_date);
