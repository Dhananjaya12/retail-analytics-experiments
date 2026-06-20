-- Sales/profit/quantity aggregated by product and category/department.
CREATE OR REPLACE VIEW vw_sales_by_product AS
SELECT
    p.product_id,
    p.product_name,
    p.category_name,
    p.department_name,
    COUNT(DISTINCT f.order_id)         AS order_count,
    SUM(f.quantity)                     AS units_sold,
    SUM(f.sales)                        AS total_sales,
    SUM(f.profit)                       AS total_profit
FROM fact_orders f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category_name, p.department_name;
