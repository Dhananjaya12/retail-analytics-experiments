# Module 4 Explained from the Beginning

This guide assumes you have never studied A/B testing or statistics.

## 1. What is an experiment?

Imagine an online store wants to change its checkout page.

The company hopes the new page will make customers spend more money or return
for another purchase. After launching it, sales increase. Did the new page cause
the increase?

We cannot know just by looking at sales before and after. Sales may have changed
because of a holiday, advertising, weather, new products, or random chance.

An experiment tries to separate the effect of the change from everything else.

## 2. What are control and treatment groups?

We divide customers into two groups:

- **Control group:** sees the old experience.
- **Treatment group:** sees the new experience.

The control group gives us a fair picture of what would probably have happened
without the change.

Suppose the average customer spends:

- Control: $100
- Treatment: $105

The estimated effect is $5, or a 5% increase.

## 3. Why must assignment be random?

Random assignment means every eligible customer has the same chance of entering
either group. It is like fairly shuffling cards.

Without random assignment, imagine putting loyal customers in treatment and new
customers in control. Treatment would probably look better even if the new page
did nothing.

Random assignment makes the groups similar on average. Therefore, the main
planned difference between them is the treatment itself. This is why a properly
randomized experiment can support a statement such as:

> The new experience caused the observed difference.

## 4. Why is our experiment synthetic?

The retail dataset contains old transactions. No real company experiment was
performed when those orders were collected.

We cannot honestly claim that Corporate and Consumer customers were randomly
assigned. They already belonged to those groups for real-world reasons.

Therefore, we build a practice experiment:

1. Select customers with usable historical and later-period data.
2. Randomly assign half to control and half to treatment.
3. Add a known improvement to treatment.
4. Check whether our statistical tools find that known improvement.

This is called **synthetic** because the treatment effect is simulated. The
customer values and purchasing variation still come from real data.

We planted two effects:

- Treatment order value increased by 5%.
- Treatment repeat-purchase rate increased by 5 percentage points.

Because we know the correct answer, we can test whether our analysis works.

## 5. Who was included?

The experiment used 8,190 eligible customers:

- 4,095 control customers
- 4,095 treatment customers

The final 365 days of the dataset were treated as the experiment period. Earlier
orders formed the pre-experiment period.

A customer needed purchases in both periods because CUPED requires historical
information.

## 6. What is a metric?

A metric is simply the number used to measure success.

We used two metrics.

### Average order value

This answers:

> On average, how much money was spent per order?

It is a continuous metric because it can have many numeric values, such as
$85.40, $120, or $231.75.

### Repeat purchase

This answers:

> Did the customer place at least two orders during the experiment period?

It is a binary metric because there are only two answers:

- 1 = yes
- 0 = no

Different kinds of metrics need different statistical tests.

## 7. Checking whether randomization worked

Before measuring the treatment result, we compare the groups using information
from before the experiment.

Pre-period average order value was:

- Control: $195.87
- Treatment: $197.09
- Difference: $1.22

That difference is very small. Cohen's d was 0.028, which also means the groups
were extremely similar.

The p-value was 0.199. For this balance check, a large p-value is good: we did
not find convincing evidence that the groups were already different before the
treatment.

This does not prove perfect equality. It means the observed difference is small
enough to be believable under random assignment.

## 8. What is random noise?

Even with fair randomization, the group averages will almost never be exactly
equal. Random samples naturally differ.

For example, flip a fair coin ten times. You may get six heads instead of
exactly five. The coin is still fair.

Statistical tests help us decide whether an observed difference is large enough
to stand out from ordinary random variation.

## 9. What is a p-value?

A p-value asks:

> If the treatment truly had no effect, how surprising would results at least
> this different be because of random variation alone?

A small p-value means the result would be difficult to explain using random
noise alone.

A common threshold is 0.05:

- p-value below 0.05: called statistically significant;
- p-value above 0.05: not enough evidence at that threshold.

A p-value does **not** tell us:

- the probability that the treatment works;
- whether the effect is important to the business;
- whether the experiment was designed correctly.

It is one piece of evidence, not a final business decision.

## 10. What is a confidence interval?

The measured effect is only an estimate. If we repeated the experiment with new
customers, the exact result would change slightly.

A 95% confidence interval gives a reasonable range of values for the true
effect, based on the model assumptions and experiment design.

For order value, the raw result was:

- Estimated effect: +$10.34
- 95% confidence interval: +$8.58 to +$12.10

The whole interval is above zero. That is evidence that the effect is positive.

The interval is more informative than the p-value because it shows both the
likely direction and size of the effect.

## 11. Continuous metric result

Experiment-period order value was:

- Control: $201.94
- Treatment: $212.29
- Difference: +$10.34
- Relative increase: 5.12%

We planted a 5% increase, and the analysis found approximately 5.12%. The small
difference comes from random group composition.

The p-value was extremely small, so random noise alone is not a convincing
explanation for this difference.

## 12. What is Welch's t-test?

Welch's t-test is a calculation for comparing two averages.

It considers:

- the difference between the averages;
- how spread out customer values are;
- how many customers are in each group.

A difference is easier to detect when groups are large and values are stable. It
is harder to detect when groups are small or customer values vary widely.

We use the Welch version because it does not require both groups to have exactly
the same amount of variance.

## 13. What is effect size?

Statistical significance asks whether an effect is distinguishable from noise.
Effect size asks how large the effect is.

We reported:

- Absolute effect: +$10.34
- Relative lift: +5.12%
- Cohen's d: 0.255

Cohen's d expresses the difference relative to normal customer-to-customer
variation. About 0.255 is usually considered a small effect, but a small effect
can still be valuable when applied to many customers.

Business importance depends on cost and scale, not only a statistical label.

