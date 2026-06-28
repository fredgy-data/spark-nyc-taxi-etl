# Validate logic
from pyspark.sql import DataFrame
from pyspark.sql.functions import col

REQUIRED_COLUMNS = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "PULocationID",
    "DOLocationID",
    "payment_type",
    "fare_amount",
    "tip_amount",
    "total_amount"
]

def validate_required_columns(df: DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

def apply_quality_filters(df: DataFrame) -> DataFrame:
    return (
        df
        .filter(col("tpep_pickup_datetime").isNotNull())
        .filter(col("tpep_dropoff_datetime").isNotNull())
        .filter(col("trip_distance") > 0)
        .filter(col("fare_amount") >= 0)
        .filter(col("total_amount") >= 0)
        .filter((col("passenger_count") >= 1) & (col("passenger_count") <= 6))
    )