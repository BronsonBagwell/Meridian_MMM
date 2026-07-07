# Executive Summary — Meridian MMM Portfolio

**Timeframe analyzed:** 2022-01-03 through 2024-02-05 (110 weekly observations)  
**Objective:** Demonstrate how an MMM workflow can move from data to budget recommendations using a Meridian-oriented setup that is credible, runnable, and easy to review.

## Bottom line
This portfolio piece tells a simple story:
- the deterministic pipeline fits the synthetic dataset cleanly (**~2.1% in-sample MAPE, ~2.9% MAPE on a held-out final ~20% of weeks**)
- **Affiliate** is the clearest scale opportunity (**~3.88x modeled ROI**, roughly 24.7k incremental conversions)
- **Search** and **Social** contribute, but modestly (**~0.19x ROI** each)
- **TV** and **Video** show **no measurable incremental lift in this model** — their budgets should be challenged before funding, not protected by habit

That is the kind of output a marketing lead can actually do something with.

## What a stakeholder should take away
1. **Scale the obvious winner.** Affiliate is delivering the strongest modeled return on the smallest weekly spend base.
2. **Keep demand capture honest.** Search still contributes, but at a modest modeled return, so it should be monitored rather than blindly defended.
3. **Pressure-test upper funnel spend.** TV and Video show no measurable incremental lift in this model and are not earning blind confidence in this scenario.
4. **Use Meridian as the serious next step.** The repo already proves the official package runs on the same dataset, so the path to a fuller Bayesian workflow is real rather than hypothetical.

## Headline metrics
- **Model fit:** 2.11% in-sample MAPE; 2.94% MAPE on the final 22 weeks when the model is refit on only the first 88 weeks (time-based holdout)
- **Best ROI:** Affiliate at ~3.88x (~24.7k incremental conversions)
- **Modest contributors:** Search at ~0.19x, Social at ~0.19x
- **No measurable lift:** Video at 0.00x, TV at 0.00x once media effects are constrained non-negative

## Recommended actions
- Increase Affiliate budget in controlled increments and monitor marginal ROI rather than assuming linear scale.
- Hold Search and Social budgets steady and watch marginal returns, since their modeled ROI is modest rather than compelling.
- Challenge TV and Video before funding: they show no measurable incremental lift in this model, so reallocate a test tranche into higher-performing channels before approving more top-of-funnel budget.
- Upgrade the workflow from synthetic demo data to a live weekly feed so the same structure can support real planning.

## Why this artifact is credible
A lot of MMM portfolio projects are either too shallow to trust or too clunky to review. This one is built to avoid both problems.

It includes:
- a **fast deterministic pipeline** for charts, metrics, and business recommendations
- a **working official Meridian runtime check** on the same dataset
- explicit documentation of what is simplified, what is real, and what would change in production

## Important limitations
- The dataset is synthetic, so the outputs are illustrative rather than decision-grade.
- The included Meridian path is intentionally lightweight by default; it proves runtime viability, not full production posterior rigor.
- The data is national rather than geo-level, so it does not showcase the full hierarchical power of Meridian.

## Why this matters as a portfolio piece
The point is not to pretend this is a finished enterprise MMM deployment. The point is to show the harder thing: sound problem framing, believable analysis structure, clean communication, and an honest bridge into a real Bayesian framework.

That is usually more useful than a repo full of impressive-looking math and zero decision clarity.
