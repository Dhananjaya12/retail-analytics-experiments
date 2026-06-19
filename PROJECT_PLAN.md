# Retail Analytics & Experiments — Project Plan

**Status:** Locked scope, ready to build
**Owner:** Dhananjaya
**Last updated:** June 2026

---

## 1. Objective

Build ONE additional portfolio project that broadens the resume beyond AI/LLM engineering, without building another chatbot/RAG app. This project demonstrates data engineering, analytics, and experimentation skills end to end on a real dataset.

**Target roles this project supports:** AI Engineer, Data Scientist, Data Analyst, Product Analyst, Analytics Engineer, Operations Analyst.

**Explicitly out of scope (cut from the original plan):**
- No Power BI / dashboarding layer (for now — can be bolted on later without touching anything below)
- No Decision Science / optimization module (no OR-Tools, no LP, no inventory optimization)
- No new/novel techniques in Product or Supply Chain modules — standard, established patterns only, taken directly from known reference approaches (cited in Section 9)

**Final module set:**
1. Data Foundation (PySpark + SQL + Snowflake)
2. Product Analytics (standard techniques)
3. Supply Chain Analytics (standard techniques)
4. Experimentation (A/B testing + CUPED)

---

## 2. Data Source

**DataCo Smart Supply Chain Dataset** (Kaggle, search "DataCo Smart Supply Chain for Big Data Analysis").

- ~180,000 unique order records
- 30,000+ unique customer profiles
- 10,000+ unique products
- Includes a secondary unstructured clickstream file (tokenized access logs) — usable for funnel-style analysis later if needed

**Key fields (verify exact names/casing against the file you download — Kaggle mirrors vary slightly):**

| Category | Fields |
|---|---|
| Order | `Order Id`, `Order Item Id`, `Order Date`, `Order Status` |
| Customer | `Customer Id`, `Customer Segment`, `Customer City`, `Customer State`, `Customer Country` |
| Product | `Product Name`, `Category Name`, `Department Name` |
| Geography | `Order Region`, `Order Country`, `Market` |
| Financials | `Sales`, `Order Profit Per Order`, `Order Item Discount` (or `Discount Rate`), `Order Item Quantity` |
| Shipping | `Shipping Mode`, `Days for shipping (real)`, `Days for shipment (scheduled)`, `Late_delivery_risk`, `Delivery Status` |

Why this dataset: it's one real source that natively supports finance, product, and supply-chain–style analysis without needing to stitch together multiple synthetic datasets.

---

## 3. Architecture

```
Raw CSV (Kaggle)
   │
   ▼
PySpark: clean, dedupe, fix dtypes, standardize dates/currency/regions
   │
   ▼
Star schema design (fact_orders + dim_customer/product/date/region)
   │
   ▼
Snowflake: COPY INTO load, SQL views per module
   │
   ├──► Product Analytics notebook (Python + SQL)
   ├──► Supply Chain Analytics notebook (Python + SQL)
   └──► Experimentation engine (Python: pandas/scipy/statsmodels)
```

No BI tool in this version. Outputs are SQL views + Python notebooks with plots (matplotlib/seaborn is enough — no new viz tooling needed for this scope).

---

## 4. Tech Stack

| Layer | Tool |
|---|---|
| ETL | PySpark (local mode is fine at this data size) |
| Warehouse | Snowflake (30-day trial, $400 credit, no card required) |
| Query layer | SQL (Snowflake) + Python (snowflake-connector-python or Snowpark) |
| Analysis | pandas, scipy, statsmodels |
| Stats / Experimentation | scipy.stats, statsmodels (power analysis, CUPED) |
| Version control | Git / GitHub |

---

## 5. Module 1 — Data Foundation (PySpark + SQL + Snowflake)

### 5.1 Cleaning tasks (PySpark, local)
- Drop/flag duplicate `Order Id` + `Order Item Id` combinations
- Fix dtypes: dates → proper date type, currency/sales fields → decimal
- Standardize categorical text (region/country casing, trim whitespace)
- Handle nulls: decide drop vs. impute per column (document the decision per field)
- Derive `first_order_date` per customer (needed later for cohort analysis)

### 5.2 Star schema design

```
fact_orders
  ├── customer_id  → dim_customer
  ├── product_id   → dim_product
  ├── order_date   → dim_date
  └── region_id    → dim_region
```

### 5.3 DDL (Snowflake) — starting sketch, adjust types once you've profiled the real file

