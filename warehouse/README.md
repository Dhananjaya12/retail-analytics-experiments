# Warehouse

Snowflake DDL and SQL views (schema.sql, product_views.sql, supply_chain_views.sql).

## Snowflake trial setup (one-time)

Run in a Snowflake worksheet (Projects → Worksheets → new SQL worksheet → run all):

```sql
CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH WITH WAREHOUSE_SIZE='XSMALL' AUTO_SUSPEND=60 AUTO_RESUME=TRUE;
CREATE DATABASE IF NOT EXISTS RETAIL_ANALYTICS;
```

(`COMPUTE_WH` already exists by default on a trial account — reused it instead
of creating a separate warehouse.)

Get your account identifier from the browser URL while logged in:
`https://app.snowflake.com/<orgname>/<account_name>/...` → account identifier
is `<orgname>-<account_name>`.

`.env` values (copy from `.env.example`):

```
SNOWFLAKE_ACCOUNT=<orgname>-<account_name>
SNOWFLAKE_USER=<snowflake login username>
SNOWFLAKE_PASSWORD=<snowflake login password>
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=RETAIL_ANALYTICS
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

## Load process

```bash
python etl/profile_raw.py          # verify raw CSV column names
python etl/clean.py                # -> data/processed/orders_clean.parquet
python etl/validate_clean.py       # sanity checks before schema design
python etl/build_star_schema.py    # -> data/processed/star_schema/*.parquet
python warehouse/load_to_snowflake.py   # creates tables + loads via write_pandas
```
