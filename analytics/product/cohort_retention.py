"""Cohort & retention analysis (PROJECT_PLAN.md Section 6.2).

Cohort = month of customer's first order. For each cohort, tracks the % of
customers placing another order in month+1, month+2, etc. Standard SaaS-
style cohort table, applied to retail order data.

Usage:
    python analytics/product/cohort_retention.py
"""
import matplotlib.pyplot as plt
import seaborn as sns

from analytics.snowflake_utils import query_df


def main() -> None:
    cohort_orders = query_df("SELECT * FROM vw_cohort_orders")

    cohort_sizes = (
        cohort_orders[cohort_orders["PERIOD_NUMBER"] == 0]
        .groupby("COHORT_MONTH")["CUSTOMER_ID"]
        .nunique()
    )

    cohort_counts = (
        cohort_orders.groupby(["COHORT_MONTH", "PERIOD_NUMBER"])["CUSTOMER_ID"]
        .nunique()
        .reset_index()
        .pivot(index="COHORT_MONTH", columns="PERIOD_NUMBER", values="CUSTOMER_ID")
    )

    retention = cohort_counts.divide(cohort_sizes, axis=0)

    print("Cohort sizes (month 0):")
    print(cohort_sizes)
    print("\nRetention matrix (% of cohort active in month N):")
    print((retention * 100).round(1))

    plt.figure(figsize=(14, 8))
    sns.heatmap(retention, annot=True, fmt=".0%", cmap="Blues")
    plt.title("Customer retention by cohort month")
    plt.xlabel("Months since first order")
    plt.ylabel("Cohort month")
    plt.tight_layout()
    plt.savefig("analytics/product/cohort_retention_heatmap.png")
    print("\nSaved chart to analytics/product/cohort_retention_heatmap.png")


if __name__ == "__main__":
    main()
