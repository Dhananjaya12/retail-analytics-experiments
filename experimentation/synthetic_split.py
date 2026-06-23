"""Create a reproducible synthetic customer-level A/B experiment.

Known injected effects:
- continuous outcome: +5% synthetic order-value uplift;
- binary outcome: +5 percentage points repeat-purchase conversion.

The untreated continuous outcome blends real pre-period and experiment-period
AOV equally. This preserves real customer variation while ensuring the
pre-period covariate is meaningfully related to the outcome, which is required
to demonstrate CUPED rather than merely call the formula.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from analytics.snowflake_utils import query_df


RANDOM_SEED = 42
ORDER_VALUE_UPLIFT = 0.05
REPEAT_PURCHASE_UPLIFT = 0.05
OUTPUT_PATH = Path("experimentation/synthetic_experiment.csv")


def create_synthetic_experiment(seed: int = RANDOM_SEED) -> pd.DataFrame:
    """Randomize customers and inject known treatment effects."""
    data = query_df("SELECT * FROM vw_experiment_customer_metrics")
    data = data.dropna(subset=["PRE_EXPERIMENT_AOV", "EXPERIMENT_AOV"]).copy()
    if len(data) < 100:
        raise ValueError(
            "Fewer than 100 eligible customers. Revisit the experiment window."
        )

    rng = np.random.default_rng(seed)
    assignments = np.array(["control"] * len(data), dtype=object)
    assignments[rng.permutation(len(data))[: len(data) // 2]] = "treatment"
    data["GROUP"] = assignments

    pre_aov = pd.to_numeric(data["PRE_EXPERIMENT_AOV"])
    experiment_aov = pd.to_numeric(data["EXPERIMENT_AOV"])
    data["ORDER_VALUE_OUTCOME"] = 0.5 * pre_aov + 0.5 * experiment_aov
    treatment_mask = data["GROUP"] == "treatment"
    data.loc[treatment_mask, "ORDER_VALUE_OUTCOME"] *= 1 + ORDER_VALUE_UPLIFT

    data["REPEAT_PURCHASE_OUTCOME"] = pd.to_numeric(
        data["REPEAT_PURCHASE"]
    ).astype(int)
    eligible_to_flip = data.index[
        treatment_mask & (data["REPEAT_PURCHASE_OUTCOME"] == 0)
    ].to_numpy()
    flip_count = min(
        int(round(REPEAT_PURCHASE_UPLIFT * treatment_mask.sum())),
        len(eligible_to_flip),
    )
    if flip_count:
        flipped = rng.choice(eligible_to_flip, size=flip_count, replace=False)
        data.loc[flipped, "REPEAT_PURCHASE_OUTCOME"] = 1

    return data


def main() -> None:
    experiment = create_synthetic_experiment()
    experiment.to_csv(OUTPUT_PATH, index=False)
    print(f"Eligible customers: {len(experiment):,}")
    print("\nRandomized group counts:")
    print(experiment["GROUP"].value_counts())
    print("\nPre-period AOV by group (balance check):")
    print(experiment.groupby("GROUP")["PRE_EXPERIMENT_AOV"].mean())
    print(f"\nSaved synthetic experiment to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

