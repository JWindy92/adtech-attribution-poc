# Attribution Approaches in AdTech

## 1. Multi-Touch Attribution (MTA)

**What it is:** User-level event tracking to credit touchpoints along conversion path

**Data required:**
- Individual impression events (user_id, ad_id, timestamp, channel)
- Conversion events (user_id, conversion_id, timestamp, value)
- Identity graph to link events

**How it works:**
1. User sees CTV ad → log event
2. User clicks Search ad → log event  
3. User converts → log event
4. Match all events via user_id
5. Apply attribution model (last-touch, linear, algorithmic)

**Example output:**
```
Conversion #123 ($500 value):
- CTV ad (Day 1): 20% credit
- Social ad (Day 3): 30% credit
- Search ad (Day 7): 50% credit (last-touch)
```

**Pros:**
- Granular touchpoint-level insights
- Works well for digital channels with tracking
- Can optimize specific campaigns/creatives

**Cons:**
- Requires user-level tracking (privacy concerns)
- Doesn't work for cookieless/untrackable channels (Linear TV, OOH)
- Correlation ≠ causation (user might have converted anyway)
- Cookie deprecation kills it

**Used by:** Clarivoy, Google Analytics, Adobe Analytics

---

## 2. Media Mix Modeling (MMM)

**What it is:** Statistical modeling of aggregate spend-to-outcome relationships

**Data required:**
- Weekly/daily spend by channel (aggregate)
- Weekly/daily conversions (aggregate)
- Optional: seasonality, promotions, competitor activity

**How it works:**
1. Collect weeks of aggregate data (spend + conversions)
2. Apply transformations (adstock, saturation)
3. Regression model estimates each channel's incremental contribution
4. Bayesian approach quantifies uncertainty

**Example output:**
```
Channel Contributions (95% credible interval):
- CTV: 30-40% of conversions
- Linear TV: 20-30%
- Search: 15-20%
- Social: 10-15%
```

**Pros:**
- Privacy-safe (no user tracking)
- Works for ALL channels (TV, radio, OOH, digital)
- Estimates true incrementality
- Post-cookie ready

**Cons:**
- Requires weeks/months of data
- Less granular (channel-level, not campaign-level)
- Assumes stable relationships
- Can't optimize individual ads

**Used by:** Nielsen, Analytic Partners, our POC

---

## 3. Incrementality Testing

**What it is:** Controlled experiments to measure true causal lift

**Methods:**
- **Geo Holdout:** Run ads in market A, not in market B, compare
- **User Holdout:** Target group A, hold out group B, compare
- **Pre/Post:** Measure conversions before/after campaign

**Example:**
```
Test: CTV campaign incrementality
- Treatment group (exposed): 1,200 conversions
- Control group (not exposed): 1,000 conversions
- Incremental lift: 20% (200 conversions)
```

**Pros:**
- Gold standard (true causality)
- Validates other attribution methods
- Can measure brand lift, not just conversions

**Cons:**
- Expensive (requires leaving money on table)
- Takes time (weeks to run tests)
- Not real-time

**Used by:** Meta, Google (for validation), enterprise brands

---

## 4. Unified Attribution (Emerging)

**What it is:** Combines MTA + MMM + Incrementality for complete view

**How it works:**
- MTA for digital lower-funnel (Search, Social clicks)
- MMM for upper-funnel (CTV, Linear TV, brand awareness)
- Incrementality tests to calibrate both
- Unified budget optimization across all

**Example:**
```
Unified view:
- Search (MTA): $50/conversion, high confidence
- CTV (MMM): $75/conversion ± $15, medium confidence
- Linear TV (MMM): $100/conversion ± $25, validated via geo test
→ Shift $200K from Linear TV to CTV
```

**Pros:**
- Best of all worlds
- Privacy-safe + granular where possible
- Validated incrementality

**Cons:**
- Complex to implement
- Requires data infrastructure
- Few vendors do this well

---

## Where This Project Fits

**Focus:** MMM (Media Mix Modeling)  
**Why:** Privacy-safe, cross-channel, incrementality-focused  
**Innovation:** Bayesian approach with uncertainty quantification  
**Comparison:** Will contrast spend-proportional (naive) vs Bayesian MMM (sophisticated)

**Future expansion:**
- Event stream simulation (show MTA data landscape)
- Incrementality testing framework
- Unified attribution prototype