```sql
CREATE TABLE dim_customer (
    customer_id        INT PRIMARY KEY,
    customer_segment   VARCHAR,
    customer_city       VARCHAR,
    customer_state      VARCHAR,
    customer_country    VARCHAR,
    first_order_date    DATE
);

CREATE TABLE dim_product (
    product_id          INT PRIMARY KEY,
    product_name         VARCHAR,
    category_name        VARCHAR,
    department_name      VARCHAR
);

CREATE TABLE dim_date (
    date_id              DATE PRIMARY KEY,
    year                 INT,
    month                INT,
    day                  INT,
    week                 INT,
    day_of_week           VARCHAR
);

CREATE TABLE dim_region (
    region_id            INT PRIMARY KEY,
    order_region          VARCHAR,
    order_country          VARCHAR,
    market                VARCHAR
);

CREATE TABLE fact_orders (
    order_id                       INT,
    order_item_id                  INT,
    customer_id                    INT REFERENCES dim_customer(customer_id),
    product_id                     INT REFERENCES dim_product(product_id),
    order_date                     DATE REFERENCES dim_date(date_id),
    region_id                      INT REFERENCES dim_region(region_id),
    sales                          NUMBER(10,2),
    profit                         NUMBER(10,2),
    discount                       NUMBER(5,2),
    quantity                       INT,
    shipping_mode                  VARCHAR,
    days_for_shipping_real         INT,
    days_for_shipment_scheduled    INT,
    late_delivery_risk             BOOLEAN,
    order_status                   VARCHAR,
    PRIMARY KEY (order_id, order_item_id)
);
```

### 5.4 Load process
1. Export cleaned PySpark output to Parquet/CSV
2. Stage file in Snowflake internal stage (`PUT` command)
3. `COPY INTO` each table
4. Run row-count and null-check validation queries

### 5.5 Validation checklist
- [ ] Row count in Snowflake matches cleaned source row count
- [ ] No orphaned foreign keys (every `fact_orders.customer_id` exists in `dim_customer`, etc.)
- [ ] Aggregate `SUM(sales)` and `SUM(profit)` from Snowflake match the cleaned source file
- [ ] No unexpected NULLs in primary key columns

---

## 6. Module 2 — Product Analytics (standard techniques)

### 6.1 RFM Segmentation
- **Recency** = days since customer's most recent order (relative to dataset max date)
- **Frequency** = count of distinct orders per customer
- **Monetary** = sum of sales per customer
- Score each dimension into quintiles (1–5), combine into an RFM segment label (e.g., Champions, At Risk, Lost, Loyal)
- Implementation: SQL window functions (`NTILE(5)`) + a Python notebook for segment profiling/visualization

### 6.2 Cohort & Retention Analysis
- Define cohort = month of customer's `first_order_date`
- For each cohort, track % of customers placing another order in month+1, month+2, etc.
- Output: cohort retention matrix/heatmap (standard SaaS-style cohort table, applied to retail)

### 6.3 Churn Flag
- Define churn = no order in the last N days (e.g. 90) relative to dataset max date — binary flag
- Optional: simple logistic regression using RFM features + segment + region to explain churn drivers (explanatory, not a production model — the point is demonstrating the analytics pattern)

**Reference pattern:** combines churn classification + clustering/segmentation in one module, following the same structure used in standard churn-segmentation portfolio projects (e.g., churn classifier + K-means segmentation paired together).

---

## 7. Module 3 — Supply Chain Analytics (standard techniques)

### 7.1 Demand Analysis
- Units sold by product/category/region, monthly and weekly
- Rolling averages, month-over-month % change
- No forecasting model required unless you want the keyword — simple trend analysis is sufficient for this scope

### 7.2 Late Delivery Analysis
- Late delivery rate = `COUNT(late_delivery_risk = 1) / COUNT(*)`, grouped by region, shipping mode, category
- Identify which shipping modes/regions disproportionately drive late risk

### 7.3 Fill Rate / Lead Time (proxy metrics)
- Since this dataset has no live inventory/stock levels, fill rate is approximated as **on-time fulfillment rate** = `1 - late delivery rate`
- Lead time = `AVG(days_for_shipping_real)` vs. `AVG(days_for_shipment_scheduled)`, plus variance between the two (a measure of forecast/promise accuracy)

**Reference pattern:** descriptive supply-chain analytics (demand, delivery performance, lead time) — deliberately excludes prescriptive/optimization techniques per scope decision.

---

## 8. Module 4 — Experimentation (A/B Testing + CUPED)

This is the most technically distinct module — keep it rigorous and well-documented since it's the differentiator.

### 8.1 Treatment/Control Design
Two viable approaches — recommend doing **both**, since (A) proves your engine works correctly and (B) shows real-world judgment:

