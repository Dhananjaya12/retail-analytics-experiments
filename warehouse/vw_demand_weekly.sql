-- Weekly demand trends by product, category, and region.
CREATE OR REPLACE VIEW vw_demand_weekly AS
WITH weekly_demand AS (
    SELECT
        DATE_TRUNC('week', f.order_date) AS demand_week,
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
        DATE_TRUNC('week', f.order_date),
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
            ORDER BY demand_week
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS units_4_week_rolling_avg,
        LAG(units_sold) OVER (
            PARTITION BY product_id, order_region
            ORDER BY demand_week
        ) AS previous_week_units
    FROM weekly_demand
)
SELECT
    demand_week,
    product_id,
    product_name,
    category_name,
    order_region,
    units_sold,
    total_sales,
    order_count,
    units_4_week_rolling_avg,
    100.0 * (units_sold - previous_week_units)
        / NULLIF(previous_week_units, 0) AS week_over_week_pct
FROM with_trends;
