# Retail Analytics & Experiments

Retail data engineering + analytics + experimentation platform built on PySpark, SQL, and Snowflake.

Full plan, schema, and build order: see [`PROJECT_PLAN.md`](./PROJECT_PLAN.md).

## Modules

- **Data Foundation** — PySpark ETL → Snowflake star schema
- **Product Analytics** — RFM segmentation, cohort/retention, churn
- **Supply Chain Analytics** — demand, late delivery, lead time
- **Experimentation** — A/B testing + CUPED variance reduction

## Setup

```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env       # then fill in your Snowflake credentials
```

## Status

See the build-order checklist in [`PROJECT_PLAN.md`](./PROJECT_PLAN.md) (Section 13).
