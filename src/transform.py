# Transform 
from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, unix_timestamp, round, to_date, hour, when, dayofweek, avg, sum, count
)

def clean_and_transform(df: DataFrame) -> DataFrame:
    df = df.withColumn(
        "trip_duration_minutes",
        round(
            (unix_timestamp("tpep_dropoff_datetime") - unix_timestamp("tpep_pickup_datetime")) / 60,
            2
        )
    )

    df = df.filter((col("trip_duration_minutes") >= 1) & (col("trip_duration_minutes") <= 300))

    df = df.withColumn("trip_date", to_date(col("tpep_pickup_datetime")))
    df = df.withColumn("pickup_hour", hour(col("tpep_pickup_datetime")))
    df = df.withColumn(
        "is_weekend",
        when(dayofweek(col("tpep_pickup_datetime")).isin([1, 7]), 1).otherwise(0)
    )

    df = df.withColumn(
        "avg_speed_kmh",
        round((col("trip_distance") / (col("trip_duration_minutes") / 60)) * 1.60934, 2)
    )

    df = df.filter((col("avg_speed_kmh") > 0) & (col("avg_speed_kmh") <= 120))

    return df.select(
        col("VendorID"),
        col("tpep_pickup_datetime").alias("pickup_datetime"),
        col("tpep_dropoff_datetime").alias("dropoff_datetime"),
        col("passenger_count"),
        col("trip_distance"),
        col("PULocationID").alias("pickup_location_id"),
        col("DOLocationID").alias("dropoff_location_id"),
        col("payment_type"),
        col("fare_amount"),
        col("tip_amount"),
        col("total_amount"),
        col("trip_duration_minutes"),
        col("trip_date"),
        col("pickup_hour"),
        col("is_weekend"),
        col("avg_speed_kmh")
    )

def aggregate_daily_metrics(df: DataFrame) -> DataFrame:
    return (
        df.groupBy("trip_date")
        .agg(
            count("*").alias("total_trips"),
            round(avg("trip_distance"), 2).alias("avg_trip_distance"),
            round(avg("trip_duration_minutes"), 2).alias("avg_trip_duration_minutes"),
            round(sum("total_amount"), 2).alias("total_revenue"),
            round(avg("fare_amount"), 2).alias("avg_fare"),
            round(avg("tip_amount"), 2).alias("avg_tip")
        )
        .orderBy("trip_date")
    )

def aggregate_payment_metrics(df: DataFrame) -> DataFrame:
    return (
        df.groupBy("payment_type")
        .agg(
            count("*").alias("total_trips"),
            round(sum("total_amount"), 2).alias("total_revenue"),
            round(avg("fare_amount"), 2).alias("avg_fare"),
            round(avg("tip_amount"), 2).alias("avg_tip")
        )
        .orderBy("payment_type")
    )

def aggregate_zone_pair_metrics(df: DataFrame) -> DataFrame:
    return (
        df.groupBy("pickup_location_id", "dropoff_location_id")
        .agg(
            count("*").alias("total_trips"),
            round(avg("trip_distance"), 2).alias("avg_distance"),
            round(sum("total_amount"), 2).alias("total_revenue")
        )
        .orderBy(col("total_revenue").desc())
    )