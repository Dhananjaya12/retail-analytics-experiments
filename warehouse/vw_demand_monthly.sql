-- Monthly demand trends by product, category, and region.
-- Rolling averages smooth short-term noise; MoM change highlights acceleration
-- or decline without introducing a forecasting model.
CREATE OR REPLACE VIEW vw_demand_monthly AS
WITH monthly_demand AS (
    SELECT
        DATE_TRUNC('month', f.order_date) AS demand_month,
        p.product_id,
        p.product_name,
        p.category_name,
        r.order_region,
        SUM(f.quantity) AS units_sold,
        SUM(f.sales) AS total_sales,
        COUNT(DISTINCT f.order_id) AS order_count
    FROM fact_orders f
    JOIN dim_product p ON f.product_id = p.product_id
    JOIN dim_region r ON f.region_id = r.region_id
    GROUP BY
        DATE_TRUNC('month', f.order_date),
        p.product_id,
        p.product_name,
        p.category_name,
        r.order_region
),
with_trends AS (
    SELECT
        *,
        AVG(units_sold) OVER (
            PARTITION BY product_id, order_region
            ORDER BY demand_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS units_3_month_rolling_avg,
        LAG(units_sold) OVER (
            PARTITION BY product_id, order_region
            ORDER BY demand_month
        ) AS previous_month_units
    FROM monthly_demand
)
SELECT
    demand_month,
    product_id,
    product_name,
    category_name,
    order_region,
    units_sold,
    total_sales,
    order_count,
    units_3_month_rolling_avg,
    100.0 * (units_sold - previous_month_units)
        / NULLIF(previous_month_units, 0) AS month_over_month_pct
FROM with_trends;
