"""Clean and standardize the raw DataCo CSV (PROJECT_PLAN.md Section 5.1).

Run `python etl/profile_raw.py` first and confirm the column names below
match the actual downloaded file (Kaggle mirrors vary slightly in casing
and naming) before trusting this output.

Usage:
    python etl/clean.py [path/to/raw.csv]

Writes cleaned output to data/processed/orders_clean.parquet.
"""
import sys
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

RAW_GLOB = "data/raw/*.csv"
OUTPUT_PATH = "data/processed/orders_clean.parquet"

# Null-handling decisions per column (Section 5.1). Document the "why" here
# since this is the part that doesn't show up in the code itself.
#
# - Order Zipcode: ~85% null in the source file (small/incomplete addresses)
#   -> dropped instead of imputed, not used by any downstream module.
# - Product Description: always null in the source file -> dropped.
# - Customer Lname / Customer Email / Customer Password: PII with no
#   analytical value for this project -> dropped at load time.
DROP_COLUMNS = [
    "Customer Email",
    "Customer Password",
    "Customer Fname",
    "Customer Lname",
    "Customer Street",
    "Product Description",
    "Product Image",
    "Order Zipcode",
]


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
    print(f"Reading: {raw_path}")

    spark = (
        SparkSession.builder.appName("dataco-clean")
        .master("local[*]")
        .getOrCreate()
    )

    df = spark.read.csv(raw_path, header=True, inferSchema=True, encoding="ISO-8859-1")
    raw_count = df.count()
    print(f"Raw row count: {raw_count}")

    existing_drop_cols = [c for c in DROP_COLUMNS if c in df.columns]
    df = df.drop(*existing_drop_cols)

    # Dedupe: an (Order Id, Order Item Id) pair should be unique. Flag rather
    # than silently drop, so downstream validation can confirm the impact.
    dedup_window = Window.partitionBy("Order Id", "Order Item Id")
    df = df.withColumn("_dup_rank", F.row_number().over(dedup_window.orderBy(F.lit(1))))
    dup_count = df.filter(F.col("_dup_rank") > 1).count()
    if dup_count:
        print(f"Dropping {dup_count} duplicate (Order Id, Order Item Id) rows")
    df = df.filter(F.col("_dup_rank") == 1).drop("_dup_rank")

    # Dates: order date / shipping date arrive as strings -> proper date type.
    for date_col in ["order date (DateOrders)", "shipping date (DateOrders)"]:
        if date_col in df.columns:
            new_col = date_col.split(" ")[0] + "_date"  # e.g. order_date
            df = df.withColumn(new_col, F.to_date(F.col(date_col), "M/d/yyyy H:mm"))

    # Currency/financial fields -> fixed decimal.
    for money_col in [
        "Sales",
        "Order Profit Per Order",
        "Order Item Discount",
        "Order Item Discount Rate",
        "Benefit per order",
        "Sales per customer",
        "Order Item Product Price",
        "Order Item Total",
        "Order Item Profit Ratio",
    ]:
        if money_col in df.columns:
            df = df.withColumn(money_col, F.col(money_col).cast("decimal(10,2)"))

    # Standardize categorical text: trim whitespace, consistent casing for
    # geography fields (these are joined/grouped on most often downstream).
    text_cols_title_case = ["Customer City", "Customer State", "Customer Country",
                             "Order City", "Order State", "Order Country",
                             "Order Region", "Market", "Category Name",
                             "Department Name"]
    for c in text_cols_title_case:
        if c in df.columns:
            df = df.withColumn(c, F.initcap(F.trim(F.col(c))))

    # Late_delivery_risk arrives as 0/1 int -> boolean.
    if "Late_delivery_risk" in df.columns:
        df = df.withColumn("Late_delivery_risk", F.col("Late_delivery_risk").cast("boolean"))

    # first_order_date per customer, needed for cohort analysis (Section 6.2).
    if "Customer Id" in df.columns and "order_date" in df.columns:
        cust_window = Window.partitionBy("Customer Id")
        df = df.withColumn("first_order_date", F.min("order_date").over(cust_window))

    clean_count = df.count()
    print(f"Cleaned row count: {clean_count} (dropped {raw_count - clean_count})")

    Path("data/processed").mkdir(parents=True, exist_ok=True)
    df.write.mode("overwrite").parquet(OUTPUT_PATH)
    print(f"Wrote cleaned data to {OUTPUT_PATH}")

    spark.stop()


if __name__ == "__main__":
    main()
