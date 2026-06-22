# AGENTS.md

## Project

**Retail Analytics & Experiments** â€” retail data engineering + analytics + experimentation platform.
PySpark â†’ Snowflake â†’ Python analysis. Full plan and reasoning: see `PROJECT_PLAN.md` at repo root.

## Scope â€” do not expand without asking first

This project deliberately excludes some things from the original brainstorm. Don't re-add them unless explicitly asked:

- **No Power BI / dashboarding layer** â€” outputs are SQL views + Python notebooks only
- **No optimization / decision-science module** â€” no OR-Tools, no linear programming, no inventory optimization
- **Product Analytics module**: standard/established techniques only (RFM, cohort/retention, churn flag) â€” no novel methods
- **Supply Chain Analytics module**: descriptive demand/delivery/lead-time analysis plus one standard weekly category-demand forecast; no prescriptive optimization
- **Experimentation module**: A/B testing + CUPED â€” this is the one module that should go deep, not broad

## Tech stack

- ETL: PySpark (local mode â€” data size doesn't need a cluster)
- Warehouse: Snowflake (trial account â€” see note below)
- Analysis: pandas, scipy, statsmodels
- No BI tool, no new viz framework

## Repo structure

```
retail-analytics-experiments/
â”œâ”€â”€ data/                    # download script + raw/processed (gitignored)
â”œâ”€â”€ etl/                     # pyspark transforms
â”œâ”€â”€ warehouse/                # Snowflake DDL + SQL views
â”‚   â”œâ”€â”€ schema.sql
â”‚   â”œâ”€â”€ product_views.sql
â”‚   â””â”€â”€ supply_chain_views.sql
â”œâ”€â”€ analytics/
â”‚   â”œâ”€â”€ product/              # RFM, cohort, churn notebooks
â”‚   â””â”€â”€ supply_chain/         # demand, delivery, lead time notebooks
â”œâ”€â”€ experimentation/          # A/B test engine + CUPED
â”œâ”€â”€ PROJECT_PLAN.md
â””â”€â”€ README.md
```

## Data

- Source: DataCo Smart Supply Chain Dataset (Kaggle) â€” 180,519 order-item rows, 20,652 customers, and 118 products in the downloaded dataset
- Star schema: `fact_orders`, `dim_customer`, `dim_product`, `dim_date`, `dim_region`
- Full DDL and field mapping in `PROJECT_PLAN.md` Section 5 â€” check there before re-deriving schema from scratch

## Conventions

- SQL: snake_case, one view per file under `warehouse/`, filename matches view name
- Python: type hints + docstrings on any function doing a non-trivial transform
- Analysis: reusable Python scripts are the source of truth. Narrative Jupyter notebooks may be added to explain the analytical process and reasoning. Charts are generated alongside the analysis files.
- Snowflake credentials: environment variables only, never hardcoded. Use a `.env` file (gitignored) with `.env.example` committed as a template
- Commit granularity: one logical step per commit (e.g., "add fact_orders DDL", not "warehouse stuff")

## Build order (current status â€” update as steps complete)

- [x] Data ingestion & cleaning (PySpark)
- [x] Star schema design + Snowflake load
- [x] Base SQL views (sales, profit, delivery, customer)
- [x] Product analytics (RFM, cohort, churn)
- [x] Supply chain analytics (demand, delivery, lead time)
- [ ] Experimentation module (synthetic split, A/B test, CUPED)
- [ ] README + ERD diagram

When a step is finished, check it off here so future sessions know where things stand.

## Snowflake note

Trial account (30 days, $400 credit, no permanent free tier). Don't burn trial time on local-only work â€” local cleaning/schema design should happen before the Snowflake connection is first used. All SQL/DDL must live in `warehouse/` regardless of whether the live warehouse is still active, since that's what persists.


