"""Sample-size and statistical-power calculations for Module 4."""
from dataclasses import dataclass

import numpy as np
from statsmodels.stats.power import NormalIndPower, TTestIndPower
from statsmodels.stats.proportion import proportion_effectsize


@dataclass
class PowerResult:
    required_per_group: int
    actual_per_group: int
    achieved_power: float


def continuous_power(
    standardized_effect: float,
    actual_per_group: int,
    alpha: float = 0.05,
    target_power: float = 0.80,
) -> PowerResult:
    """Power analysis for a two-sided independent-samples t-test."""
    analysis = TTestIndPower()
    required = analysis.solve_power(
        effect_size=abs(standardized_effect),
        alpha=alpha,
        power=target_power,
        ratio=1.0,
        alternative="two-sided",
    )
    achieved = analysis.power(
        effect_size=abs(standardized_effect),
        nobs1=actual_per_group,
        alpha=alpha,
        ratio=1.0,
        alternative="two-sided",
    )
    # Some scipy/statsmodels combinations return NaN for the noncentral-t
    # calculation at very large sample sizes. Fall back to the asymptotic
    # normal approximation, which is appropriate at this N.
    if not np.isfinite(achieved):
        achieved = NormalIndPower().power(
            effect_size=abs(standardized_effect),
            nobs1=actual_per_group,
            alpha=alpha,
            ratio=1.0,
            alternative="two-sided",
        )
    return PowerResult(int(required + 0.9999), actual_per_group, float(achieved))


def proportion_power(
    baseline_rate: float,
    target_rate: float,
    actual_per_group: int,
    alpha: float = 0.05,
    target_power: float = 0.80,
) -> PowerResult:
    """Power analysis for two independent conversion rates."""
    effect = abs(proportion_effectsize(target_rate, baseline_rate))
    analysis = NormalIndPower()
    required = analysis.solve_power(
        effect_size=effect,
        alpha=alpha,
        power=target_power,
        ratio=1.0,
        alternative="two-sided",
    )
    achieved = analysis.power(
        effect_size=effect,
        nobs1=actual_per_group,
        alpha=alpha,
        ratio=1.0,
        alternative="two-sided",
    )
    return PowerResult(int(required + 0.9999), actual_per_group, float(achieved))


