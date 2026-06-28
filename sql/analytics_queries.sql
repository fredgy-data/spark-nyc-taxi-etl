-- SQL queries
-- 1. Daily revenue and trip volume
SELECT
    trip_date,
    total_trips,
    total_revenue
FROM agg_daily_trip_metrics
ORDER BY trip_date;

-- 2. Payment type performance
SELECT
    payment_type,
    total_trips,
    total_revenue,
    avg_fare,
    avg_tip
FROM agg_payment_type_metrics
ORDER BY total_revenue DESC;

-- 3. Top route pairs by revenue
SELECT
    pickup_location_id,
    dropoff_location_id,
    total_trips,
    total_revenue
FROM agg_zone_pair_metrics
ORDER BY total_revenue DESC
LIMIT 10;

-- 4. Peak pickup hours
SELECT
    pickup_hour,
    COUNT(*) AS total_trips
FROM fact_taxi_trips
GROUP BY pickup_hour
ORDER BY total_trips DESC;

-- 5. Average trip duration per day
SELECT
    trip_date,
    AVG(trip_duration_minutes) AS avg_duration
FROM fact_taxi_trips
GROUP BY trip_date
ORDER BY trip_date;

-- 6. Top pickup zones by trip volume
SELECT
    pickup_location_id,
    COUNT(*) AS total_trips
FROM fact_taxi_trips
GROUP BY pickup_location_id
ORDER BY total_trips DESC
LIMIT 10;