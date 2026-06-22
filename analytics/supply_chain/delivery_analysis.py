"""Late-delivery and lead-time analysis for Sections 7.2 and 7.3.

On-time fulfillment is used as a fill-rate proxy because the dataset has no
inventory or stock-level fields. A late-risk index above 1 means a group has
a higher late-delivery rate than the dataset-wide benchmark.

Usage:
    python -m analytics.supply_chain.delivery_analysis
"""
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

from analytics.snowflake_utils import query_df


OUTPUT_DIR = Path("analytics/supply_chain")


def main() -> None:
    delivery = query_df("SELECT * FROM vw_supply_chain_delivery")

    numeric_columns = [
        "ORDER_ITEM_COUNT",
        "LATE_COUNT",
        "LATE_DELIVERY_RATE",
        "AVG_ACTUAL_LEAD_DAYS",
        "AVG_SCHEDULED_LEAD_DAYS",
        "AVG_LEAD_TIME_VARIANCE_DAYS",
        "LATE_RISK_INDEX",
    ]
    delivery[numeric_columns] = delivery[numeric_columns].astype(float)

    weighted_late_rate = (
        delivery["LATE_COUNT"].sum() / delivery["ORDER_ITEM_COUNT"].sum()
    )
    print(f"Overall late-delivery rate: {weighted_late_rate:.1%}")
    print(f"On-time fulfillment proxy: {1 - weighted_late_rate:.1%}")

    mode_summary = delivery.groupby("SHIPPING_MODE", as_index=False).agg(
        items=("ORDER_ITEM_COUNT", "sum"),
        late_items=("LATE_COUNT", "sum"),
    )
    mode_summary["late_rate"] = (
        mode_summary["late_items"] / mode_summary["items"]
    )

    # Weight subgroup averages by order-item volume. Otherwise a tiny
    # region/category group influences the shipping-mode result as much as a
    # group containing thousands of items.
    for source, target in [
        ("AVG_ACTUAL_LEAD_DAYS", "avg_actual_days"),
        ("AVG_SCHEDULED_LEAD_DAYS", "avg_scheduled_days"),
        ("AVG_LEAD_TIME_VARIANCE_DAYS", "avg_variance_days"),
    ]:
        weighted = (
            delivery[source] * delivery["ORDER_ITEM_COUNT"]
        ).groupby(delivery["SHIPPING_MODE"]).sum()
        mode_summary[target] = (
            mode_summary["SHIPPING_MODE"].map(weighted)
            / mode_summary["items"]
        )

    mode_summary = mode_summary.sort_values("late_rate", ascending=False)
    print("\nDelivery performance by shipping mode:")
    print(mode_summary.to_string(index=False))

    high_volume = delivery[
        delivery["ORDER_ITEM_COUNT"]
        >= delivery["ORDER_ITEM_COUNT"].quantile(0.75)
    ]
    risky_groups = high_volume.sort_values(
        ["LATE_RISK_INDEX", "ORDER_ITEM_COUNT"], ascending=False
    )
    print("\nHighest-risk high-volume combinations:")
    print(
        risky_groups[
            [
                "ORDER_REGION",
                "SHIPPING_MODE",
                "CATEGORY_NAME",
                "ORDER_ITEM_COUNT",
                "LATE_DELIVERY_RATE",
                "LATE_RISK_INDEX",
                "AVG_LEAD_TIME_VARIANCE_DAYS",
            ]
        ]
        .head(15)
        .to_string(index=False)
    )

    plt.figure(figsize=(8, 5))
    sns.barplot(data=mode_summary, x="SHIPPING_MODE", y="late_rate")
    plt.axhline(
        weighted_late_rate,
        color="red",
        linestyle="--",
        label="Overall late rate",
    )
    plt.title("Late-delivery rate by shipping mode")
    plt.xlabel("Shipping mode")
    plt.ylabel("Late-delivery rate")
    plt.xticks(rotation=25)
    plt.legend()
    plt.tight_layout()
    output = OUTPUT_DIR / "late_rate_by_shipping_mode.png"
    plt.savefig(output)
    plt.close()
    print(f"\nSaved chart to {output}")


if __name__ == "__main__":
    main()

