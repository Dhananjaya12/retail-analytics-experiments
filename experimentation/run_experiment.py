"""Run the complete Module 4 experimentation analysis.

This script performs:
1. Randomized synthetic experiment with known effects.
2. Welch t-test for average order value.
3. Two-proportion z-test for repeat purchase.
4. CUPED adjustment and variance comparison.
5. Sample-size and achieved-power calculations.
6. A clearly labelled observational segment comparison.

Usage:
    python -m experimentation.run_experiment
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from analytics.snowflake_utils import query_df
from experimentation.ab_test import two_proportion_z_test, welch_t_test
from experimentation.cuped import apply_cuped
from experimentation.power_analysis import continuous_power, proportion_power
from experimentation.synthetic_split import (
    ORDER_VALUE_UPLIFT,
    REPEAT_PURCHASE_UPLIFT,
    create_synthetic_experiment,
)


OUTPUT_DIR = Path("experimentation")


def print_continuous_result(label: str, result: object) -> None:
    """Print a compact continuous-metric test result."""
    print(f"\n{label}")
    print(f"  Control mean:      {result.control_mean:.2f}")
    print(f"  Treatment mean:    {result.treatment_mean:.2f}")
    print(f"  Absolute effect:   {result.absolute_effect:.2f}")
    print(f"  Relative lift:     {result.relative_lift:.2%}")
    print(f"  95% CI:            [{result.ci_low:.2f}, {result.ci_high:.2f}]")
    print(f"  p-value:           {result.p_value:.6g}")
    print(f"  Cohen's d:         {result.cohens_d:.4f}")


def main() -> None:
    experiment = create_synthetic_experiment()
    control = experiment[experiment["GROUP"] == "control"].copy()
    treatment = experiment[experiment["GROUP"] == "treatment"].copy()

    print("SYNTHETIC RANDOMIZED EXPERIMENT")
    print(f"Eligible customers: {len(experiment):,}")
    print(f"Control: {len(control):,} | Treatment: {len(treatment):,}")
    print(f"Injected order-value uplift: {ORDER_VALUE_UPLIFT:.1%}")
    print(
        "Injected repeat-purchase uplift: "
        f"{REPEAT_PURCHASE_UPLIFT:.1%} percentage points"
    )

    balance = welch_t_test(
        control["PRE_EXPERIMENT_AOV"], treatment["PRE_EXPERIMENT_AOV"]
    )
    print_continuous_result("Randomization balance check: pre-period AOV", balance)
    print(
        "  Interpretation: a large p-value is desirable here; it indicates "
        "no evidence of a pre-existing group difference."
    )

    raw_result = welch_t_test(
        control["ORDER_VALUE_OUTCOME"], treatment["ORDER_VALUE_OUTCOME"]
    )
    print_continuous_result("Raw Welch t-test: experiment-period AOV", raw_result)

    cuped = apply_cuped(
        experiment["ORDER_VALUE_OUTCOME"], experiment["PRE_EXPERIMENT_AOV"]
    )
    experiment["ORDER_VALUE_CUPED"] = cuped.adjusted_outcome
    control_cuped = experiment.loc[
        experiment["GROUP"] == "control", "ORDER_VALUE_CUPED"
    ]
    treatment_cuped = experiment.loc[
        experiment["GROUP"] == "treatment", "ORDER_VALUE_CUPED"
    ]
    cuped_result = welch_t_test(control_cuped, treatment_cuped)
    print_continuous_result("CUPED-adjusted Welch t-test", cuped_result)
    print(f"  Pre/outcome correlation: {cuped.correlation:.3f}")
    print(f"  CUPED theta:             {cuped.theta:.4f}")
    print(f"  Variance before CUPED:   {cuped.variance_before:.2f}")
    print(f"  Variance after CUPED:    {cuped.variance_after:.2f}")
    print(f"  Variance reduction:      {cuped.variance_reduction:.1%}")

    conversion_result = two_proportion_z_test(
        int(control["REPEAT_PURCHASE_OUTCOME"].sum()),
        len(control),
        int(treatment["REPEAT_PURCHASE_OUTCOME"].sum()),
        len(treatment),
    )
    print("\nTwo-proportion z-test: repeat purchase")
    print(f"  Control rate:       {conversion_result.control_rate:.2%}")
    print(f"  Treatment rate:     {conversion_result.treatment_rate:.2%}")
    print(f"  Absolute effect:    {conversion_result.absolute_effect:.2%}")
    print(f"  Relative lift:      {conversion_result.relative_lift:.2%}")
    print(
        f"  95% CI:             [{conversion_result.ci_low:.2%}, "
        f"{conversion_result.ci_high:.2%}]"
    )
    print(f"  p-value:            {conversion_result.p_value:.6g}")

    pooled_sd = float(experiment["ORDER_VALUE_OUTCOME"].std(ddof=1))
    standardized_effect = raw_result.absolute_effect / pooled_sd
    continuous_power_result = continuous_power(
        standardized_effect=standardized_effect,
        actual_per_group=min(len(control), len(treatment)),
    )
    conversion_power_result = proportion_power(
        baseline_rate=conversion_result.control_rate,
        target_rate=min(conversion_result.control_rate + REPEAT_PURCHASE_UPLIFT, 0.999),
        actual_per_group=min(len(control), len(treatment)),
    )
    print("\nPower analysis (alpha=0.05, target power=0.80)")
    print(
        "  Continuous metric required/actual per group: "
        f"{continuous_power_result.required_per_group:,} / "
        f"{continuous_power_result.actual_per_group:,}"
    )
    print(
        f"  Continuous achieved power: {continuous_power_result.achieved_power:.1%}"
    )
    print(
        "  Conversion metric required/actual per group: "
        f"{conversion_power_result.required_per_group:,} / "
        f"{conversion_power_result.actual_per_group:,}"
    )
    print(
        f"  Conversion achieved power: {conversion_power_result.achieved_power:.1%}"
    )

    observational = query_df(
        """
        SELECT customer_segment, avg_order_value
        FROM vw_customer_summary
        WHERE customer_segment IN ('Consumer', 'Corporate')
        """
    )
    consumer = observational.loc[
        observational["CUSTOMER_SEGMENT"] == "Consumer", "AVG_ORDER_VALUE"
    ]
    corporate = observational.loc[
        observational["CUSTOMER_SEGMENT"] == "Corporate", "AVG_ORDER_VALUE"
    ]
    observational_result = welch_t_test(consumer, corporate)
    print_continuous_result(
        "Observational comparison: Corporate vs Consumer AOV",
        observational_result,
    )
    print(
        "  CAUTION: this comparison is observational, not randomized. "
        "It describes association and must not be interpreted causally."
    )

    comparison = pd.DataFrame(
        {
            "estimate": [raw_result.absolute_effect, cuped_result.absolute_effect],
            "ci_low": [raw_result.ci_low, cuped_result.ci_low],
            "ci_high": [raw_result.ci_high, cuped_result.ci_high],
            "method": ["Raw", "CUPED"],
        }
    )
    comparison["ci_width"] = comparison["ci_high"] - comparison["ci_low"]
    errors = np.vstack(
        [
            comparison["estimate"] - comparison["ci_low"],
            comparison["ci_high"] - comparison["estimate"],
        ]
    )
    ci_narrowing = 1 - (
        comparison.loc[comparison["method"] == "CUPED", "ci_width"].iloc[0]
        / comparison.loc[comparison["method"] == "Raw", "ci_width"].iloc[0]
    )
    print(f"  95% CI narrowing from CUPED: {ci_narrowing:.1%}")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
    for axis, zoomed in zip(axes, [False, True]):
        axis.errorbar(
            comparison["estimate"],
            comparison["method"],
            xerr=errors,
            fmt="o",
            capsize=5,
        )
        axis.axvline(0, color="gray", linestyle="--")
        axis.set_xlabel("Estimated AOV effect (95% CI)")
        axis.set_title("Zoomed CI comparison" if zoomed else "Full scale")
        if zoomed:
            padding = 0.5
            axis.set_xlim(
                comparison["ci_low"].min() - padding,
                comparison["ci_high"].max() + padding,
            )
        for row_index, row in comparison.reset_index(drop=True).iterrows():
            axis.annotate(
                f"width={row['ci_width']:.2f}",
                (row["ci_high"], row_index),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=9,
            )
    fig.suptitle(
        f"Raw vs CUPED treatment effect — CI narrowed {ci_narrowing:.1%}"
    )
    fig.tight_layout()
    output = OUTPUT_DIR / "raw_vs_cuped_effect.png"
    fig.savefig(output)
    plt.close(fig)
    print(f"\nSaved comparison chart to {output}")


if __name__ == "__main__":
    main()

