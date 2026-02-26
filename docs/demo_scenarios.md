# Demo Scenarios for Attribution Innovation Lab Presentation

**Context**: Comcast Advertising is an **ad inventory seller** (CTV, Linear TV, digital). We collect exposure data from campaigns run on our inventory. These demos show how we use internal MMM to supplement vendor attribution (Clarivoy) for **directional intelligence** to guide pricing, yield optimization, and sales enablement.

**Target Audience**: Mixed - Technical, Non-Technical, Executive  
**Time**: 5-10 minutes  
**Goal**: Show innovation, demonstrate business value (revenue growth, not cost savings), prove technical capability

**Critical Framing**: All outputs are for **INTERNAL USE ONLY** - we're not replacing advertiser-facing attribution vendors.

---

## Demo 1: "The Attribution Comparison" (RECOMMENDED - 7 min)

**Hook**: "Different attribution methods tell completely different stories about our inventory's value. Let me show you."

### Setup (30 seconds)
- Open Streamlit dashboard: `streamlit run app/dashboard_bayesian.py`
- "This simulates an advertiser spending $24.5M on our inventory over 2 years"

### Part 1: Simple Attribution (2 min)
**Switch to "Spend-Proportional (Simple)"**

**Talking Points**:
- "This is how vendor attribution often works - if advertiser spent 40% on Linear TV, assume it drove 40% of conversions"
- Point to the chart: "All channels look roughly equal - no clear winner"
- "Problem: Sales can't use this to justify premium pricing or to upsell specific inventory"

**Show the numbers**:
- Attribution %: All channels similar (~25% each)
- Cost per conversion: All similar (~$15-$30)
- "From this, we'd conclude all our inventory performs equally - but that's not actionable"

### Part 2: Bayesian MMM (3 min)
**Switch to "Bayesian MMM (Advanced)"**

