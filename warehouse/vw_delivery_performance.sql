-- Delivery performance aggregated by region, shipping mode, and category.
-- Base for the late-delivery / lead-time analysis in the supply chain
-- module (Section 7.2-7.3) — this view holds the raw counts/averages,
-- the module-specific views derive rates from these.
CREATE OR REPLACE VIEW vw_delivery_performance AS
SELECT
    r.order_region,
    f.shipping_mode,
    p.category_name,
    COUNT(*)                                            AS order_item_count,
    SUM(CASE WHEN f.late_delivery_risk THEN 1 ELSE 0 END) AS late_count,
    AVG(f.days_for_shipping_real)                        AS avg_days_shipping_real,
    AVG(f.days_for_shipment_scheduled)                    AS avg_days_shipment_scheduled
FROM fact_orders f
JOIN dim_region r ON f.region_id = r.region_id
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY r.order_region, f.shipping_mode, p.category_name;
