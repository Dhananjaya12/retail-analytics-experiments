-- Sales/profit aggregated by region/country/market.
CREATE OR REPLACE VIEW vw_sales_by_region AS
SELECT
    r.region_id,
    r.order_region,
    r.order_country,
    r.market,
    COUNT(DISTINCT f.order_id)         AS order_count,
    SUM(f.quantity)                     AS units_sold,
    SUM(f.sales)                        AS total_sales,
    SUM(f.profit)                       AS total_profit
FROM fact_orders f
JOIN dim_region r ON f.region_id = r.region_id
GROUP BY r.region_id, r.order_region, r.order_country, r.market;
