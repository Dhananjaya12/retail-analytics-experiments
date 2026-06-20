-- Customer-level order aggregates. Base for RFM segmentation (Section 6.1)
-- and churn flagging (Section 6.3) in the product analytics module.
CREATE OR REPLACE VIEW vw_customer_summary AS
SELECT
    c.customer_id,
    c.customer_segment,
    c.customer_city,
    c.customer_state,
    c.customer_country,
    c.first_order_date,
    MAX(f.order_date)                   AS last_order_date,
    COUNT(DISTINCT f.order_id)          AS order_count,
    SUM(f.sales)                        AS total_sales,
    SUM(f.profit)                       AS total_profit,
    SUM(f.sales) / COUNT(DISTINCT f.order_id) AS avg_order_value
FROM fact_orders f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_segment, c.customer_city, c.customer_state,
         c.customer_country, c.first_order_date;
