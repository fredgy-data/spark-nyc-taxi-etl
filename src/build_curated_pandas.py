import os
import yaml
import pandas as pd


def load_config(path: str = "config/config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def clean_and_transform_pandas(df: pd.DataFrame) -> pd.DataFrame:
    required_columns = [
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

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"], errors="coerce")
    df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"], errors="coerce")

    df = df[df["tpep_pickup_datetime"].notna()]
    df = df[df["tpep_dropoff_datetime"].notna()]
    df = df[df["trip_distance"] > 0]
    df = df[df["fare_amount"] >= 0]
    df = df[df["total_amount"] >= 0]
    df = df[(df["passenger_count"] >= 1) & (df["passenger_count"] <= 6)]

    df["trip_duration_minutes"] = (
        (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 60
    ).round(2)

    df = df[(df["trip_duration_minutes"] >= 1) & (df["trip_duration_minutes"] <= 300)]

    df["trip_date"] = df["tpep_pickup_datetime"].dt.date
    df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
    df["is_weekend"] = df["tpep_pickup_datetime"].dt.dayofweek.isin([5, 6]).astype(int)

    df["avg_speed_kmh"] = (
        (df["trip_distance"] / (df["trip_duration_minutes"] / 60)) * 1.60934
    ).round(2)

    df = df[(df["avg_speed_kmh"] > 0) & (df["avg_speed_kmh"] <= 120)]

    final_df = df[[
        "VendorID",
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
        "passenger_count",
        "trip_distance",
        "PULocationID",
        "DOLocationID",
        "payment_type",
        "fare_amount",
        "tip_amount",
        "total_amount",
        "trip_duration_minutes",
        "trip_date",
        "pickup_hour",
        "is_weekend",
        "avg_speed_kmh"
    ]].copy()

    final_df = final_df.rename(columns={
        "tpep_pickup_datetime": "pickup_datetime",
        "tpep_dropoff_datetime": "dropoff_datetime",
        "PULocationID": "pickup_location_id",
        "DOLocationID": "dropoff_location_id"
    })

    return final_df


def main() -> None:
    config = load_config()
    raw_path = config["raw_data_path"]
    curated_dir = "data/curated"

    ensure_dir(curated_dir)

    print("STEP 1: Reading raw parquet with pandas")
    df = pd.read_parquet(raw_path)

    print("STEP 2: Cleaning and transforming raw data in pandas")
    clean_df = clean_and_transform_pandas(df)

    print("STEP 3: Building daily metrics")
    daily_metrics = (
        clean_df.groupby("trip_date", as_index=False)
        .agg(
            total_trips=("trip_date", "count"),
            avg_trip_distance=("trip_distance", "mean"),
            avg_trip_duration_minutes=("trip_duration_minutes", "mean"),
            total_revenue=("total_amount", "sum"),
            avg_fare=("fare_amount", "mean"),
            avg_tip=("tip_amount", "mean")
        )
    )

    print("STEP 4: Building payment metrics")
    payment_metrics = (
        clean_df.groupby("payment_type", as_index=False)
        .agg(
            total_trips=("payment_type", "count"),
            total_revenue=("total_amount", "sum"),
            avg_fare=("fare_amount", "mean"),
            avg_tip=("tip_amount", "mean")
        )
    )

    print("STEP 5: Building zone pair metrics")
    zone_pair_metrics = (
        clean_df.groupby(["pickup_location_id", "dropoff_location_id"], as_index=False)
        .agg(
            total_trips=("pickup_location_id", "count"),
            avg_distance=("trip_distance", "mean"),
            total_revenue=("total_amount", "sum")
        )
        .sort_values("total_revenue", ascending=False)
    )

    print("STEP 6: Rounding numeric columns")
    for table in [daily_metrics, payment_metrics, zone_pair_metrics]:
        numeric_cols = table.select_dtypes(include="number").columns
        table[numeric_cols] = table[numeric_cols].round(2)

    print("STEP 7: Writing curated parquet files")
    daily_metrics.to_parquet(os.path.join(curated_dir, "agg_daily_trip_metrics.parquet"), index=False)
    payment_metrics.to_parquet(os.path.join(curated_dir, "agg_payment_type_metrics.parquet"), index=False)
    zone_pair_metrics.to_parquet(os.path.join(curated_dir, "agg_zone_pair_metrics.parquet"), index=False)

    print("STEP 8: Attempting PostgreSQL load")
    try:
        from sqlalchemy import create_engine

        engine = create_engine(
            "postgresql+pg8000://admin:admin@127.0.0.1:5432/taxi_dw"
        )

        clean_df.to_sql("fact_taxi_trips", engine, if_exists="replace", index=False)
        daily_metrics.to_sql("agg_daily_trip_metrics", engine, if_exists="replace", index=False)
        payment_metrics.to_sql("agg_payment_type_metrics", engine, if_exists="replace", index=False)
        zone_pair_metrics.to_sql("agg_zone_pair_metrics", engine, if_exists="replace", index=False)

        print("STEP 9: Curated layer and PostgreSQL load completed successfully")

    except Exception as e:
        print("STEP 9: PostgreSQL load skipped due to local environment connection/auth issue")
        print(f"DETAIL: {e}")
        print("Curated parquet outputs were created successfully.")


if __name__ == "__main__":
    main()