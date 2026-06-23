"""CUPED variance reduction utilities."""
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class CupedResult:
    adjusted_outcome: pd.Series
    theta: float
    correlation: float
    variance_before: float
    variance_after: float
    variance_reduction: float


def apply_cuped(outcome: pd.Series, covariate: pd.Series) -> CupedResult:
    """Adjust an outcome using a pre-experiment covariate."""
    y = pd.to_numeric(outcome).astype(float)
    x = pd.to_numeric(covariate).astype(float)
    covariance = float(np.cov(y, x, ddof=1)[0, 1])
    x_variance = float(x.var(ddof=1))
    if x_variance == 0:
        raise ValueError("CUPED covariate has zero variance.")

    theta = covariance / x_variance
    adjusted = y - theta * (x - x.mean())
    variance_before = float(y.var(ddof=1))
    variance_after = float(adjusted.var(ddof=1))
    reduction = 1 - variance_after / variance_before

    return CupedResult(
        adjusted_outcome=adjusted,
        theta=float(theta),
        correlation=float(y.corr(x)),
        variance_before=variance_before,
        variance_after=variance_after,
        variance_reduction=float(reduction),
    )
