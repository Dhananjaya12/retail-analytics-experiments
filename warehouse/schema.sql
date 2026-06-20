-- Star schema for DataCo Smart Supply Chain dataset.
-- Source: data/processed/orders_clean.parquet (180,519 rows, validated via
-- etl/validate_clean.py — no dupes, no null PKs, no null first_order_date).
--
-- Surrogate keys: dim_customer/dim_product/dim_date reuse the dataset's own
-- natural keys (Customer Id, Product Card Id, the date itself) as PK, since
-- those are already unique and stable. dim_region has no natural single-
-- column key (it's the combination of region/country/market), so it gets a
-- generated surrogate key populated at load time.

CREATE TABLE dim_customer (
    customer_id         INT PRIMARY KEY,
    customer_segment    VARCHAR,
    customer_city        VARCHAR,
    customer_state       VARCHAR,
    customer_country     VARCHAR,
    first_order_date     DATE
);

CREATE TABLE dim_product (
    product_id           INT PRIMARY KEY,
    product_name          VARCHAR,
    product_price         NUMBER(10,2),
    category_id           INT,
    category_name         VARCHAR,
    department_id         INT,
    department_name       VARCHAR
);

CREATE TABLE dim_date (
    date_id               DATE PRIMARY KEY,
    year                  INT,
    month                 INT,
    day                   INT,
    week                  INT,
    day_of_week            VARCHAR
);

CREATE TABLE dim_region (
    region_id             INT PRIMARY KEY,
    order_region           VARCHAR,
    order_country           VARCHAR,
    market                  VARCHAR
);

CREATE TABLE fact_orders (
    order_id                       INT,
    order_item_id                  INT,
    customer_id                    INT REFERENCES dim_customer(customer_id),
    product_id                     INT REFERENCES dim_product(product_id),
    order_date                     DATE REFERENCES dim_date(date_id),
    region_id                      INT REFERENCES dim_region(region_id),
    sales                          NUMBER(10,2),
    profit                         NUMBER(10,2),
    discount                       NUMBER(10,2),
    discount_rate                  NUMBER(5,2),
    quantity                       INT,
    shipping_mode                  VARCHAR,
    delivery_status                VARCHAR,
    order_status                   VARCHAR,
    days_for_shipping_real          INT,
    days_for_shipment_scheduled     INT,
    late_delivery_risk              BOOLEAN,
    PRIMARY KEY (order_id, order_item_id)
);
