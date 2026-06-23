"""Reusable statistical tests for Module 4 experimentation."""
from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass
class ContinuousTestResult:
    control_mean: float
    treatment_mean: float
    absolute_effect: float
    relative_lift: float
    p_value: float
    ci_low: float
    ci_high: float
    cohens_d: float


@dataclass
class ProportionTestResult:
    control_rate: float
    treatment_rate: float
    absolute_effect: float
    relative_lift: float
    z_statistic: float
    p_value: float
    ci_low: float
    ci_high: float


def welch_t_test(control: np.ndarray, treatment: np.ndarray) -> ContinuousTestResult:
    """Compare continuous outcomes without assuming equal variances."""
    control = np.asarray(control, dtype=float)
    treatment = np.asarray(treatment, dtype=float)
    control_mean = float(control.mean())
    treatment_mean = float(treatment.mean())
    effect = treatment_mean - control_mean

    test = stats.ttest_ind(treatment, control, equal_var=False)
    control_var = control.var(ddof=1)
    treatment_var = treatment.var(ddof=1)
    se = np.sqrt(control_var / len(control) + treatment_var / len(treatment))
    numerator = (control_var / len(control) + treatment_var / len(treatment)) ** 2
    denominator = (
        (control_var / len(control)) ** 2 / (len(control) - 1)
        + (treatment_var / len(treatment)) ** 2 / (len(treatment) - 1)
    )
    degrees_freedom = numerator / denominator
    critical = stats.t.ppf(0.975, degrees_freedom)

    pooled_sd = np.sqrt(
        ((len(control) - 1) * control_var + (len(treatment) - 1) * treatment_var)
        / (len(control) + len(treatment) - 2)
    )
    cohens_d = effect / pooled_sd if pooled_sd else float("nan")

    return ContinuousTestResult(
        control_mean=control_mean,
        treatment_mean=treatment_mean,
        absolute_effect=effect,
        relative_lift=effect / control_mean if control_mean else float("nan"),
        p_value=float(test.pvalue),
        ci_low=float(effect - critical * se),
        ci_high=float(effect + critical * se),
        cohens_d=float(cohens_d),
    )


def two_proportion_z_test(
    control_successes: int,
    control_total: int,
    treatment_successes: int,
    treatment_total: int,
) -> ProportionTestResult:
    """Compare two binary conversion rates using a pooled z-test."""
    control_rate = control_successes / control_total
    treatment_rate = treatment_successes / treatment_total
    effect = treatment_rate - control_rate
    pooled = (control_successes + treatment_successes) / (
        control_total + treatment_total
    )
    pooled_se = np.sqrt(
        pooled * (1 - pooled) * (1 / control_total + 1 / treatment_total)
    )
    z_statistic = effect / pooled_se if pooled_se else float("nan")
    p_value = 2 * stats.norm.sf(abs(z_statistic))

    unpooled_se = np.sqrt(
        control_rate * (1 - control_rate) / control_total
        + treatment_rate * (1 - treatment_rate) / treatment_total
    )
    critical = stats.norm.ppf(0.975)

    return ProportionTestResult(
        control_rate=float(control_rate),
        treatment_rate=float(treatment_rate),
        absolute_effect=float(effect),
        relative_lift=float(effect / control_rate) if control_rate else float("nan"),
        z_statistic=float(z_statistic),
        p_value=float(p_value),
        ci_low=float(effect - critical * unpooled_se),
        ci_high=float(effect + critical * unpooled_se),
    )
