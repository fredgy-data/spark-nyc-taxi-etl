-- SQL create tables
CREATE TABLE IF NOT EXISTS fact_taxi_trips (
    vendorid INTEGER,
    pickup_datetime TIMESTAMP,
    dropoff_datetime TIMESTAMP,
    passenger_count INTEGER,
    trip_distance NUMERIC,
    pickup_location_id INTEGER,
    dropoff_location_id INTEGER,
    payment_type INTEGER,
    fare_amount NUMERIC,
    tip_amount NUMERIC,
    total_amount NUMERIC,
    trip_duration_minutes NUMERIC,
    trip_date DATE,
    pickup_hour INTEGER,
    is_weekend INTEGER,
    avg_speed_kmh NUMERIC
);

CREATE TABLE IF NOT EXISTS agg_daily_trip_metrics (
    trip_date DATE,
    total_trips INTEGER,
    avg_trip_distance NUMERIC,
    avg_trip_duration_minutes NUMERIC,
    total_revenue NUMERIC,
    avg_fare NUMERIC,
    avg_tip NUMERIC
);

CREATE TABLE IF NOT EXISTS agg_payment_type_metrics (
    payment_type INTEGER,
    total_trips INTEGER,
    total_revenue NUMERIC,
    avg_fare NUMERIC,
    avg_tip NUMERIC
);

CREATE TABLE IF NOT EXISTS agg_zone_pair_metrics (
    pickup_location_id INTEGER,
    dropoff_location_id INTEGER,
    total_trips INTEGER,
    avg_distance NUMERIC,
    total_revenue NUMERIC
);