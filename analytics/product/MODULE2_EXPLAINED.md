# Module 2 Explained — Product Analytics (in plain English)

This document explains everything we did in Module 2, step by step, in simple
language — no jargon left unexplained. Read this before looking at any code.

---

## The big picture

We have a dataset of ~180,000 retail orders from ~20,000 customers. Module 2
asks three questions about those customers:

1. **Who are our best/worst customers?** → RFM Segmentation
2. **Do customers keep coming back over time?** → Cohort & Retention Analysis
3. **Which customers have we lost, and why?** → Churn Analysis

Each one uses a different, standard technique that real companies use. None
of this is "AI" or machine learning in the deep-learning sense — it's
statistics and bookkeeping applied carefully.

---

## Part 1: RFM Segmentation

### What problem is this solving?

Imagine you have 20,000 customers. You can't treat them all the same — some
spend a lot and shop often, others bought once two years ago and vanished.
RFM is a 40-year-old marketing technique (predates computers, originally
done with paper records) that buckets customers into groups based on three
numbers:

- **R = Recency** — how many days ago was their last order? (Lower is better
  — a customer who ordered yesterday is more "alive" than one who ordered
  3 years ago.)
- **F = Frequency** — how many orders have they placed, total? (Higher is
  better — more orders means more loyalty.)
- **M = Monetary** — how much money have they spent with us in total?
  (Higher is better — obviously, big spenders matter more.)

### How do we turn 3 numbers into a "score"?

For each of the three numbers, we sort ALL 20,000 customers from worst to
best on that one number, then chop them into 5 equal-sized buckets (this is
called a **quintile** — "quint" = 5). Bucket 5 = best 20% of customers on
that number, bucket 1 = worst 20%.

So every customer gets 3 scores, each from 1 to 5:
- An R-score (1-5)
- An F-score (1-5)
- An M-score (1-5)

A customer with R=5, F=5, M=5 ordered recently, orders a lot, and spends a
lot — that's about as good as a customer gets.

### Why "quintiles" specifically, and why in SQL?

Splitting into 5 equal groups is just the traditional convention for RFM —
it's specific enough to be useful, not so granular that bucket sizes get
noisy. We computed it in SQL (inside Snowflake, the cloud database) instead
of in Python, because:
- The database already has all 180K order rows; no need to download them
  into a notebook just to do arithmetic.
- SQL has a built-in command for exactly this job: `NTILE(5)`, which means
  "sort everyone and split them into 5 even groups." One line of SQL does
  what would otherwise take several lines of pandas code.

### How do we turn 3 scores into a single label?

We wrote simple rules (in code, called a `CASE WHEN` statement — basically
a stack of if/else checks) like:
- If R, F, and M are ALL high (4 or 5) → label them **"Champions"**
- If R and F are decently high → **"Loyal"**
- If R is high but F is low (came back recently but rarely orders) →
  **"New / Promising"**
