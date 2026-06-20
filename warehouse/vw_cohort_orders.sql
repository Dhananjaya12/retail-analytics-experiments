-- One row per (customer, month) they placed an order, with cohort month
-- (month of first order) and period_number (months since cohort start).
-- Base for cohort/retention analysis (PROJECT_PLAN.md Section 6.2).
CREATE OR REPLACE VIEW vw_cohort_orders AS
SELECT DISTINCT
    f.customer_id,
    DATE_TRUNC('month', c.first_order_date) AS cohort_month,
    DATE_TRUNC('month', f.order_date)        AS order_month,
    DATEDIFF(
        'month',
        DATE_TRUNC('month', c.first_order_date),
        DATE_TRUNC('month', f.order_date)
    ) AS period_number
FROM fact_orders f
JOIN dim_customer c ON f.customer_id = c.customer_id;
