# AdTech Data Landscape

## Data Hierarchy: Event → Aggregate

```
Event Stream (millions of rows)
    ↓ aggregation
Weekly/Daily Summaries (hundreds of rows)
    ↓ statistical modeling
Attribution Results (one row per channel)
```

---

## 1. Event-Level Data (MTA Uses This)

### Impression Events
```csv
event_id,user_id,timestamp,channel,campaign_id,creative_id,spend
imp_001,user_abc,2024-01-15T14:30:00,ctv,camp_100,creative_5,0.025
imp_002,user_xyz,2024-01-15T14:31:15,search,camp_101,creative_8,1.50
imp_003,user_abc,2024-01-17T09:12:00,social,camp_102,creative_3,0.85
```

**Size:** ~10M events/week for mid-size advertiser  
**Used by:** MTA systems (Clarivoy)  
**Storage:** Databricks event tables

### Conversion Events
```csv
conversion_id,user_id,timestamp,value,source
conv_001,user_abc,2024-01-18T10:45:00,250.00,website
conv_002,user_def,2024-01-18T11:20:00,500.00,app
```

**Size:** ~50K events/week  
**Used by:** MTA systems  
**Storage:** Databricks event tables

---

## 2. Aggregate Data (MMM Uses This)

### Weekly Spend by Channel
```csv
week,ctv_spend,linear_tv_spend,search_spend,social_spend
2024-01-01,85000,115000,32000,21000
2024-01-08,82000,110000,35000,19000
2024-01-15,88000,118000,33000,22000
```

**How it's created:**
```sql
SELECT 
  DATE_TRUNC('week', timestamp) as week,
  channel,
  SUM(spend) as total_spend
FROM impressions
GROUP BY week, channel;
```

**Size:** ~50 rows/year per channel  
**Used by:** MMM systems (our POC)  
**Storage:** Aggregated tables or CSVs

### Weekly Conversions
```csv
week,conversions
2024-01-01,1850
2024-01-08,1920
2024-01-15,1780
```

**How it's created:**
```sql
SELECT 
  DATE_TRUNC('week', timestamp) as week,
  COUNT(*) as conversions
FROM conversions
GROUP BY week;
```

---

## 3. Attribution Results (Output)

### MTA Output (User-Level Attribution)
```csv
conversion_id,touchpoint_channel,touchpoint_timestamp,credit_pct
conv_001,ctv,2024-01-15T14:30:00,0.20
conv_001,social,2024-01-17T09:12:00,0.30
conv_001,search,2024-01-18T09:00:00,0.50
```

**Granularity:** Per conversion, per touchpoint  
**Used for:** Campaign optimization, creative testing

### MMM Output (Channel-Level Attribution)
```csv
channel,attribution_pct,incremental_conversions,cost_per_conversion
ctv,0.35,3250,78.50
linear_tv,0.25,2320,125.00
search,0.20,1860,45.20
social,0.20,1860,32.50
```

**Granularity:** Per channel, per time period  
**Used for:** Budget allocation, strategic planning

---

## Data Flow at Comcast (Current Setup)

```
Ad Serving Platform
    ↓ (impression events)
Databricks (event storage)
    ↓ (user-level events)
Clarivoy (MTA processing)
    ↓ (attribution results)
Salesforce (reporting for AEs)
```

**Gap:** No MMM layer (what we're adding)

---

## Data Flow with MMM (This Project)

```
Ad Serving Platform
    ↓ (impression events)
Databricks (event storage)
    ↓ (aggregation query)
Weekly Summaries (aggregate data)
    ↓ (our pipeline)
MMM Model (Bayesian regression)
    ↓ (channel contributions)
Dashboard (strategic insights)
```

**Integration point:** Databricks aggregation → CSVDataSource (now) or DatabricksDataSource (later)

---

## Privacy Comparison

| Data Level | User IDs? | Cookie Dependent? | Post-Privacy Ready? |
|------------|-----------|-------------------|---------------------|
| Event Stream | Yes | Yes | ❌ No |
| Aggregate | No | No | ✅ Yes |
| MTA Output | Derived from events | Yes | ❌ No |
| MMM Output | No user data | No | ✅ Yes |

**Key insight:** MMM is privacy-safe by design - no user tracking required.

---

## What This Project Generates

**Currently:** Synthetic aggregate data (Level 2)  
**Future option:** Synthetic event stream (Level 1) → aggregation pipeline → MMM input

This shows the full data landscape without requiring production data access.
