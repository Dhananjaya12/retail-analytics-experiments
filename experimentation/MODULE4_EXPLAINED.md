# Module 4 Explained — A/B Testing, CUPED, and Power

## What this module asks

Suppose a company introduces a new discount or checkout strategy. Customers in the treatment group appear to spend more. Did the change cause the increase, or could random noise explain it?

A randomized A/B test answers that question by assigning comparable customers to control and treatment groups and changing only the treatment experience.

## Why the experiment is synthetic

The retail dataset contains historical transactions, not a real randomized experiment. We must not pretend an existing segment comparison is causal.

Instead, we create a reproducible 50/50 customer split and inject effects whose true values are known:

- +5% order-value outcome for treatment. The untreated synthetic outcome is an equal blend of each customer’s real pre-period and experiment-period AOV. This preserves real variation while creating the pre/outcome correlation CUPED requires;
- +5 percentage points repeat-purchase conversion for treatment.

If the testing engine recovers these planted effects, it demonstrates that the statistical workflow behaves correctly.

## Experiment population and periods

The final 365 observed days are the experiment period. Earlier purchases form the pre-period. Customers need activity in both periods because CUPED requires a historical covariate.

The pre-period average order value is not an outcome. It is information known before treatment assignment and is used for randomization balance checks and CUPED.

## Randomization balance

Before evaluating treatment outcomes, we compare pre-period AOV between control and treatment. Because assignment is random, the groups should not show a meaningful pre-existing difference. A large balance-check p-value is desirable; it is not evidence that treatment failed.

## Continuous outcome: Welch's t-test

Average order value is continuous. Welch's t-test compares treatment and control means without assuming equal variance.

We report:

- control and treatment means;
- absolute effect;
- relative lift;
- p-value;
- 95% confidence interval;
- Cohen's d standardized effect size.

If the confidence interval excludes zero and the p-value is below 0.05, the result is statistically significant at the chosen threshold.

## Binary outcome: two-proportion z-test

Repeat purchase is binary: a customer either repeated or did not. We compare the two conversion rates using a two-proportion z-test and report the absolute percentage-point effect, relative lift, confidence interval, and p-value.

## CUPED

CUPED uses a pre-experiment metric correlated with the outcome to remove predictable customer-to-customer variation:

`Y_adjusted = Y - theta * (X - mean(X))`

Here, `X` is pre-period AOV and `Y` is experiment-period AOV. CUPED should preserve the treatment effect while reducing variance. Lower variance produces a narrower confidence interval or greater power with the same sample size.

CUPED is useful only when the pre-period covariate is correlated with the outcome. The script reports that correlation and the actual percentage variance reduction.

## Power analysis

Power is the probability of detecting a real effect of the specified size. We use alpha 0.05 and target power 0.80.

For each metric, the analysis reports:

- required customers per group;
- actual customers per group;
- achieved power with the available sample.

A non-significant result from an underpowered experiment is inconclusive, not proof of no effect.

## Observational comparison

The module also compares Corporate and Consumer customer AOV using real segment labels. This is explicitly observational. Segment membership was not randomized, so differences may be caused by geography, product mix, customer behavior, or other confounders.

The comparison demonstrates statistical testing but supports association only, not a causal claim.

## Files

- `warehouse/vw_experiment_customer_metrics.sql`: experiment/pre-period customer metrics.
- `experimentation/synthetic_split.py`: randomized assignment and effect injection.
- `experimentation/ab_test.py`: Welch and proportion tests.
- `experimentation/cuped.py`: variance reduction.
- `experimentation/power_analysis.py`: required sample and achieved power.
- `experimentation/run_experiment.py`: complete end-to-end report.

