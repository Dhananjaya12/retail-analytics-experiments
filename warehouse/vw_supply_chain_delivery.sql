-- Late-delivery, on-time fulfillment, and lead-time proxy metrics.
-- late_risk_index > 1 means the group is riskier than the dataset overall.
CREATE OR REPLACE VIEW vw_supply_chain_delivery AS
WITH overall AS (
    SELECT
        AVG(IFF(late_delivery_risk, 1.0, 0.0)) AS overall_late_rate
    FROM fact_orders
),
grouped AS (
    SELECT
        r.order_region,
        f.shipping_mode,
        p.category_name,
        COUNT(*) AS order_item_count,
        SUM(IFF(f.late_delivery_risk, 1, 0)) AS late_count,
        AVG(IFF(f.late_delivery_risk, 1.0, 0.0)) AS late_delivery_rate,
        AVG(f.days_for_shipping_real) AS avg_actual_lead_days,
        AVG(f.days_for_shipment_scheduled) AS avg_scheduled_lead_days,
        AVG(
            f.days_for_shipping_real - f.days_for_shipment_scheduled
        ) AS avg_lead_time_variance_days,
        STDDEV(
            f.days_for_shipping_real - f.days_for_shipment_scheduled
        ) AS stddev_lead_time_variance_days
    FROM fact_orders f
    JOIN dim_region r ON f.region_id = r.region_id
    JOIN dim_product p ON f.product_id = p.product_id
    GROUP BY r.order_region, f.shipping_mode, p.category_name
)
SELECT
    g.*,
    1.0 - g.late_delivery_rate AS on_time_fulfillment_rate,
    g.late_delivery_rate / NULLIF(o.overall_late_rate, 0) AS late_risk_index,
    100.0 * g.late_count / SUM(g.late_count) OVER () AS share_of_all_late_items_pct,
    100.0 * g.order_item_count / SUM(g.order_item_count) OVER () AS share_of_all_items_pct
FROM grouped g
CROSS JOIN overall o;
