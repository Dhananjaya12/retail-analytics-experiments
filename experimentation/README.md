# Experimentation

Module 4 implements a reproducible A/B-testing workflow with known synthetic effects, continuous and binary hypothesis tests, CUPED variance reduction, sample-size/power analysis, and a clearly labelled observational comparison.

## Run order

1. Create `warehouse/vw_experiment_customer_metrics.sql` in Snowflake.
2. Run `python -m experimentation.synthetic_split` to inspect eligibility and randomization balance.
3. Run `python -m experimentation.run_experiment` for the complete report.

See `MODULE4_EXPLAINED.md` for the reasoning and interpretation guide.
