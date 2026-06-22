-- NYC Taxi schema: real-world ride data used for time-series and aggregation queries.
-- Based on the NYC TLC public dataset structure.

CREATE TABLE IF NOT EXISTS nyc_taxi_zones (
    location_id     INTEGER     PRIMARY KEY,
    borough         VARCHAR(50),
    zone            VARCHAR(100),
    service_zone    VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS nyc_payment_types (
    payment_type_id     INTEGER     PRIMARY KEY,
    payment_type_name   VARCHAR(50) NOT NULL,
    description         TEXT
);

CREATE TABLE IF NOT EXISTS nyc_rate_codes (
    rate_code_id    INTEGER     PRIMARY KEY,
    rate_code_name  VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS nyc_trips (
    trip_id                 BIGSERIAL       PRIMARY KEY,
    vendor_id               INTEGER,
    pickup_datetime         TIMESTAMP       NOT NULL,
    dropoff_datetime        TIMESTAMP       NOT NULL,
    passenger_count         SMALLINT,
    trip_distance           NUMERIC(8,2),
    pickup_location_id      INTEGER         REFERENCES nyc_taxi_zones(location_id),
    dropoff_location_id     INTEGER         REFERENCES nyc_taxi_zones(location_id),
    rate_code_id            INTEGER         REFERENCES nyc_rate_codes(rate_code_id),
    payment_type_id         INTEGER         REFERENCES nyc_payment_types(payment_type_id),
    fare_amount             NUMERIC(8,2),
    extra                   NUMERIC(8,2),
    mta_tax                 NUMERIC(8,2),
    tip_amount              NUMERIC(8,2),
    tolls_amount            NUMERIC(8,2),
    improvement_surcharge   NUMERIC(8,2),
    congestion_surcharge    NUMERIC(8,2),
    total_amount            NUMERIC(8,2)
);

-- Partial index for time-range queries (very common for taxi analytics).
CREATE INDEX IF NOT EXISTS nyc_trips_pickup_datetime_idx
    ON nyc_trips (pickup_datetime DESC);

CREATE INDEX IF NOT EXISTS nyc_trips_dropoff_datetime_idx
    ON nyc_trips (dropoff_datetime DESC);
