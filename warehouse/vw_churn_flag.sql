-- Churn flag: no order in the last 90 days relative to the dataset's max
-- order date (PROJECT_PLAN.md Section 6.3). Built on vw_customer_summary.
CREATE OR REPLACE VIEW vw_churn_flag AS
WITH dataset_max_date AS (
    SELECT MAX(last_order_date) AS max_date FROM vw_customer_summary
)
SELECT
    c.customer_id,
    c.customer_segment,
    c.customer_country,
    c.order_count,
    c.total_sales,
    c.total_profit,
    c.avg_order_value,
    DATEDIFF('day', c.last_order_date, m.max_date) AS days_since_last_order,
    DATEDIFF('day', c.last_order_date, m.max_date) > 90 AS is_churned
FROM vw_customer_summary c
CROSS JOIN dataset_max_date m;
