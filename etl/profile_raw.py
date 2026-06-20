"""Profile the raw DataCo CSV before writing the cleaning job.

Run this first, after placing the Kaggle CSV under data/raw/. It prints
column names/dtypes, row count, null counts, and a few sample rows so the
cleaning logic in clean.py can be matched against the real file instead of
guessed column names from the dataset's reference docs.

Usage:
    python etl/profile_raw.py [path/to/raw.csv]
"""
import sys
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

DEFAULT_RAW_GLOB = "data/raw/*.csv"


def find_raw_csv(explicit_path: str | None) -> str:
    if explicit_path:
        return explicit_path
    matches = list(Path("data/raw").glob("*.csv"))
    if not matches:
        raise FileNotFoundError(
            "No CSV found under data/raw/. Download the DataCo dataset from "
            "Kaggle and place it there, or pass an explicit path."
        )
    return str(matches[0])


def main() -> None:
    raw_path = find_raw_csv(sys.argv[1] if len(sys.argv) > 1 else None)
    print(f"Profiling: {raw_path}\n")

    spark = (
        SparkSession.builder.appName("dataco-profile")
        .master("local[*]")
        .getOrCreate()
    )

    df = spark.read.csv(raw_path, header=True, inferSchema=True, encoding="ISO-8859-1")

    row_count = df.count()
    print(f"Row count: {row_count}")
    print(f"Column count: {len(df.columns)}\n")

    print("Schema:")
    df.printSchema()

    print("Null counts per column:")
    null_counts = df.select(
        [F.sum(F.col(c).isNull().cast("int")).alias(c) for c in df.columns]
    ).collect()[0]
    for c in df.columns:
        n = null_counts[c]
        if n:
            print(f"  {c}: {n} nulls ({n / row_count:.1%})")

    print("\nSample rows:")
    df.show(5, truncate=40)

    spark.stop()


if __name__ == "__main__":
    main()
