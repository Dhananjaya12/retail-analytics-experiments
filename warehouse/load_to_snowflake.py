"""Load the star schema parquet files into Snowflake (Section 5.4).

Requires SNOWFLAKE_* env vars in .env (see .env.example) and a running
trial. Creates tables from warehouse/schema.sql if they don't exist, then
loads each table via write_pandas (pandas -> internal stage -> COPY INTO).

Usage:
    python warehouse/load_to_snowflake.py
"""
import os
from pathlib import Path

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas

STAR_SCHEMA_DIR = Path("data/processed/star_schema")
SCHEMA_DDL_PATH = Path("warehouse/schema.sql")

TABLES = ["dim_customer", "dim_product", "dim_date", "dim_region", "fact_orders"]


def get_connection() -> snowflake.connector.SnowflakeConnection:
    load_dotenv()
    required = [
        "SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_WAREHOUSE", "SNOWFLAKE_DATABASE", "SNOWFLAKE_SCHEMA",
    ]
    missing = [v for v in required if not os.environ.get(v)]
    if missing:
        raise RuntimeError(f"Missing required env vars: {missing}. Check your .env file.")

    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
        role=os.environ.get("SNOWFLAKE_ROLE"),
    )


def create_tables(conn: snowflake.connector.SnowflakeConnection) -> None:
    ddl = SCHEMA_DDL_PATH.read_text()
    cur = conn.cursor()
    for statement in ddl.split(";"):
        statement = statement.strip()
        if statement:
            cur.execute(statement)
    cur.close()


def load_table(conn: snowflake.connector.SnowflakeConnection, table_name: str) -> None:
    parquet_path = STAR_SCHEMA_DIR / f"{table_name}.parquet"
    pdf = pd.read_parquet(parquet_path)
    pdf.columns = [c.upper() for c in pdf.columns]

    success, n_chunks, n_rows, _ = write_pandas(
        conn, pdf, table_name.upper(), auto_create_table=False
    )
    print(f"{table_name}: loaded {n_rows} rows (success={success})")


def main() -> None:
    conn = get_connection()
    try:
        print("Creating tables from warehouse/schema.sql ...")
        create_tables(conn)

        for table_name in TABLES:
            load_table(conn, table_name)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