**Talking Points**:
- "Now let's apply statistical modeling that accounts for TV carryover effects and diminishing returns"
- Wait for model to run (pre-cached if you've loaded it once): "Running 4,000 simulations across all possible channel mixes"
- Point to the results: "Notice how the value story completely changes"

**Show the differences**:
- Attribution %: Now varies significantly (e.g., 35% Linear TV, 20% Search, 25% CTV, 20% Social)
- Cost per conversion: Clear efficiency differences emerge
- **Expand "View Posterior Distributions"**: "These confidence intervals show our uncertainty - we're not guessing"

**Business Impact** (Seller perspective):
- Point to optimization chart: "This tells us CTV has 20% headroom before hitting diminishing returns"
- "Sales insight: We can confidently upsell CTV inventory to this advertiser"
- "Pricing insight: Linear TV shows incremental value - we can justify premium CPM"

### Part 3: The (Seller framing):
- "Simple attribution made all our inventory look the same - we'd have no upsell strategy"
- "Bayesian MMM reveals CTV has headroom, Linear TV proves incremental value despite higher CPM"
- "Sales enablement: We can now say 'Our CTV inventory drove 30% of your conversions with just 25% of spend - you're under-utilizing it'"
- "Revenue impact: Data-driven upselling vs. gut-feel negotiations"

**For Executives**: Revenue growth through strategic upselling, premium pricing justification  
**For Technical**: Posterior distributions, credible intervals, MCMC convergence  
**For Non-Technical**: "We can now prove our inventory's value with statistics, not just anecdotes"tervals, MCMC convergence  
**For Non-Technical**: Clear before/after visual impact

---

## Demo 2: "Event-Level to Aggregate - The Full Data Journey" (6 min)
on our inventory to strategic pricing decisions."

### Part 1: Event-Level Data (1.5 min)
**Run**: `python data/generate_event_stream.py`

**Talking Points**:
- "When someone sees an ad on our CTV inventory, we log an exposure event"
- Show impression event sample: "This is what we collect - user ID, timestamp, inventory type"
- "When they convert, the advertiser's vendor (Clarivoy) logs that"
- "5,000 exposures per week × 4 channels = 20,000 events/week"
- "Privacy note: Contains user IDs - Clarivoy can do user journey analysis, we can't for privacy/compliance
- "Privacy concerns: contains user IDs, exact timestamps, individual behavior"

### Part 2: Aggregation (1.5 min)
**Show the output**: weekly_aggregated_sample.csv

**Talkiinternal MMM, we aggregate to weekly summaries by inventory type"
- "Now it's just 4 numbers per week - total exposures and conversions by channel"
- "Privacy-safe: No user IDs, fully anonymized, compliance-friendly"
- "This is our sweet spot: Enough to model inventory effectiveness, not enough to identify individuals"

### Part 3: MMM → Strategic Insights (2 min)
**Run**: `python run_bayesian_mmm.py` (or show cached results)

**Talking Points** (Seller framing):
- "We model the relationship between advertiser spend on our inventory and their outcomes"
- Show attribution results: "Our CTV inventory drives 30% of conversions with 25% of spend - strong incremental value"
- Show saturation analysis: "Model shows advertiser could increase CTV spend by 20% before diminishing returns"
- "Sales action: Upsell CTV inventory with data-backed confidenceet - efficient"
- Show optimization: "Model recommends shifting $500K from Linear TV to CTV"

### Part 4: The Bridge (1 min)
**Show diagram** (create visual):
``` - Clarivoy)    Aggregate (MMM - Internal)
────────────────────────────    ──────────────────────────
✓ User journeys                 ✓ Privacy-safe  
✓ Real-time                     ✓ Cross-channel inventory view
✓ Last-click attribution        ✓ Incremental lift estimates
✗ Privacy risks                 ✗ No user-level insights
✗ Misses TV carryover           ✗ Weekly lag

        ↓
   COMPLEMENTARY, NOT COMPETITIVE
   ──────────────────────────────
   Clarivoy: Advertiser-facing attribution
   Our MMM: Internal inventory analytics
```

**Key Message**: "We're not replacing Clarivoy - we're supplementing their attribution with our own directional intelligence for pricing and yield decisions
**Key Message**: "The future isn't MTA vs. MMM - it's combining them. Our architecture is built for that."

---Advertiser Upsell Headroom Analysis" (5 min)

**Hook**: "Let's answer the question every sales rep asks: 'Can I upsell this advertiser without hitting diminishing returns?'"

### Setup
Already complete: `demos/budget_scenarios.py`

### Demo Flow (4 min)
**Run**: `python demos/budget_scenarios.py`

**Show output table**:
```
Advertiser Spend Level  | Optimal Allocation              | Marginal Efficiency
─────────────────────────────────────────────────────────────────────────────
$24.5M (Current)        | CTV: $6M, Linear: $8M, ...      | Baseline
$29.4M (+20%)           | CTV: $7.2M (+$1.2M), Linear: ...| Still efficient (upsell!)
$36.8M (+50%)           | CTV: $8M (+$2M), Search: ...    | Diminishing (caution)
```

**Talking Points** (Seller perspective):
- "At current $24.5M spend, advertiser allocation looks like this"
- "If they increase by $2M: Model says put 60% to CTV, 40% to Search - both still have headroom"
- "But at +50% ($12M more), efficiency drops - we're hitting saturation on our inventory"
- "Sales insight: Confidently upsell up to +20-30%, but beyond that, we need creative refresh or new inventory"

**Business Value**: 
- "Prevents churn - don't oversell saturated inventory"
- "Maximizes revenue - identify exact headroom for upselling"
- "Data-driven negotiations - 'Our analysis shows you can add $XM before efficiency drops'results"

**Business Value**: "Prevents wasteful overspending in saturated channels"

### Wrap-up (1 min)
- "This isn't a forecast - it's a strategic planning tool"
- "Shows exactly where marginal dollars are most effective"
- "Updates automatically as new data comes in"

---

## Demo 4: "The Innovation Roadmap - From MMM to Unified Attribution" (8 min)

**Hook**: "We didn't just build a tool - we built a platform for attribution innovation. Let me show you the roadmap."

### Part 1: Whshared with advertisers - it's internal directional intelligence"
- "Shows exactly where our inventory has capacity vs. saturation"
- "Updates automatically as campaigns run and data refreshes"
- "Sales use: Personalized upsell recommendations per advertiser
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────┐
│ Data Source │───▶│ Transformer  │───▶│    Model    │───▶│Optimizer │
│  (Pluggable)│    │  (Pluggable) │    │ (Pluggable) │    │(Pluggable)│
└─────────────┘    └──────────────┘    └─────────────┘    └──────────┘
      │                   │                    │                 │
    ┌─┴─┐              ┌──┴──┐            ┌───┴───┐        ┌────┴────┐
    │CSV│              │Adstock│          │Bayesian│       │  SciPy  │
    │DB │              │Saturate│         │  MMM   │       │Constrained│
    └───┘              └─────┘            │Spend-Prop│     └─────────┘
                                          └─────────┘
```

**Talking Points**:
- "Abstract Base Class pattern - swap any component without breaking others"
- "Today: CSV source, Bayesian model"
- "Tomorrow: Databricks source, Real-time model, Multi-objective optimizer"

### Part 2: Where the Industry Is Going (3 min)
**Open**: `docs/trends_and_approaches.md`

**Show the 8 trends** (scroll through quickly):
1. Performance Over Platforms ← **We're here**
2. End of TV vs. Digital Divide ← **Architecture supports this**
3. World Cup 2026 Real-Time
4. CTV Connects to Conversions ← **Clean rooms next**
5. Data Reawakens with Creativity
6. Collaboration Economy
7. APAC Innovation
8. Gen Z Dynamic Identity

**Talking Points**:
- "We've mapped 40 different attribution approaches across these trends"
- "Our POC covers Trend 1 (MMM) and parts of Trend 2 (unified measurement)"
- "The architecture is designed to expand into any of these"

### Part 3: Next 6 Months (2 min)
**Show roadmap** (create slide):

```
Q1 2026 ✅
├─ Bayesian MMM (DONE)
├─ Synthetic data with realistic properties (DONE)
└─ Interactive dashboard (DONE)

Q2 2026 🔨
├─ Databricks integration (real data)
├─ Creative effectiveness testing (Trend 5)
├─ Event-level + aggregate unified model (Trend 1)
└─ Clean room attribution (Trend 6)

Q3 2026 🎯
├─ Real-time attribution for live events (Trend 3)
├─ CTV household-level matching (Trend 4)
├─ A/B testing framework (incrementality)
└─ Multi-objective optimization (cost + brand lift)

Q4 2026 🚀
├─ Cross-platform journey analytics (Trend 1)
├─ Federated learning POC (Trend 6)
└─ Production readiness (scale, monitoring, CI/CD)
```

### Part 4: The Ask (1 min)
**For Executives**:
- "We've proven the technical foundation works"
- "Need access to real Databricks data to validate against Clarivoy benchmarks"
- "6-month runway to build production-grade unified attribution platform"

**For Technical**:
- "Open to collaboration - code is modular, well-documented"
- "Looking for feedback on model specifications, data schemas"

**For Non-Technical**:
- "This will answer questions like 'Should we shift budget from Linear TV to streaming?' with confidence"

---(advertiser campaigns) to validate"
- "6-month runway to build production-grade analytics for sales/pricing teams"

**For Technical**:
- "Open to collaboration - code is modular, well-documented"
- "Looking for feedback on model specifications, data schemas"

**For Sales/Business**:
- "This will answer: 'How much can I upsell before hitting diminishing returns?'"
- "Pricing team: 'What's the marginal ROI to justify premium CPM?'"
- "Yield: 'Which advertisers are over-saturated vs. have headroom?'
Channel      | Attribution % | CPC
─────────────────────────────────
CTV          | 30%          | $25
Linear TV    | 28%          | $27
Search       | 24%          | $22
Social       | 18%          | $30
```

**Talking Points**:
- "Most tools give you these numbers and call it done"
- "But what's the confidence interval? Is 30% ± 2% or ± 15%?"
- "If we can't quantify uncertainty, we can't make informed decisions"

### Part 2: Bayesian Posterior Distributions (3 min)
**Run model, expand "View Posterior Distributions"**

**Show ArviZ summary**:
```
         mean     std    hdi_3%   hdi_97%    r_hat
beta[0]  0.841   0.023   0.798    0.884     1.01
beta[1]  0.827   0.028   0.775    0.879     1.00
beta[2]  0.814   0.031   0.756    0.871     1.01
beta[3]  0.805   0.026   0.757    0.853     1.00
```

**Talking Points**:
- "Each beta is a distribution, not a point"
- "CTV coefficient: 0.84 ± 0.04 (95% credible interval: 0.80-0.88)"
- "Linear TV: 0.83 ± 0.05 - overlaps with CTV!"
- "That means we can't say with certainty that CTV is better than Linear TV"
- "But we CAN say both are better than Social (0.81 ± 0.05)"

**Show r_hat**:
- "R-hat ~1.0 means chains converged - we can trust these estimates"

### Part 3: Decision-Making Under Uncertainty (1 min)
**Create visualization** (optional - use Plotly):
- Show overlapping posterior distributions for each channel
- Highlight areas of overlap vs. separation

**Key Message**:
- "When posteriors overlap significantly: maintain current allocation or test incrementally"
- "When clearly separated: confidently shift budget"
- "Uncertainty ≠ weakness - it's intellectual honesty that prevents costly mistakes"

---

## Demo 6: "15-Second Proof of Value" (Elevator Pitch - 2 min)

**For when you have < 2 minutes**

### The Setup (15 sec)
- Open dashboard (pre-loaded)
- "We spent $24.5M last year on advertising. Question: Was it allocated optimally?"

### The Reveal (45 sec)
**Point to optimization chart**:
- "Current allocation: fairly even across channels"
- "Model recommendation: shift $2M from Linear TV to CTV and Search"
- "Expected impact: +8% conversions with same budget = $XXX,XXX in revenue"

###Advertisers spent $24.5M on our inventory last year. Question: Can we prove incremental value to justify premium pricing?"

### The Reveal (45 sec)
**Point to MMM results**:
- "Vendor attribution (Clarivoy) says last-click drove conversions"
- "Our MMM shows: Our CTV inventory drove 30% of conversions with just 25% of spend - strong incremental value"
- "Saturation analysis: Advertiser has 20% headroom to spend more on CTV before diminishing returns"

### The Differentiator (30 sec)
- "Unlike Clarivoy (last-click, advertiser-facing), this is **internal directional intelligence**"
- "Unlike CPM pricing, this quantifies **marginal ROI** of our inventory"
- "Unlike gut-feel sales, this gives **data-driven upsell confidence**"

### The Ask (30 sec)
- "Next step: Validate against real advertiser campaigns in Databricks"
- "Timeline: 2 weeks integration, 4 weeks validation, 6 weeks pilot with sales team"
- "Business impact: Revenue growth through strategic upselling, premium pricing justification1-3** (data journey - event to aggregate to optimization)  
**Minute 6-8**: **Demo 4 Part 2** (trends roadmap - show innovation vision)  
**Minute 8-10**: **Demo 1 Part 3** + Q&A (business impact, the ask)

---

## Pre-Demo Checklist

**Technical Setup** (Do before presentation):
1. ✅ Run `streamlit run app/dashboard_bayesian.py` in background (pre-cache the Bayesian model)
2. ✅ Have `python run_bayesian_mmm.py` results copied to clipboard
3. ✅ Open `docs/trends_and_approaches.md` in browser
4. ✅ Test internet connection (dashboard needs to load Plotly)
5. ✅ Close unnecessary browser tabs/applications
6. ✅ Increase terminal font size for visibility
7. ✅ Prepare 1-slide visual for architecture diagram

**Talking Points** (Print or memorize):
- **For Executives**: "Revenue growth through data-driven upselling, not cost savings. Identify $XM upsell opportunities per advertiser."
- **For Technical**: "Bayesian hierarchical regression with MCMC sampling, 4000 posterior draws, credible intervals for uncertainty"
- **For Sales**: "Tells you exactly how much you can upsell before hitting diminishing returns - personalized per advertiser"

**Backup Plans**:
- If dashboard crashes: Have screenshots ready
- If model takes too long: "This is running 4,000 simulations - let me show you cached results"
- If technical questions stump you: "Great question - let me follow up with details after"

---

## Killer Quotes to Use

**Opening**:
- "Clarivoy tells advertisers what happened - we tell ourselves what to DO (pricing, yield, upselling)"
- "We're not measuring campaigns - we're measuring our inventory's incremental value"

**Middle**:
- "The difference between CPM pricing and marginal ROI pricing is the difference between guessing and knowing"
- "Privacy regulations made user-level tracking harder - but they made aggregate MMM more valuable than ever"
- "Sales teams ask: 'Can I upsell?' This gives them a data-driven answer: 'Yes, they have 20% headroom on CTV'"

**Closing**:
- "This isn't just analytics - it's a revenue engine for strategic upselling"
- "In 2026, the question isn't 'should we use MMM?' - it's 'can we afford to sell inventory without knowing its marginal ROI?'"

---

## Post-Demo Follow-Ups

**Materials to Send**:
1. Link to dashboard (if hosted)
2. `docs/trends_and_approaches.md` - "Here are the 40 approaches we discussed"
3. `docs/stage3_bayesian_mmm.md` - Technical deep-dive
4. README.md - "Try it yourself" instructions

**Questions You'll Get**:

**"How long to get this working with our data?"**
→ "2 weeks integration + 4 weeks validation = production pilot by [date]"

**"What about seasonality / promotions / price changes?"**
→ "Great question - that's Phase 2. We add control variables to the model. Want to see the roadmap?"

**"How does this compare to what we get from Clarivoy?"**
→ "Clarivoy does MTA (event-level, last-click) for advertisers. This does MMM (aggregate, statistical) for internal strategy. Complementary, not competitive - we supplement their attribution with our own directional intelligence for pricing and yield."

**"Can we trust a model?"**
→ "Models are tools, not magic. We validate against incrementality tests and cross-check with historical data. Plus, Bayesian methods show you the uncertainty - you decide if you're confident enough to act."