- **(A) Synthetic, ground-truth-known split (primary):** Randomly assign existing customers/orders 50/50 into Group A / Group B. Inject a known synthetic effect into Group B (e.g., simulate a +5% uplift in order value for a "new discount strategy"). This lets you verify your testing engine correctly detects a known, planted effect — the standard way to validate an experimentation pipeline without live randomized data.
- **(B) Quasi-experimental, real data (secondary):** Compare existing real segments (e.g., `Customer Segment` = Corporate vs. Consumer) on a metric of interest. Be explicit in your write-up that this is observational, not causal — correlation only, no random assignment.

### 8.2 Core Statistical Test
- Binary/conversion-style metric (e.g., repeat-purchase yes/no) → two-proportion z-test or chi-square test of independence
- Continuous metric (e.g., order value) → Welch's t-test (does not assume equal variances)
- Report: effect size, p-value, 95% confidence interval

### 8.3 CUPED Variance Reduction
CUPED (Controlled-experiment Using Pre-Experiment Data) reduces variance using a pre-period covariate correlated with the outcome:

```
Y_cuped = Y - θ × (X - X̄)
θ = Cov(Y, X) / Var(X)
```

Where `X` = customer's historical average order value *before* the experiment window, `Y` = the metric during the experiment window. Report variance before vs. after CUPED adjustment to show why it matters — this is the "additional relevant technique" paired with the core A/B test.

### 8.4 Sample Size / Power
- Use `statsmodels.stats.power` to calculate required sample size for a given effect size, alpha = 0.05, power = 0.8
- Compare required N to the actual customer count available in the dataset — discuss whether the dataset has enough power to detect the effect size you're testing for

**Reference pattern:** combines a standard two-sample hypothesis test with CUPED variance reduction, following the same structure used in advanced A/B-testing toolkits (CUPED + significance testing paired together).

---

## 9. Repo Structure

```
retail-analytics-experiments/
├── data/                    # download script + raw/processed (gitignored)
├── etl/                     # pyspark transforms
├── warehouse/                # Snowflake DDL + SQL views
│   ├── schema.sql
│   ├── product_views.sql
│   └── supply_chain_views.sql
├── analytics/
│   ├── product/              # RFM, cohort, churn notebooks
│   └── supply_chain/         # demand, delivery, lead time notebooks
├── experimentation/          # A/B test engine + CUPED
│   ├── synthetic_split.py
│   ├── ab_test.py
│   └── cuped.py
├── README.md
└── requirements.txt
```

---

## 10. Build Order

1. **Data ingestion & cleaning** — PySpark job, local
2. **Star schema + Snowflake load** — DDL, COPY INTO, validation
3. **Base SQL views** — sales, profit, delivery, customer aggregates
4. **Product analytics notebook** — RFM, cohort, churn
5. **Supply chain analytics notebook** — demand, late delivery, lead time
6. **Experimentation module** — synthetic split, core test, CUPED, power analysis
7. **README + ERD diagram + push to GitHub**

**Rough estimate:** 3–4 weeks at a steady pace. Steps 1–3 (foundation) are highest leverage since every later module depends on them — front-load effort there.

---

## 11. Snowflake Trial Strategy

- Snowflake trial = 30 days, $400 credit, no permanent free tier
- **Do all local cleaning/schema design (Section 5.1–5.3) before starting the trial clock** — don't burn trial days on local work
- Start the trial only when ready to load data and start running SQL
- Push every DDL/SQL/PySpark script to GitHub continuously — this is what persists and what reviewers actually look at, not the live warehouse
- Once the trial nears expiry, take screenshots/recordings of any live queries you want to reference later (e.g., for interview walkthroughs)

---

## 12. Job-Target Mapping

| Module | Strengthens resume for |
|---|---|
| Data Foundation (PySpark/SQL/Snowflake) | Analytics Engineer, Data Engineer, Data Analyst |
| Product Analytics | Product Analyst, Data Analyst, Data Scientist |
| Supply Chain Analytics | Operations Analyst, Data Analyst |
| Experimentation (A/B + CUPED) | Data Scientist, Product Analyst |

Honest note: with the Decision Science module removed, this project no longer directly targets "Decision Scientist" roles — the Experimentation module is now your strongest differentiator instead.

---

## 13. Next Steps

- [ ] Download dataset, profile actual column names/types
- [ ] Write PySpark cleaning script
- [ ] Finalize and run star schema DDL
- [ ] Start Snowflake trial, load data
- [ ] Build Module 2 → 3 → 4 in order
