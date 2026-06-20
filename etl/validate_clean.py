"""Sanity-check data/processed/orders_clean.parquet before designing the
Snowflake star schema (Section 5.5 validation checklist, run locally first).

Usage:
    python etl/validate_clean.py
"""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

INPUT_PATH = "data/processed/orders_clean.parquet"


def main() -> None:
    spark = (
        SparkSession.builder.appName("dataco-validate")
        .master("local[*]")
        .getOrCreate()
    )

    df = spark.read.parquet(INPUT_PATH)

    print(f"Row count: {df.count()}")

    dup_count = (
        df.groupBy("Order Id", "Order Item Id")
        .count()
        .filter(F.col("count") > 1)
        .count()
    )
    print(f"Duplicate (Order Id, Order Item Id) pairs: {dup_count}")

    pk_nulls = df.filter(
        F.col("Order Id").isNull() | F.col("Order Item Id").isNull()
    ).count()
    print(f"Rows with null primary key parts: {pk_nulls}")

    date_range = df.select(
        F.min("order_date").alias("min_order_date"),
        F.max("order_date").alias("max_order_date"),
    ).collect()[0]
    print(f"order_date range: {date_range['min_order_date']} to {date_range['max_order_date']}")

    totals = df.select(
        F.sum("Sales").alias("total_sales"),
        F.sum("Order Profit Per Order").alias("total_profit"),
    ).collect()[0]
    print(f"Total Sales: {totals['total_sales']}")
    print(f"Total Profit: {totals['total_profit']}")

    print(f"Distinct customers: {df.select('Customer Id').distinct().count()}")
    print(f"Distinct products: {df.select('Product Card Id').distinct().count()}")

    null_first_order_date = df.filter(F.col("first_order_date").isNull()).count()
    print(f"Rows with null first_order_date: {null_first_order_date}")

    spark.stop()


if __name__ == "__main__":
    main()
