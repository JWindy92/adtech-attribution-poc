# Optimizer Test Suite Glossary

## Hill Saturation Function Tests

These tests verify that the Hill saturation function correctly models how marketing channels show **diminishing returns** as you spend more money on them.

### test_hill_saturation_zero_input
**What it tests:** When you don't spend any money on a channel, you get zero results back.

**Real-world analogy:** If you allocate $0 to a social media campaign, you won't get any conversions from it.

---

### test_hill_saturation_half_saturation_point
**What it tests:** Each channel has a "sweet spot" spend level (called gamma). At this spend level, you're getting 50% of the maximum possible benefit from that channel.

**Real-world analogy:** If a social media channel has a sweet spot of $100K, then spending $100K gets you halfway to the maximum benefit you could ever achieve, no matter how much more you spend.

---

### test_hill_saturation_monotonic_increase
**What it tests:** Spending more money always produces more results. You never reach a point where spending additional dollars actually makes things worse.

**Real-world analogy:** Whether you're spending $1K, $10K, or $100K on a channel, more spend always yields more conversions (even if each additional dollar gives diminishing returns).

---

### test_hill_saturation_bounded_zero_one
**What it tests:** The "saturation factor" representing diminishing returns always stays between 0% and 100% effectiveness.

**Real-world analogy:** A channel can theoretically reach 100% saturation (maximum possible effectiveness), but never exceed it. Similarly, it can't go below 0%.

---

### test_hill_saturation_large_spend_approaches_one
**What it tests:** If you spend an enormous amount of money on a channel, the saturation effect approaches its maximum (very close to 100%).

**Real-world analogy:** There's a limit to how much impact you can get from a single channel. Eventually, with massive spending, you hit a ceiling where additional money barely moves the needle.

---

### test_hill_saturation_alpha_affects_steepness
**What it tests:** Different channels have different "curves" that determine how quickly they hit diminishing returns. The alpha parameter controls how sharp this curve is.

**Real-world analogy:** Some channels (like search) respond sharply to spend increases early on but then plateau quickly. Other channels (like broad display) respond more gradually.

---

### test_hill_saturation_gamma_affects_shape
**What it tests:** The "sweet spot" spend level (gamma) is different for each channel. Some channels are efficient at lower spend levels, others need higher spend to hit their sweet spot.

**Real-world analogy:** Email marketing might reach its sweet spot at $50K, while TV advertising might need $1M to reach its sweet spot. Different channels, different efficiency profiles.

---

### test_hill_saturation_vectorized
**What it tests:** The Hill saturation function can process multiple channels simultaneously (as an array), not just one at a time.

**Real-world analogy:** You can calculate the saturation effect for all 4 of your marketing channels (CTV, Social, Search, Linear TV) in one calculation instead of doing them one-by-one.

---

### test_hill_saturation_symmetry_with_parameters
**What it tests:** The function is deterministic and reliable. If you ask it the same question twice, you get the same answer (no randomness).

**Real-world analogy:** Your marketing model should be predictable. Running the same optimization twice with the same data should give you the same budget recommendations.

---

## Saturation Objective Function Tests

These tests verify that the optimization objective function correctly **scores** different budget allocation strategies, so the optimizer can tell which allocations are good and which are bad.

### test_objective_different_allocations_produce_different_values
**What it tests:** Different ways of splitting your budget should get different scores. An allocation of [$5K, $5K] should score differently than [$7K, $3K].

**Real-world analogy:** If you split your budget equally between channels, you should get a different performance score than if you favor one channel over another.

---

### test_objective_higher_allocation_to_high_return_channel_improves_objective
**What it tests:** If you move budget from a lower-performing channel to a higher-performing channel, your overall score should improve.

**Real-world analogy:** If Social Media converts customers at a 2x better rate than Display Ads, then moving $2K from Display to Social should boost your overall campaign performance score.

**Status:** ❌ **CURRENTLY FAILING** - This is the bug we're hunting!

---

### test_objective_all_zero_allocation
**What it tests:** If you allocate $0 to all channels, your optimization score is $0 (no budget, no results).

**Real-world analogy:** If you run no campaigns, you generate no conversions. The score is zero.

---

### test_objective_respects_saturation_differences
**What it tests:** Channels with different saturation curves should reward different budget splits. A channel that saturates quickly shouldn't score the same as one that grows more slowly.

**Real-world analogy:** Search (quick saturation) and Display (slow saturation) have different optimal spending levels. The objective function should recognize this and score allocations differently for each.

---

### test_objective_increases_with_higher_baseline_revenue
**What it tests:** A channel that naturally produces more conversions (higher baseline revenue) should contribute more to your overall score when you allocate money to it.

**Real-world analogy:** If Social Media typically delivers 10,000 conversions per million spent, while Search delivers 5,000 per million spent, then allocating an extra dollar to Social should boost your overall score more than allocating to Search.

