# Extract logic
from pyspark.sql import SparkSession, DataFrame

def read_raw_data(spark: SparkSession, file_path: str) -> DataFrame:
    return spark.read.parquet(file_path)