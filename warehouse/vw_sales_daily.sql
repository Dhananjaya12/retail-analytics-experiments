-- Daily sales/profit/order volume, base aggregate for trend analysis.
CREATE OR REPLACE VIEW vw_sales_daily AS
SELECT
    d.date_id,
    d.year,
    d.month,
    d.week,
    d.day_of_week,
    COUNT(DISTINCT f.order_id)         AS order_count,
    SUM(f.quantity)                     AS units_sold,
    SUM(f.sales)                        AS total_sales,
    SUM(f.profit)                       AS total_profit,
    SUM(f.discount)                     AS total_discount
FROM fact_orders f
JOIN dim_date d ON f.order_date = d.date_id
GROUP BY d.date_id, d.year, d.month, d.week, d.day_of_week;
