-- RFM (Recency/Frequency/Monetary) scoring for Product Analytics (Section 6.1).
-- Recency/Frequency/Monetary are quintile-scored (1-5, 5=best) via NTILE,
-- then combined into a segment label. Built on top of vw_customer_summary.
CREATE OR REPLACE VIEW vw_rfm_scores AS
WITH dataset_max_date AS (
    SELECT MAX(last_order_date) AS max_date FROM vw_customer_summary
),
rfm_base AS (
    SELECT
        c.customer_id,
        c.customer_segment,
        c.customer_country,
        DATEDIFF('day', c.last_order_date, m.max_date) AS recency_days,
        c.order_count                                   AS frequency,
        c.total_sales                                   AS monetary
    FROM vw_customer_summary c
    CROSS JOIN dataset_max_date m
),
rfm_scored AS (
    SELECT
        *,
        -- Lower recency_days is better, so invert the quintile (6 - ntile).
        6 - NTILE(5) OVER (ORDER BY recency_days)  AS r_score,
        NTILE(5) OVER (ORDER BY frequency)          AS f_score,
        NTILE(5) OVER (ORDER BY monetary)           AS m_score
    FROM rfm_base
)
SELECT
    customer_id,
    customer_segment,
    customer_country,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    (r_score + f_score + m_score) AS rfm_total,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'New / Promising'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 AND m_score <= 2 THEN 'Lost'
        ELSE 'Needs Attention'
    END AS rfm_segment
FROM rfm_scored;
