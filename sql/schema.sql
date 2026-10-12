CREATE TABLE IF NOT EXISTS temperature_readings (
    reading_id TEXT PRIMARY KEY,
    device_id TEXT NOT NULL,
    observed_at TIMESTAMP NOT NULL,
    temperature DOUBLE PRECISION NOT NULL,
    location TEXT NOT NULL CHECK (location IN ('In', 'Out'))
);
CREATE INDEX IF NOT EXISTS idx_readings_date ON temperature_readings(observed_at);
