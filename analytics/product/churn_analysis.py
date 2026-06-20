"""Churn flag + explanatory churn-driver model (PROJECT_PLAN.md Section 6.3).

Churn = no order in the last 90 days relative to the dataset's max order
date (see warehouse/vw_churn_flag.sql). The logistic regression here is
explanatory only — it demonstrates the analytics pattern (churn drivers via
RFM-style features + segment), not a production churn model. Recency is
excluded as a feature since it directly determines the label.

Usage:
    python analytics/product/churn_analysis.py
"""
import pandas as pd
import statsmodels.api as sm

from analytics.snowflake_utils import query_df


def main() -> None:
    churn = query_df("SELECT * FROM vw_churn_flag")

    churn_rate = churn["IS_CHURNED"].mean()
    print(f"Overall churn rate (>90 days since last order): {churn_rate:.1%}")
    print("\nChurn rate by customer segment:")
    print(churn.groupby("CUSTOMER_SEGMENT")["IS_CHURNED"].mean())

    # ORDER_COUNT near-perfectly separates churned/non-churned in this
    # dataset (repeat orders mechanically land closer to the dataset's end
    # date), which breaks logistic regression (quasi-separation, infinite
    # coefficients). That's a real finding -- report it descriptively
    # instead of forcing it into the model.
    order_count_bucket = churn["ORDER_COUNT"].clip(upper=3).map({1: "1 order", 2: "2 orders", 3: "3+ orders"})
    print("\nChurn rate by order count (frequency is the dominant churn driver):")
    print(churn.groupby(order_count_bucket)["IS_CHURNED"].mean())

    # TOTAL_SALES and AVG_ORDER_VALUE are near-perfectly collinear here
    # (identical for the ~70% of customers with exactly 1 order, since
    # avg = total when count = 1), so only one of them is included.
    features = churn[["AVG_ORDER_VALUE", "CUSTOMER_SEGMENT"]].copy()
    features = pd.get_dummies(features, columns=["CUSTOMER_SEGMENT"], drop_first=True)
    features = sm.add_constant(features.astype(float))
    target = churn["IS_CHURNED"].astype(int)

    model = sm.Logit(target, features).fit(disp=False)
    print("\nLogistic regression: churn drivers excluding order count")
    print("(avg order value + segment only, since frequency causes separation)")
    print(model.summary())


if __name__ == "__main__":
    main()
