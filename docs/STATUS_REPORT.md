# Marketing Mix Model Analysis Report

## Executive Summary

Your R² of **0.75** is quite strong for media modeling, meaning your variables explain 75% of the variation in conversions.

---

## 1. Channel Performance: Winners and Losers

### 🏆 Search - Your MVP
- **Marginal CPA:** $34.03 (most efficient by far)
- **P-value:** 0.000 (highly significant)
- **Interpretation:** The model is extremely confident in this result. Search is your most cost-effective channel.

### 📺 Linear TV vs. CTV
- **Linear TV CPA:** $103
- **CTV CPA:** $168
- **Status:** Both statistically significant and reliable
- **Insight:** Linear TV currently outperforms CTV in efficiency, though both are solid "workhorse" channels.

### ⚠️ Social - Problem Area
- **Marginal CPA:** $2,380 (significantly higher than target)
- **P-value:** 0.945 (not statistically significant)
- **Interpretation:** The model cannot find a consistent relationship between social spend and conversions. This appears to be noise rather than a real effect.

---

## 2. Baseline Conversions

**Intercept (const):** 380.45 conversions/week

This suggests that without paid advertising, you'd still generate ~380 conversions per week from organic sources (SEO, direct traffic, brand word-of-mouth).

**Note:** P-value of 0.218 indicates high variability in baseline conversions, likely due to seasonal fluctuations.

---

## 3. Model Diagnostics: Warning Signs

### Multicollinearity (Condition Number: 9.91e+03)
- **Issue:** Your spend channels move together (e.g., when CTV increases, Linear TV often increases too)
- **Impact:** Makes it harder to isolate which channel truly caused conversions
- **Severity:** Moderate concern

### Autocorrelation (Durbin-Watson: 0.317)
- **Ideal Score:** 2.0
- **Your Score:** 0.317 (very low)
- **Interpretation:** Model errors are highly correlated week-to-week
- **Root Cause:** Likely seasonal trends (holiday peaks, summer slowdowns) not yet captured

---

## 4. Next Steps: Making This "Board-Room Ready"

To improve model accuracy and clean up results, the recommended next step is **adding seasonality variables.**

### Approach:
Add dummy variables for months or a simple trend line to capture seasonal patterns without changing the core dollar-math.

### Expected Improvements:
- ✅ Better Durbin-Watson score
- ✅ More accurate CPAs
- ✅ Clearer picture of social spend impact
- ✅ Model explainability for stakeholders is quite strong for media modeling, meaning your variables explain 75% of the variation in conversions.
Here is the "translation" of your regression summary into business insights:
1. The Winners and Losers
Search is your MVP: With a Marginal CPA of $34.03, Search is incredibly efficient. Its P-value is 0.000 (highly significant), meaning the model is very confident in this result.
Linear TV vs. CTV:
Linear TV ($103 CPA) is currently outperforming CTV ($168 CPA) in terms of efficiency.
Both are statistically significant (
), so these are reliable "workhorse" channels for you.
Social is a Problem: The Marginal CPA of $2,380 is likely much higher than your target. Furthermore, the P-value is 0.945, which means the model can't find a consistent relationship between Social spend and conversions. It’s effectively "noise" right now.
2. The "Base" Conversions
const = 380.45: This suggests that if you turned off all these paid ads, you would still get roughly 380 conversions per week from organic sources (SEO, direct traffic, brand word-of-mouth).
Note: The P-value for the constant is 0.218, which is a bit high. This usually happens when the "Base" fluctuates a lot or when media spend is very consistent (making it hard for the model to see what happens when spend is zero).
3. Warning Signs (The "Cond. No." and Durbin-Watson)
The model gave you two "yellow flags" in the notes:
Multicollinearity (Cond. No. 9.91e+03): This suggests some of your spend channels move together (e.g., when you increase CTV, you also increase Linear TV). This makes it harder for the model to tell exactly which one caused the conversion.
Autocorrelation (Durbin-Watson 0.317): A "perfect" score is 2.0. Your score of 0.317 is very low, meaning your model has "serial correlation."
Translation: The error you make this week is very similar to the error you made last week. This usually means there is a seasonal trend (like a holiday peak or a slow summer) that the model isn't seeing yet.
How to make this model "Board-Room Ready"
To fix that Durbin-Watson score and get more accurate CPAs, the next logical step is usually to add Seasonality.
The easiest way to do this without changing your dollar-math is to add "dummy variables" for months or a simple trend line.
Would you like me to show you how to add a "Month" variable to see if that cleans up the Social Spend results and the Durbin-Watson score?


```
                            OLS Regression Results                            
==============================================================================
Dep. Variable:            conversions   R-squared:                       0.750
Model:                            OLS   Adj. R-squared:                  0.740
Method:                 Least Squares   F-statistic:                     74.23
Date:                Sun, 01 Mar 2026   Prob (F-statistic):           6.06e-29
Time:                        17:54:48   Log-Likelihood:                -670.73
No. Observations:                 104   AIC:                             1351.
Df Residuals:                      99   BIC:                             1365.
Df Model:                           4                                         
Covariance Type:            nonrobust                                         
=============================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
---------------------------------------------------------------------------------------------
const                       380.4531    306.576      1.241      0.218    -227.859     988.765
ctv_spend_saturated           3.3415      1.279      2.612      0.010       0.803       5.880
social_spend_saturated        0.1201      1.752      0.069      0.945      -3.357       3.597
search_spend_saturated       11.1205      1.508      7.373      0.000       8.128      14.113
linear_tv_spend_saturated     6.4966      1.274      5.101      0.000       3.969       9.024
==============================================================================
Omnibus:                        6.170   Durbin-Watson:                   0.317
Prob(Omnibus):                  0.046   Jarque-Bera (JB):                3.024
Skew:                           0.140   Prob(JB):                        0.221
Kurtosis:                       2.213   Cond. No.                     9.91e+03
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[2] The condition number is large, 9.91e+03. This might indicate that there are
strong multicollinearity or other numerical problems.
const                        380.453108
ctv_spend_saturated            3.341494
social_spend_saturated         0.120107
search_spend_saturated        11.120502
linear_tv_spend_saturated      6.496636
dtype: float64
At an average weekly spend of $79,250.12:
Each additional $1 is expected to bring 0.005935 conversions.
Your Marginal CPA is: $168.50
At an average weekly spend of $20,442.18:
Each additional $1 is expected to bring 0.000420 conversions.
Your Marginal CPA is: $2380.82
At an average weekly spend of $35,797.45:
Each additional $1 is expected to bring 0.029388 conversions.
Your Marginal CPA is: $34.03
At an average weekly spend of $111,975.37:
Each additional $1 is expected to bring 0.009707 conversions.
Your Marginal CPA is: $103.02
```