## 14. Binary metric result

Repeat-purchase rates were:

- Control: 45.32%
- Treatment: 50.53%

There are two ways to describe this change.

### Percentage-point increase

50.53% - 45.32% = 5.20 percentage points.

### Relative increase

5.20 / 45.32 = approximately 11.48%.

These are not contradictory. They describe the same result differently.

The 95% confidence interval for the percentage-point effect was 3.04% to 7.36%.
It does not include zero, so the evidence supports a positive effect.

## 15. What is the two-proportion z-test?

This test compares two yes/no rates. It asks whether the difference between the
control and treatment percentages is too large to be reasonably explained by
random variation.

It is the binary-metric counterpart to the test used for averages.

## 16. Why customer spending creates noise

Some customers naturally spend very little. Others naturally spend much more.
This variation makes the treatment effect harder to see.

Imagine trying to hear a quiet melody in a noisy room. The treatment effect is
the melody. Natural customer differences are background noise.

CUPED tries to remove part of that predictable background noise.

## 17. What is CUPED?

CUPED uses information known before the experiment to improve measurement.

A customer who spent heavily before the experiment may also tend to spend
heavily during it. Historical spending can explain part of the later outcome.

CUPED roughly does this:

1. Estimate how strongly pre-period spending predicts experiment spending.
2. Remove that predictable part from the experiment outcome.
3. Compare control and treatment using the adjusted values.

It does not create a larger treatment effect. It aims to measure the effect more
precisely.

An analogy: runners begin at different natural speeds. Instead of comparing
only finishing speeds, historical speeds help account for those starting
differences.

## 18. Why we changed the first synthetic outcome

Initially, the pre-period AOV and experiment outcome had almost zero
correlation: 0.00146.

That means historical spending told us almost nothing about the later outcome.
CUPED correctly produced almost no improvement.

To demonstrate CUPED honestly, we created a synthetic untreated outcome that
blends:

- 50% real pre-period AOV;
- 50% real experiment-period AOV.

Then we applied the known 5% treatment increase.

This preserves real customer variation while creating a meaningful relationship
between historical and later spending. The final correlation was 0.540.

This design choice is clearly disclosed because the experiment is a method
validation exercise, not a real company intervention.

## 19. CUPED result

Before CUPED:

- Variance: 1674.59
- Confidence interval: $8.58 to $12.10
- Interval width: $3.52

After CUPED:

- Variance: 1186.20
- Confidence interval: $8.24 to $11.19
- Interval width: $2.95

CUPED reduced variance by 29.2% and narrowed the confidence interval by about
16%.

Why did a 29.2% variance reduction produce only a 16% narrower interval?
Confidence-interval width depends on the square root of variance, not directly
on variance itself. This is expected.

The adjusted effect was +$9.72, close to the raw +$10.34 estimate. CUPED made
the estimate more precise rather than changing the business conclusion.

## 20. What is statistical power?

Power asks:

> If an effect of the planned size really exists, how likely is the experiment
> to detect it?

We normally target at least 80% power.

Low power is like searching a dark room with a weak flashlight. Failing to see
something does not prove it is absent.

## 21. Power results

For the observed order-value effect:

- Required customers per group: 247
- Available customers per group: 4,095
- Achieved power: approximately 100%

For the five-percentage-point repeat-purchase effect:

- Required customers per group: 1,566
- Available customers per group: 4,095
- Achieved power: 99.5%

The experiment had far more customers than required for effects of these sizes.
This is why both effects were detected clearly.

This does not mean every tiny effect could be detected. Smaller effects require
larger samples.

## 22. Randomized versus observational analysis

We also compared Corporate and Consumer customers using real customer labels.

Average order values were:

- Consumer: $477.66
- Corporate: $480.10
- Difference: $2.43
- p-value: 0.601
- Confidence interval: -$6.67 to +$11.53

The interval crosses zero, so the data does not show a clear difference.

More importantly, this comparison is observational. Customers were not randomly
assigned to become Corporate or Consumer. Even if the difference were
significant, segment membership might be connected to geography, product mix,
company size, or other factors.

Therefore:

- Randomized experiment: can support a causal claim.
- Observational comparison: supports association only.

## 23. What we proved and what we did not prove

### We demonstrated

- reproducible random assignment;
- a balance check;
- testing a continuous outcome;
- testing a binary outcome;
- confidence intervals and effect sizes;
- CUPED variance reduction;
- sample-size and power calculations;
- correct separation of causal and observational claims.

### We did not prove

- that a real discount strategy raises order value by 5%;
- that a real checkout change raises repeat purchases;
- that the synthetic business results should be deployed.

The effects were intentionally planted. This module validates the analytics
process, not a real intervention.

## 24. The entire workflow in one simple sequence

1. Choose who is eligible.
2. Randomly split customers into control and treatment.
3. Confirm the groups look similar before treatment.
4. Define success metrics before examining results.
5. Run the experiment.
6. Compare group outcomes with the correct tests.
7. Report effect size, uncertainty, and p-value.
8. Use CUPED when a useful pre-period metric exists.
9. Check whether sample size provides enough power.
10. Separate randomized causal evidence from observational association.

## 25. Files

- `warehouse/vw_experiment_customer_metrics.sql`: prepares historical and experiment-period customer metrics.
- `experimentation/synthetic_split.py`: randomizes customers and plants known effects.
- `experimentation/ab_test.py`: compares averages and conversion rates.
- `experimentation/cuped.py`: reduces predictable variance.
- `experimentation/power_analysis.py`: checks required sample size and achieved power.
- `experimentation/run_experiment.py`: runs the full report.
- `experimentation/module4_walkthrough.ipynb`: presentation notebook.

Read this guide first, then use the notebook to see each idea applied to the
actual validated results.
