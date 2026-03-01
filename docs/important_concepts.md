# Important Concepts: Alpha, Beta, and Gamma

## Alpha: The Steepness Parameter

**Definition:** Alpha controls how sharply a marketing channel responds to spending increases early on. It determines the curve's steepness in the Hill saturation function.

**Mathematical role:** In the Hill equation `x^alpha / (x^alpha + gamma^alpha)`, alpha is the exponent that controls the shape of the response curve.

### What happens when Alpha goes UP:
- The channel shows a **sharper, more dramatic response** to initial spending
- Early spend produces bigger returns (steep climb)
- The curve plateaus more aggressively (hits saturation faster)
- Good for: Channels that are "all or nothing"

**Adtech Example:** A search campaign with high alpha (2.0) might see huge conversion jumps from $0 to $50K spend, then level off. Every dollar from $0-$50K is valuable, but dollars above that don't help much.

### What happens when Alpha goes DOWN:
- The channel shows **gradual, steady response** to spending increases
- Spend increases produce smaller but more consistent returns
- The curve climbs more gently toward saturation
- Good for: Channels with steady, predictable returns

**Adtech Example:** A brand awareness display campaign with low alpha (0.5) might show consistent but gradual conversion increases. Spending $100K produces twice what $50K produces, which produces twice what $25K produces.

---

## Beta: The Channel's Impact Coefficient

**Definition:** Beta represents the **strength of a channel's influence** on conversions. It's derived from the Bayesian MMM model and quantifies how much each channel contributes to driving customer conversions.

**Mathematical role:** Beta is the regression coefficient in the Bayesian model. Higher beta = stronger direct impact on conversions.

### What happens when Beta goes UP:
- The channel becomes **more powerful and valuable** for driving conversions
- The optimizer allocates more budget to this channel (assuming capacity)
- This channel's contribution to overall campaign ROI increases
- Good for: High-performing channels

**Adtech Example:** Your Social Media channel has beta = 3,700, while Linear TV has beta = 860. Social (3,700) is 4x more powerful at driving conversions. The optimizer should heavily favor social spending.

### What happens when Beta goes DOWN:
- The channel becomes **weaker and less valuable** for driving conversions
- The optimizer allocates less budget to this channel
- This channel contributes less to overall campaign ROI
- Good for: Low-performing or niche channels

**Adtech Example:** If your Search campaign's beta drops from 6,200 to 3,100 (perhaps because the market is saturated), it's now half as effective. The optimizer should shift budget away from search toward better-performing channels.

### Why Beta Matters in the Fix:
The bug fix changes the objective function to use beta instead of attributed_conversions. This makes sense because:
- **Beta is variable per channel** (each channel has different strength)
- **Attributed conversions are fixed** (they don't change with your allocation)
- The optimizer needs to see that allocating to high-beta channels rewards you with more conversions. Using beta gives it that signal.

---

## Gamma: The Half-Saturation Point

**Definition:** Gamma is the spend level at which a marketing channel reaches **50% of its maximum effectiveness**. It's the "sweet spot" threshold where moderate saturation effects begin to matter.

**Mathematical role:** In the Hill equation, gamma is the parameter where the function equals 0.5 (50% effectiveness). It's channel-specific and typically measured in dollars.

### What happens when Gamma goes UP:
- The channel needs **more spending** to reach its half-saturation point
- The channel is **efficient at high spend levels** (doesn't saturate easily)
- Early spending returns are more modest, but the channel scales well
- Good for: High-volume channels that can absorb large budgets profitably

**Adtech Example:** A Search channel with high gamma ($600K) means:
- At $300K spend, you're still below 50% saturation
- At $600K spend, you hit 50% of max effectiveness
- At $1.2M spend, you're nearing maximum effectiveness
- This channel can absorb a multi-million dollar budget

### What happens when Gamma goes DOWN:
- The channel reaches its half-saturation point **quickly with lower spend**
- The channel **saturates rapidly** (diminishing returns kick in early)
- High spend on this channel hits strong diminishing returns
- Good for: Niche, targeted channels with limited capacity

**Adtech Example:** A Retargeting campaign with low gamma ($50K) means:
- At $25K spend, you're below 50% saturation
- At $50K spend, you hit 50% of max effectiveness
- Above $50K, returns diminish sharply (limited audience to reach)
- This channel works best with a capped budget

### Real-World Implication:
If gamma values across your channels are:
- CTV: $465K (needs moderate spend to saturate)
- Social: $566K (needs higher spend to saturate)
- Search: $481K (needs moderate spend to saturate)
- Linear TV: $444K (saturates quickest)

Then the optimizer knows that CTV and Social can absorb bigger budgets sustainably, while Linear TV should get more modest allocations before hitting diminishing returns.

---

## How They Work Together: A Practical Example

Imagine three channels with these parameters:

| Channel | Alpha | Beta | Gamma |
|---------|-------|------|-------|
| Search | 1.10 | 6,190 | $481K |
| Social | 1.03 | 3,722 | $566K |
| Display | 0.70 | 800 | $250K |

**What this tells the optimizer:**

1. **Search** (high beta + moderate gamma): Powerful channel, moderate saturation. Allocate significant budget here.

2. **Social** (moderate beta + high gamma): Less powerful than search, but scales well to high spend. Good for secondary allocation.

3. **Display** (low beta + low gamma): Weak channel that saturates quickly. Allocate minimally.

The optimizer should recommend something like: Prioritize Search 🎯, grow Social 📈, limit Display 🛑.

---

## Glossary Cheat Sheet

| Parameter | What It Measures | Up = | Down = |
|-----------|------------------|------|--------|
| **Alpha** | Response curve steepness | Sharp response, quick plateau | Gradual response, slow plateau |
| **Beta** | Channel strength/power | More valuable for conversions | Less valuable for conversions |
| **Gamma** | Saturation threshold (in $) | Channel scales well | Channel saturates quickly |
