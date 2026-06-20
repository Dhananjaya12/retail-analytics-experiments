"""Build the star schema tables (warehouse/schema.sql) from the cleaned
orders dataset, ready for Snowflake load.

Usage:
    python etl/build_star_schema.py

Reads data/processed/orders_clean.parquet, writes one parquet file per
target table under data/processed/star_schema/, with columns already
renamed/typed to match warehouse/schema.sql exactly.
"""
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

INPUT_PATH = "data/processed/orders_clean.parquet"
OUTPUT_DIR = "data/processed/star_schema"


def main() -> None:
    spark = (
        SparkSession.builder.appName("dataco-build-star-schema")
        .master("local[*]")
        .getOrCreate()
    )

    df = spark.read.parquet(INPUT_PATH)
    out_dir = Path(OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    # dim_customer
    dim_customer = (
        df.select(
            F.col("Customer Id").alias("customer_id"),
            F.col("Customer Segment").alias("customer_segment"),
            F.col("Customer City").alias("customer_city"),
            F.col("Customer State").alias("customer_state"),
            F.col("Customer Country").alias("customer_country"),
            F.col("first_order_date"),
        )
        .dropDuplicates(["customer_id"])
    )
    dim_customer.write.mode("overwrite").parquet(f"{OUTPUT_DIR}/dim_customer.parquet")
    print(f"dim_customer: {dim_customer.count()} rows")

    # dim_product
    dim_product = (
        df.select(
            F.col("Product Card Id").alias("product_id"),
            F.col("Product Name").alias("product_name"),
            F.col("Product Price").cast("decimal(10,2)").alias("product_price"),
            F.col("Category Id").alias("category_id"),
            F.col("Category Name").alias("category_name"),
            F.col("Department Id").alias("department_id"),
            F.col("Department Name").alias("department_name"),
        )
        .dropDuplicates(["product_id"])
    )
    dim_product.write.mode("overwrite").parquet(f"{OUTPUT_DIR}/dim_product.parquet")
    print(f"dim_product: {dim_product.count()} rows")

    # dim_date
    dim_date = (
        df.select(F.col("order_date").alias("date_id"))
        .dropDuplicates(["date_id"])
        .withColumn("year", F.year("date_id"))
        .withColumn("month", F.month("date_id"))
        .withColumn("day", F.dayofmonth("date_id"))
        .withColumn("week", F.weekofyear("date_id"))
        .withColumn("day_of_week", F.date_format("date_id", "EEEE"))
    )
    dim_date.write.mode("overwrite").parquet(f"{OUTPUT_DIR}/dim_date.parquet")
    print(f"dim_date: {dim_date.count()} rows")

    # dim_region — no natural single-column key, so generate a surrogate.
    dim_region = (
        df.select(
            F.col("Order Region").alias("order_region"),
            F.col("Order Country").alias("order_country"),
            F.col("Market").alias("market"),
        )
        .dropDuplicates(["order_region", "order_country", "market"])
        .withColumn("region_id", F.monotonically_increasing_id().cast("int"))
        .select("region_id", "order_region", "order_country", "market")
    )
    dim_region.write.mode("overwrite").parquet(f"{OUTPUT_DIR}/dim_region.parquet")
    print(f"dim_region: {dim_region.count()} rows")

    # fact_orders — join back to dim_region to pick up the surrogate key.
    fact_orders = (
        df.join(
            dim_region,
            (df["Order Region"] == dim_region["order_region"])
            & (df["Order Country"] == dim_region["order_country"])
            & (df["Market"] == dim_region["market"]),
            "left",
        )
        .select(
            F.col("Order Id").alias("order_id"),
            F.col("Order Item Id").alias("order_item_id"),
            F.col("Customer Id").alias("customer_id"),
            F.col("Product Card Id").alias("product_id"),
            F.col("order_date"),
            F.col("region_id"),
            F.col("Sales").cast("decimal(10,2)").alias("sales"),
            F.col("Order Profit Per Order").cast("decimal(10,2)").alias("profit"),
            F.col("Order Item Discount").cast("decimal(10,2)").alias("discount"),
            F.col("Order Item Discount Rate").cast("decimal(5,2)").alias("discount_rate"),
            F.col("Order Item Quantity").alias("quantity"),
            F.col("Shipping Mode").alias("shipping_mode"),
            F.col("Delivery Status").alias("delivery_status"),
            F.col("Order Status").alias("order_status"),
            F.col("Days for shipping (real)").alias("days_for_shipping_real"),
            F.col("Days for shipment (scheduled)").alias("days_for_shipment_scheduled"),
            F.col("Late_delivery_risk").alias("late_delivery_risk"),
        )
    )
    fact_orders.write.mode("overwrite").parquet(f"{OUTPUT_DIR}/fact_orders.parquet")
    print(f"fact_orders: {fact_orders.count()} rows")

    orphan_regions = fact_orders.filter(F.col("region_id").isNull()).count()
    if orphan_regions:
        print(f"WARNING: {orphan_regions} fact_orders rows failed to match a region")

    spark.stop()


if __name__ == "__main__":
    main()
