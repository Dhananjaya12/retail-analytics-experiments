"""RFM segmentation profiling (PROJECT_PLAN.md Section 6.1).

Scoring itself happens in warehouse/vw_rfm_scores.sql (NTILE-based quintiles
on recency/frequency/monetary). This script profiles and visualizes the
resulting segments.

Usage:
    python analytics/product/rfm_segmentation.py
"""
import matplotlib.pyplot as plt
import seaborn as sns

from analytics.snowflake_utils import query_df


def main() -> None:
    rfm = query_df("SELECT * FROM vw_rfm_scores")

    segment_counts = rfm["RFM_SEGMENT"].value_counts()
    print("Customer count by RFM segment:")
    print(segment_counts)

    segment_profile = (
        rfm.groupby("RFM_SEGMENT")
        .agg(
            customers=("CUSTOMER_ID", "count"),
            avg_recency_days=("RECENCY_DAYS", "mean"),
            avg_frequency=("FREQUENCY", "mean"),
            avg_monetary=("MONETARY", "mean"),
        )
        .sort_values("avg_monetary", ascending=False)
    )
    print("\nSegment profile:")
    print(segment_profile)

    plt.figure(figsize=(8, 5))
    sns.barplot(x=segment_counts.index, y=segment_counts.values)
    plt.title("Customer count by RFM segment")
    plt.ylabel("Customers")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("analytics/product/rfm_segment_counts.png")
    print("\nSaved chart to analytics/product/rfm_segment_counts.png")


if __name__ == "__main__":
    main()
