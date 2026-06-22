# Module 3: Supply Chain Analytics — Plain-English Guide

## What this module is trying to answer

This module asks three practical questions:

1. What products are customers buying, where, and when?
2. Which deliveries are most likely to arrive late?
3. How closely does actual shipping time match the promised shipping time?

It is descriptive analysis. We explain what happened and where problems are
concentrated. We do not forecast future demand or optimize inventory because
those tasks are outside this project's scope.

## Part 1: Demand analysis

Here, **demand** means the number of units customers purchased.

We calculate demand:

- by product and category;
- by region;
- by month and week.

Raw weekly or monthly numbers can jump around, so we also calculate rolling
averages:

- a 3-month rolling average;
- a 4-week rolling average.

A rolling average is simply the average of the current period and a few recent
periods. It makes the overall direction easier to see.

We also calculate month-over-month and week-over-week percentage changes. These
tell us how much demand changed compared with the previous available period.
They are trend indicators, not forecasts.

## Part 2: Late-delivery analysis

Each order item has a `late_delivery_risk` value:

- `1` or `TRUE`: considered late;
- `0` or `FALSE`: not considered late.

The late-delivery rate is:

`late items / all items`

We calculate it for combinations of region, shipping mode, and category.

The **late-risk index** compares each group with the overall dataset:

`group late rate / overall late rate`

- index above 1: worse than average;
- index equal to 1: approximately average;
- index below 1: better than average.

We also consider volume. A tiny group can have a high rate but affect very few
orders. A high-volume group with an above-average late rate is usually more
important operationally.

## Part 3: Fill-rate and lead-time proxies

The dataset does not contain inventory levels, stockouts, or fulfilled versus
requested quantities. Therefore, a true fill rate cannot be calculated.

Instead, the project clearly labels **on-time fulfillment rate** as a proxy:

`1 - late-delivery rate`

This is useful for delivery performance, but it should never be presented as a
true inventory fill rate.

Lead time compares:

- actual shipping days;
- scheduled or promised shipping days.

The lead-time variance is:

`actual days - scheduled days`

- positive: shipment took longer than promised;
- zero: shipment matched the promise;
- negative: shipment arrived faster than promised.

The standard deviation of this difference measures consistency. A larger value
means shipping performance is less predictable.

## Files in this module

- `warehouse/vw_demand_monthly.sql`: monthly demand and trends.
- `warehouse/vw_demand_weekly.sql`: weekly demand and trends.
- `warehouse/vw_supply_chain_delivery.sql`: delivery and lead-time metrics.
- `analytics/supply_chain/demand_analysis.py`: demand summaries and chart.
- `analytics/supply_chain/delivery_analysis.py`: delivery summaries and chart.

The SQL performs warehouse-side calculations. The Python scripts retrieve the
smaller results, print interpretable summaries, and create presentation-ready
charts.
