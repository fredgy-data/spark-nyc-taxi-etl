# Load logic
import os
from pyspark.sql import DataFrame

def write_parquet(df: DataFrame, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.write.mode("overwrite").parquet(output_path)

def write_to_postgres(df: DataFrame, table_name: str, jdbc_url: str, properties: dict) -> None:
    (
        df.write
        .mode("overwrite")
        .jdbc(url=jdbc_url, table=table_name, properties=properties)
    )