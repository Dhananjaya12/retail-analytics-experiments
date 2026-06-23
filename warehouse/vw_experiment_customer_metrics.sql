-- Customer-level metrics for Module 4 experimentation.
-- The final 365 observed days form the experiment period; all earlier orders
-- form the pre-period used as the CUPED covariate.
CREATE OR REPLACE VIEW vw_experiment_customer_metrics AS
WITH dates AS (
    SELECT
        MAX(order_date) AS max_date,
        DATEADD('day', -365, MAX(order_date)) AS experiment_start
    FROM fact_orders
),
customer_metrics AS (
    SELECT
        f.customer_id,
        c.customer_segment,
        AVG(IFF(f.order_date < d.experiment_start, f.sales, NULL))
            AS pre_experiment_aov,
        AVG(IFF(f.order_date >= d.experiment_start, f.sales, NULL))
            AS experiment_aov,
        COUNT(DISTINCT IFF(
            f.order_date >= d.experiment_start, f.order_id, NULL
        )) AS experiment_order_count
    FROM fact_orders f
    JOIN dim_customer c ON f.customer_id = c.customer_id
    CROSS JOIN dates d
    GROUP BY f.customer_id, c.customer_segment
)
SELECT
    customer_id,
    customer_segment,
    pre_experiment_aov,
    experiment_aov,
    experiment_order_count,
    IFF(experiment_order_count >= 2, 1, 0) AS repeat_purchase
FROM customer_metrics
WHERE pre_experiment_aov IS NOT NULL
  AND experiment_aov IS NOT NULL;
