# Module 3 Explained — Supply Chain Analytics and Demand Forecasting

## The complete story

Module 3 answers four connected questions:

1. What products are customers buying, where, and when?
2. Which deliveries are most likely to arrive late?
3. How closely does actual shipping time match the promised time?
4. What might weekly category demand look like over the next 12 weeks?

The first three questions describe historical operations. The fourth adds one carefully evaluated prediction task. Inventory optimization remains excluded.

## Part 1: Demand analysis

Demand means units purchased. We summarize units by product, category, region, month, and week. Three-month and four-week rolling averages smooth noisy values. Month-over-month and week-over-week percentages describe change but do not forecast.

Validated findings:

- Cleats had the highest unit demand: 73,734 units.
- Central America had the highest regional demand: 62,091 units.

Units and revenue answer different questions. A high-priced category may earn more revenue despite selling fewer units.

## Part 2: Late-delivery analysis

Late-delivery rate is `late order items / all order items`. The overall rate was approximately 54.8%, so the on-time rate was about 45.2%.

The late-risk index is `group late rate / overall late rate`:

- above 1: worse than average;
- equal to 1: approximately average;
- below 1: better than average.

We combine rate and volume because a tiny high-risk group may matter less than a moderately risky group affecting thousands of orders.

## Part 3: Lead time and the fill-rate proxy

The dataset has no stock levels, requested quantities, backorders, or stockout records. Therefore, a true inventory fill rate cannot be calculated. We use on-time fulfillment rate (`1 - late-delivery rate`) as a clearly labelled delivery proxy.

Lead-time variance is `actual shipping days - scheduled shipping days`:

- positive: slower than promised;
- zero: matched the promise;
- negative: faster than promised.

Shipping-mode averages are weighted by item volume.

Validated findings:

- First Class: 95.3% late; two actual days versus one promised.
- Second Class: 76.6% late; about four actual days versus two promised.
- Same Day: 45.7% late.
- Standard Class: 38.1% late; approximately four actual and promised days.

The faster services appear to make promises that operations cannot reliably meet. Standard Class is slower but much better calibrated.

## Part 4: Weekly demand forecasting

### Why forecasting belongs here

Supply-chain teams forecast demand to plan labor, transport, purchasing, and inventory. It naturally extends the historical demand analysis. Product Analytics remains customer-focused and does not need a prediction model merely for symmetry.

### Why forecast categories

We forecast the five highest-volume categories rather than individual products. Category series are less sparse and more stable. Product-region combinations would produce many small, unreliable time series.

### Time-based evaluation

The final 12 observed weeks are held out as test data. Earlier weeks train the models. A random split would leak future information into training and produce misleading results.

### Model 1: seasonal naive

Seasonal naive predicts each week using demand from the corresponding week one year earlier. It is the baseline. A complex model is worthwhile only if it beats a reasonable simple method.

### Model 2: Holt-Winters

Additive Holt-Winters estimates:

- level: normal demand;
- trend: upward or downward movement;
- seasonality: patterns repeated over 52 weeks.

### Metrics

MAE is the average absolute error in units. WAPE is `sum of absolute errors / sum of actual demand`. Lower is better. The lower-WAPE model is selected independently for each category.

After evaluation, the winner is fitted on all observed weeks and produces a 12-week forecast. The script saves backtest metrics, future forecasts, and one chart per category.

## Critical limitation

The dataset has a sharp volume shift near late 2017. It may represent a data-collection change rather than a real business event. Models can mistake structural changes for repeatable demand. Therefore, these forecasts demonstrate correct modeling and evaluation, but they are not production inventory recommendations.

In a real business, we would investigate the shift and add promotions, price, holidays, stockouts, and other causal features.

## Files

- `warehouse/vw_demand_monthly.sql`
- `warehouse/vw_demand_weekly.sql`
- `warehouse/vw_supply_chain_delivery.sql`
- `analytics/supply_chain/demand_analysis.py`
- `analytics/supply_chain/delivery_analysis.py`
- `analytics/supply_chain/demand_forecasting.py`
- `analytics/supply_chain/module3_walkthrough.ipynb`
