"""Demand trend analysis for PROJECT_PLAN.md Section 7.1.

Uses Snowflake views for monthly and weekly aggregation, rolling averages,
and growth rates. This is descriptive trend analysis, not forecasting.

Usage:
    python -m analytics.supply_chain.demand_analysis
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from analytics.snowflake_utils import query_df


OUTPUT_DIR = Path("analytics/supply_chain")


def main() -> None:
    monthly = query_df("SELECT * FROM vw_demand_monthly")
    weekly = query_df("SELECT * FROM vw_demand_weekly")

    print(f"Monthly demand rows: {len(monthly):,}")
    print(f"Weekly demand rows: {len(weekly):,}")

    category_summary = (
        monthly.groupby("CATEGORY_NAME", as_index=False)
        .agg(
            units_sold=("UNITS_SOLD", "sum"),
            total_sales=("TOTAL_SALES", "sum"),
        )
        .sort_values("units_sold", ascending=False)
    )
    print("\nTop 10 categories by units sold:")
    print(category_summary.head(10).to_string(index=False))

    region_summary = (
        monthly.groupby("ORDER_REGION", as_index=False)
        .agg(units_sold=("UNITS_SOLD", "sum"))
        .sort_values("units_sold", ascending=False)
    )
    print("\nTop 10 regions by units sold:")
    print(region_summary.head(10).to_string(index=False))

    category_monthly = (
        monthly.groupby(["DEMAND_MONTH", "CATEGORY_NAME"], as_index=False)
        .agg(units_sold=("UNITS_SOLD", "sum"))
    )
    top_categories = category_summary.head(5)["CATEGORY_NAME"]
    plot_data = category_monthly[
        category_monthly["CATEGORY_NAME"].isin(top_categories)
    ].copy()
    plot_data["DEMAND_MONTH"] = pd.to_datetime(plot_data["DEMAND_MONTH"])

    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=plot_data,
        x="DEMAND_MONTH",
        y="units_sold",
        hue="CATEGORY_NAME",
    )
    plt.title("Monthly demand for top 5 product categories")
    plt.xlabel("Month")
    plt.ylabel("Units sold")
    plt.tight_layout()
    output = OUTPUT_DIR / "monthly_category_demand.png"
    plt.savefig(output)
    plt.close()
    print(f"\nSaved chart to {output}")


if __name__ == "__main__":
    main()
