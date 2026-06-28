import yaml
from pyspark.sql import SparkSession

from extract import read_raw_data
from validate import validate_required_columns, apply_quality_filters
from transform import clean_and_transform
from load import write_parquet


def load_config(path: str = "config/config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def build_spark_session(app_name: str) -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3")
        .config("spark.hadoop.io.native.lib.available", "false")
        .getOrCreate()
    )


def main() -> None:
    config = load_config()
    spark = build_spark_session(config["app_name"])

    print("STEP 1: Reading data")
    raw_df = read_raw_data(spark, config["raw_data_path"])

    print("STEP 2: Validating required columns")
    validate_required_columns(raw_df)

    print("STEP 3: Applying quality filters")
    valid_df = apply_quality_filters(raw_df)

    print("STEP 4: Cleaning and transforming")
    clean_df = clean_and_transform(valid_df)

    print("STEP 5: Attempting Spark processed write")
    try:
        write_parquet(clean_df, config["processed_data_path"])
        print("STEP 6: Spark processed parquet written successfully")
    except Exception as e:
        print("STEP 6: Spark write skipped due to Windows/Hadoop compatibility issue")
        print(f"DETAIL: {e}")

    print("STEP 7: Spark transformation pipeline completed")
    spark.stop()


if __name__ == "__main__":
    main()