- If R is low but F is high (used to order a lot, but hasn't lately) →
  **"At Risk"**
- If everything is low → **"Lost"**
- Anything else → **"Needs Attention"**

These are just business-friendly names slapped onto the numbers so a
marketing person can read "At Risk" instead of "R=2, F=4, M=3."

### What did we actually find?

| Segment | # Customers | Meaning |
|---|---|---|
| At Risk | 7,765 | Used to order a lot, haven't lately — worth a win-back email |
| New / Promising | 7,663 | Recent first-timers, haven't proven loyalty yet |
| Loyal | 4,625 | Solid, consistent repeat customers |
| Needs Attention | 364 | Mixed signals, no clear pattern |
| Lost | 235 | Long gone, low value — probably not worth chasing |

**Interesting wrinkle:** nobody landed in "Champions" (the absolute best
tier). That's not a mistake — it's because the top 20% on recency, the top
20% on frequency, and the top 20% on spending happen to be *different sets
of people* in this dataset. There's no rule that says the same customers
must be best at all three things at once, and here, none were.

---

## Part 2: Cohort & Retention Analysis

### What problem is this solving?

This answers: "If I get 100 new customers in January, how many of them are
still buying from me 3 months later? 6 months later?" This is the exact
question subscription companies (Netflix, gyms, SaaS products) live and die
by, applied here to a retail dataset.

### What's a "cohort"?

A **cohort** just means "a group of customers who all started at the same
time." We define a customer's cohort as the *month of their very first
order*. So everyone who placed their first-ever order in January 2015 is
the "January 2015 cohort," everyone whose first order was in February 2015
is the "February 2015 cohort," etc.

### How do we measure "retention"?

For each cohort, we look at every following month and count: out of the
people in that cohort, how many placed ANOTHER order that month? We express
this as a percentage of the original group size.

We call "month 0" the cohort's starting month (100% by definition, since
that's literally when they had their first order). "Month 1" is one month
later, "month 2" is two months later, and so on. The end result is a grid
(a **cohort retention matrix**) — rows are cohorts (Jan 2015, Feb 2015...),
columns are "months since joining" (0, 1, 2, 3...), and each cell is a
retention percentage. We then color this grid like a heatmap (darker blue =
higher retention) so patterns jump out visually instead of reading raw
numbers.

### What did we find?

Retention drops hard after month 0 (makes sense — most people order once
and don't come back right away), then **stabilizes around 11-17%** for
every later month, for almost every cohort. In plain terms: roughly 1 in 7
or 8 customers from any given starting month will place another order in
any later given month, and that rate doesn't really improve or worsen over
the company's lifetime — it's a flat, structural quality of this customer
base.

**A data quirk we flagged:** cohort sizes (how many *new* customers joined
each month) suddenly jump from a few hundred to over 2,000 starting around
October 2017. That's too sudden to be real organic growth — it's much more
likely an artifact of how this practice dataset was put together (e.g. a
big batch of data got added near the end), not a real business event. We
call this out explicitly so nobody mistakes it for "the company suddenly
got way better at acquiring customers in Oct 2017."

---

## Part 3: Churn Flag & Drivers

### What problem is this solving?

"Churn" means a customer has effectively stopped being a customer. This
part (a) decides a simple rule for *when* someone counts as churned, and
(b) tries to explain *what kind* of customer is more likely to churn.

### The churn rule

We defined churn as: **no order in the last 90 days**, counting backward
from the most recent date anywhere in the dataset. This is a deliberately
simple, fixed rule (not a machine-learning prediction) — it's just a
yes/no flag based on one number (days since last order > 90).

**Result:** 69.8% of customers are flagged as churned by this definition.
That's a high number, but it's a direct consequence of this being a
finite, several-year-old dataset — of course most customers who only
bought once years ago are now "churned" relative to the dataset's end date.

### Trying to explain WHY customers churn (the interesting part)

The project plan suggested an optional next step: build a model that
explains which customer traits correlate with churning. We used **logistic
regression** — a standard statistics technique for predicting a yes/no
outcome (churned or not) from a few input numbers, and telling you how much
each input matters.

This is where it got genuinely interesting, because our first three
attempts broke, and figuring out *why* taught us something real about the
data:

#### Attempt 1: Include "number of orders" as a factor — broke

We tried using order count, total spend, average order size, and customer
type as inputs. The model refused to settle on an answer (technically:
"failed to converge") and spat out absurd numbers.

**Why it broke:** we discovered that in this dataset, literally **100% of
customers with 2 or more orders are churned**, while only ~30% of one-time
customers are churned. When one input variable predicts the outcome almost
perfectly, the math behind logistic regression breaks down (it's called
"separation" — imagine trying to draw a line that perfectly divides two
groups; the model tries to make the slope infinitely steep, which computers
can't represent). So this wasn't a coding bug — it was the model honestly
telling us "this input is too powerful, I can't process it normally."

The reason this is true here: most customers who order more than once do so
in a short burst close to their first order, and basically nobody in this
dataset continues ordering all the way up to the dataset's final month. So
mathematically, having multiple orders almost guarantees your last order
happened well over 90 days before the dataset ends.

#### Attempt 2: Try a "regularized" fix while keeping order count in — also unusable

There's a standard mathematical trick for this exact "separation" problem
(adding a penalty that discourages extreme values, called L1
regularization). We tried it. It technically ran without crashing, but the
results were meaningless — confidence ranges so wide they were useless
(think "this effect is somewhere between -1000% and +1000%," which tells
you nothing).

#### Attempt 3: Remove order count, but keep BOTH total spend and average order value — broke differently

Without order count, we tried total money spent and average amount per
order together. This broke too, but for a completely different reason:
**these two numbers are nearly identical for ~70% of customers** — anyone
who placed exactly 1 order has total spend = average order value, since
there's only one order to average. Feeding a model two columns that are
basically copies of each other (called **multicollinearity**) confuses it
in the same way asking "how much does height matter vs. height-in-inches"
would — the model can't tell the two apart, so it gives one a huge positive
number and the other a huge negative number that cancel out.

#### Final, working model

We removed order count (report it separately as a plain percentage, since
that's clearer anyway) and removed total spend (kept only average order
value, dropping its redundant twin). With just average order value + 
customer type as inputs, the model finally ran cleanly and gave trustworthy
numbers:

- **Average order value** has a small but real effect: customers who spend
  more per order are *very slightly* more likely to churn. (Statistically
  significant, meaning this isn't just random noise — but the actual size
  of the effect is small.)
- **Customer type** (Consumer vs. Corporate vs. Home Office) makes
  basically no difference to churn likelihood.

### The big lesson from this whole exercise

When a statistics model "fails to converge" or gives crazy numbers, it's
not always a code bug — it's often the model trying to tell you something
true about the data:
1. One input might be *too* predictive (separation) — usually means that
   input is basically a disguised version of the answer itself.
2. Two inputs might be measuring almost the same thing (collinearity) —
   the fix is to keep only one of them.

---

## Where to see this for yourself

- The actual SQL queries that compute all the scores/flags live in
  `warehouse/vw_rfm_scores.sql`, `warehouse/vw_cohort_orders.sql`,
  `warehouse/vw_churn_flag.sql`.
- The Python scripts that run the analysis and make charts are in
  `analytics/product/rfm_segmentation.py`, `cohort_retention.py`,
  `churn_analysis.py`.
- The full step-by-step notebook (including the broken attempts, shown
  live) is `analytics/product/module2_walkthrough.ipynb`.
