# AdTech Attribution Data Dictionary

A comprehensive reference for the data signals that modern attribution and measurement vendors use. Organized by domain. Not all signals are available in every measurement approach — privacy regime, channel type, and vendor relationship determine what's accessible.

---

## Table of Contents
1. [Exposure & Impression Data](#1-exposure--impression-data)
2. [Conversion & Outcome Data](#2-conversion--outcome-data)
3. [Identity & Audience Data](#3-identity--audience-data)
4. [Channel-Specific Signals](#4-channel-specific-signals)
5. [Creative & Asset Data](#5-creative--asset-data)
6. [Spend & Budget Data](#6-spend--budget-data)
7. [Context & Environment Data](#7-context--environment-data)
8. [Geo & Location Data](#8-geo--location-data)
9. [Device & Technical Data](#9-device--technical-data)
10. [First-Party & CRM Data](#10-first-party--crm-data)
11. [Third-Party Enrichment Data](#11-third-party-enrichment-data)
12. [Control & Baseline Variables](#12-control--baseline-variables)
13. [Clean Room & Privacy-Safe Data](#13-clean-room--privacy-safe-data)
14. [Attribution Output Data](#14-attribution-output-data)
15. [Incrementality & Experiment Data](#15-incrementality--experiment-data)
16. [Platform API Data](#16-platform-api-data)
17. [Data Availability by Attribution Method](#17-data-availability-by-attribution-method)

---

## 1. Exposure & Impression Data

The raw record of an ad being served. The foundational input for all attribution.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `impression_id` | string | Unique event identifier | `imp_8a3f2b1c` |
| `timestamp` | datetime | UTC time the impression was served | `2026-02-15T14:32:07Z` |
| `user_id` | string | Pseudonymous or hashed user identifier | `uid_94f1a2` |
| `household_id` | string | Household-level grouping (especially for CTV/linear) | `hh_00231` |
| `device_id` | string | Device-level identifier (IDFA, GAID, IP-derived) | `idfa_7a9c...` |
| `campaign_id` | string | Campaign grouping for the ad | `camp_2026_q1_brand` |
| `line_item_id` | string | Trafficking unit within a campaign | `li_8832` |
| `creative_id` | string | Specific ad creative served | `cr_30sec_v2` |
| `placement_id` | string | Ad slot or placement within a publisher | `place_espn_preroll` |
| `channel` | enum | Media channel type | `ctv`, `linear_tv`, `search`, `social`, `display`, `audio`, `ooh`, `email` |
| `publisher_id` | string | Identity of the publisher serving the ad | `nbcu_peacock` |
| `ad_format` | enum | Format of the ad unit | `video_preroll`, `banner_300x250`, `native`, `audio_spot` |
| `duration_seconds` | integer | Length of video/audio ad in seconds | `30` |
| `viewability_pct` | float | Percentage of ad pixels in view (display/video) | `0.82` |
| `view_through_pct` | float | Fraction of video watched before skip | `0.91` |
| `completed_view` | boolean | Whether video was watched to completion | `true` |
| `audibility` | boolean | Whether audio was on during the impression (CTV/video) | `true` |
| `cost_per_impression` | float | CPM / 1000 for this impression | `0.0185` |
| `auction_id` | string | Programmatic auction identifier | `auc_bb3...` |
| `deal_id` | string | PMP or programmatic guaranteed deal | `deal_4421` |
| `supply_type` | enum | Inventory source type | `open_exchange`, `pmp`, `programmatic_guaranteed`, `direct` |
| `environment` | enum | App or web context | `app`, `mobile_web`, `desktop_web`, `ctv_app` |
| `content_genre` | string | Genre of surrounding content | `sports`, `news`, `drama` |
| `content_rating` | string | Audience rating of the content | `PG`, `TV-14` |

**Scale:** 10M–500M rows/week for large advertisers  
**Primary users:** MTA (Multi-Touch Attribution), Frequency analysis, Reach & frequency planning  
**Storage pattern:** Event tables in data warehouse (Databricks, BigQuery, Snowflake)

---

## 2. Conversion & Outcome Data

What actually happened — the "Y" variable in all attribution models.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `conversion_id` | string | Unique conversion event identifier | `conv_00184` |
| `timestamp` | datetime | UTC time the conversion occurred | `2026-02-16T09:15:22Z` |
| `user_id` | string | Pseudonymous/hashed user who converted | `uid_94f1a2` |
| `household_id` | string | Household-level linkage | `hh_00231` |
| `conversion_type` | enum | What outcome occurred | `purchase`, `lead`, `registration`, `install`, `subscription`, `store_visit`, `call`, `brand_lift` |
| `conversion_value` | float | Revenue or assigned value in USD | `249.99` |
| `order_id` | string | Transaction identifier for purchases | `ord_77421` |
| `product_id` | string | SKU or product purchased | `sku_tv65_4k` |
| `product_category` | string | Category hierarchy | `electronics/televisions` |
| `source` | enum | Where the conversion was recorded | `website`, `app`, `in_store`, `call_center`, `crm` |
| `attribution_window` | string | Lookback window applied | `1d_view`, `7d_click`, `28d_view` |
| `channel_last_touch` | string | Last channel before conversion (for reference) | `search` |
| `session_id` | string | Web/app session associated with conversion | `sess_9a12` |
| `is_new_customer` | boolean | First-time conversion vs. repeat | `true` |
| `is_attributed` | boolean | Whether any touchpoint was matched | `true` |
| `conversion_lag_days` | integer | Days from first exposure to conversion | `4` |

**Scale:** 10K–5M events/week  
**Tag implementations:** Pixel fires (JS), server-side events (CAPI), SDK events  
**Privacy concern:** User-level — requires consent and/or hashing in post-cookie environments

---

## 3. Identity & Audience Data

Links exposures to outcomes and enriches who the audience is.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `user_id` | string | Internal pseudonymous ID (hashed email, RampID) | `ramp_abc123` |
| `hashed_email` | string | SHA-256 or MD5 of email address | `5f4dcc3b...` |
| `hashed_phone` | string | Hashed phone number for matching | `c4ca4238...` |
| `idfa` | string | Apple iOS device identifier (post-ATT: consent required) | `A1B2-C3D4...` |
| `gaid` | string | Google Android Advertising ID | `38400000-...` |
| `cookie_id` | string | Third-party cookie (deprecated/limited) | `_ga=2.1...` |
| `ip_address` | string | IPv4/v6 for probabilistic matching (hashed for privacy) | `[hashed]` |
| `household_id` | string | IP or set-top box derived household grouping | `hh_00231` |
| `livewramp_id` | string | LiveRamp RampID (cross-publisher resolution) | `ramp_...` |
| `uid2` | string | Unified ID 2.0 — hashed/salted email-based ID | `uid2_...` |
| `first_party_segment` | string | Advertiser-defined audience segment | `high_intent_buyers` |
| `lookalike_segment` | string | Model-expanded audience based on seed | `lal_cust_30d` |
| `age_bucket` | enum | Age range (from panel or modeled) | `25-34`, `35-44` |
| `gender` | enum | Gender (from panel or modeled) | `M`, `F`, `Unknown` |
| `income_bucket` | enum | HHI range | `$75k-$100k` |
| `education_level` | enum | Modeled or panel-sourced | `college_grad` |
| `parental_status` | boolean | Has children in household | `true` |
| `dma_code` | string | Nielsen Designated Market Area code | `501` (NYC) |
| `zip_code` | string | 5-digit USPS zip | `10001` |
| `lifecycle_stage` | enum | Customer journey stage | `prospect`, `active_customer`, `lapsed`, `churned` |
| `propensity_score` | float | Model score for likelihood to convert | `0.73` |
| `identity_confidence` | float | Match quality score (0–1) | `0.91` |
| `opt_in_consent` | boolean | User has consented to tracking/targeting | `true` |

**Privacy note:** PII fields must be hashed or handled in clean rooms. Post-cookie, deterministic IDs require active consent. Probabilistic IDs (IP-based) have lower legal certainty.

---

## 4. Channel-Specific Signals

### 4a. Linear TV

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `network` | string | Broadcast or cable network | `ESPN`, `NBC` |
| `daypart` | enum | Programming time block | `primetime`, `late_night`, `daytime` |
| `program_name` | string | Show the ad aired in | `Sunday Night Football` |
| `spot_length` | integer | Ad duration in seconds | `30` |
| `pod_position` | integer | Position within the commercial break | `1` (first) |
| `pod_length` | integer | Total seconds in the commercial break | `120` |
| `air_date` | date | Date the spot aired | `2026-02-15` |
| `market` | string | Local or national market | `DMA:501`, `national` |
| `grp` | float | Gross Rating Points (reach × frequency) | `25.4` |
| `trp` | float | Target Rating Points (GRPs for target demo) | `18.2` |
| `household_reach` | integer | Estimated households reached | `4200000` |
| `rate_card_cpm` | float | Published CPM for the placement | `18.50` |
| `actual_cpm` | float | Negotiated/cleared CPM | `15.20` |
| `acr_match_rate` | float | Fraction of households with ACR data (Inscape, Samba TV) | `0.42` |

### 4b. CTV / Streaming

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `platform` | string | Streaming service | `Peacock`, `Tubi`, `Hulu`, `Pluto` |
| `device_type` | enum | Smart TV type or platform | `roku`, `fire_tv`, `apple_tv`, `smart_tv` |
| `content_type` | enum | Live or on-demand | `live`, `vod`, `bvod` |
| `stream_id` | string | Individual viewing session | `stream_a1b2` |
| `acr_event_id` | string | ACR impression match token | `acr_9f3...` |
| `completion_rate` | float | Share who watched the full ad | `0.94` |
| `qr_scan_event_id` | string | If QR code scanned from screen | `qr_evt_001` |
| `interactive_engagement` | boolean | Viewer interacted with ad (shoppable) | `true` |
| `frequency_campaign` | integer | Exposures to this campaign in window | `3` |

### 4c. Search (Paid)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `query` | string | Search query that triggered the ad | `best 65 inch tv 2026` |
| `keyword` | string | Matched keyword in campaign | `buy 4k television` |
| `match_type` | enum | Keyword match type | `broad`, `phrase`, `exact` |
| `ad_rank` | integer | Position of the ad in search results | `2` |
| `quality_score` | integer | Platform quality score (1–10) | `8` |
| `click_through_rate` | float | CTR for the keyword | `0.047` |
| `cost_per_click` | float | CPC for this keyword | `1.42` |
| `search_engine` | enum | Platform | `google`, `bing`, `amazon` |
| `brand_vs_nonbrand` | enum | Query type | `brand`, `nonbrand`, `competitor` |

### 4d. Social Media

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `platform` | enum | Social network | `meta_facebook`, `meta_instagram`, `tiktok`, `youtube`, `pinterest`, `snapchat` |
| `ad_set_id` | string | Ad set / ad group identifier | `adset_9912` |
| `objective` | enum | Campaign objective | `reach`, `video_views`, `conversions`, `app_installs` |
| `placement` | enum | Placement within platform | `feed`, `stories`, `reels`, `in-stream` |
| `engagement_actions` | integer | Likes, shares, comments | `1842` |
| `video_3s_views` | integer | Views of 3+ seconds | `420000` |
| `swipe_ups` | integer | Story swipe-up clicks | `312` |
| `capi_match_rate` | float | Server-side Conversions API match rate | `0.76` |

### 4e. Display / Programmatic

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `dsp` | string | Demand-side platform | `ttd`, `dv360`, `xandr` |
| `ssp` | string | Supply-side platform | `pubmatic`, `magnite` |
| `ad_size` | string | Banner dimensions | `300x250`, `728x90`, `320x50` |
| `viewability_vendor` | string | Viewability measurement partner | `doubleverify`, `ias`, `moat` |
| `brand_safety_score` | float | Brand suitability score (0–100) | `92.0` |
| `invalid_traffic_flag` | boolean | IVT or bot traffic detected | `false` |
| `click_url` | string | Landing page URL (hashed for privacy) | `[hashed]` |
| `post_click_session` | boolean | Did a trackable session follow the click | `true` |

### 4f. Audio / Podcasts / Streaming Radio

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `platform` | enum | Audio platform | `spotify`, `pandora`, `iheartradio`, `podcast_network` |
| `content_type` | enum | Format | `streaming_radio`, `podcast`, `audiobook` |
| `listen_completion_rate` | float | Fraction of ad heard | `0.88` |
| `host_read` | boolean | Host-read podcast ad | `true` |
| `vanity_url_traffic` | integer | Web visits from mention of vanity URL | `1440` |
| `promo_code_redemptions` | integer | Promo code uses attributable to spot | `87` |

### 4g. Out-of-Home (OOH/DOOH)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `panel_id` | string | Billboard or display panel identifier | `panel_times_sq_001` |
| `location_lat` | float | Latitude of the panel | `40.7580` |
| `location_lon` | float | Longitude of the panel | `-73.9855` |
| `daily_impressions_est` | integer | Estimated daily exposures (traffic × visibility) | `128000` |
| `dwell_time_seconds` | integer | Average view time for digital OOH | `6` |
| `creative_rotation` | string | Which creative displayed in the slot | `cr_brand_v1` |
| `foot_traffic_lift` | float | Lift in store visits near panel vs. control | `0.04` |
| `mobile_device_seen` | integer | Devices observed near panel (mobility data provider) | `48000` |

### 4h. Email

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `email_send_id` | string | Campaign send batch ID | `send_2026_02_15_a` |
| `open_event` | boolean | Email opened (unreliable post Apple MPP) | `true` |
| `click_event` | boolean | Link inside email was clicked | `true` |
| `subject_line` | string | Email subject (for A/B testing) | `Exclusive offer for you` |
| `send_time` | datetime | Time email was delivered | `2026-02-15T09:00:00Z` |
| `unsubscribe` | boolean | Recipient unsubscribed | `false` |
| `deliverability_score` | float | Inbox placement probability | `0.94` |
| `utm_campaign` | string | UTM tracking parameter | `em_promo_feb26` |
| `utm_medium` | string | UTM medium tag | `email` |

---

## 5. Creative & Asset Data

Attributes of the ad itself — critical for creative effectiveness analysis.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `creative_id` | string | Unique creative identifier | `cr_30sec_brand_v3` |
| `creative_name` | string | Human-readable name | `Brand_30s_Spring_2026_V3` |
| `format` | enum | Ad format type | `video_30s`, `video_15s`, `display_300x250`, `native`, `audio_30s` |
| `has_logo_first_5s` | boolean | Brand logo appears in first 5 seconds | `true` |
| `has_cta` | boolean | Contains a call-to-action | `true` |
| `cta_text` | string | Text of the call-to-action | `Shop Now` |
| `message_theme` | enum | Primary message category | `promotional`, `brand`, `product_feature`, `testimonial` |
| `emotion_primary` | enum | Dominant emotional tone | `joy`, `excitement`, `trust`, `urgency` |
| `sentiment_score` | float | NLP-derived sentiment (–1 to +1) | `0.72` |
| `has_celebrity` | boolean | Features a celebrity or known spokesperson | `false` |
| `product_shown` | boolean | Product is visually featured | `true` |
| `price_mentioned` | boolean | Price or offer disclosed in creative | `true` |
| `offer_type` | enum | Promotional mechanic | `discount_pct`, `bogo`, `free_shipping`, `none` |
| `color_palette` | string | Primary visual colors | `blue_white_orange` |
| `brand_prominence_score` | float | Fraction of video frames with brand visible (0–1) | `0.61` |
| `ab_test_cell` | string | Experiment cell assignment | `variant_b` |
| `flight_start_date` | date | When creative began running | `2026-02-01` |
| `flight_end_date` | date | When creative stopped | `2026-02-28` |
| `version` | string | Iteration/version tag | `v3` |

---

## 6. Spend & Budget Data

Financial inputs to attribution models.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `period` | date | Time period (daily/weekly) | `2026-02-15` |
| `channel` | enum | Media channel | `ctv`, `search`, `social` |
| `campaign_id` | string | Campaign grouping | `camp_q1_brand` |
| `gross_spend` | float | Total billed spend before fees (USD) | `128500.00` |
| `net_spend` | float | Media cost after agency/tech fees | `109225.00` |
| `agency_fee` | float | Agency commission | `12850.00` |
| `tech_fee` | float | DSP/ad tech platform fees | `6425.00` |
| `impressions_delivered` | integer | Total impressions served | `6942000` |
| `clicks` | integer | Total link clicks | `14233` |
| `completed_views` | integer | 100% video completions | `5210000` |
| `effective_cpm` | float | Effective CPM (spend / impressions × 1000) | `18.51` |
| `effective_cpcv` | float | Cost per completed view | `0.0247` |
| `planned_budget` | float | Original planned allocation | `130000.00` |
| `budget_utilization_pct` | float | Spend vs. plan | `0.988` |
| `pacing_flag` | enum | Under/on/over pace | `on_pace` |
| `rate_type` | enum | Buying model | `cpm`, `cpc`, `cpv`, `cpa`, `cpiagg`, `flat_rate` |
| `io_id` | string | Insertion Order identifier | `io_20892` |

---

## 7. Context & Environment Data

Signals about *when* and *where* the ad ran — important for MMM control variables.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `date` | date | Calendar date | `2026-02-15` |
| `day_of_week` | enum | Day name | `Sunday` |
| `week_number` | integer | ISO week number | `7` |
| `month` | integer | Calendar month | `2` |
| `quarter` | integer | Fiscal or calendar quarter | `1` |
| `is_holiday` | boolean | Date falls on a major holiday | `false` |
| `holiday_name` | string | Name if applicable | `Presidents Day` |
| `is_tentpole_event` | boolean | Major cultural/sporting event nearby | `true` |
| `event_name` | string | Name of the event | `Super Bowl LX` |
| `competitor_spend_index` | float | Relative competitive spend pressure (indexed) | `1.24` |
| `category_search_trend` | float | Google Trends index for product category | `84.0` |
| `news_sentiment_index` | float | Macro news valence (0–100, 50 = neutral) | `46.0` |
| `content_context` | string | Publisher content topic (brand safe scoring) | `sports/football` |
| `weather_condition` | enum | Local weather (for geo campaigns) | `sunny`, `rain`, `snow` |
| `temperature_f` | float | Local temperature (relevant for some categories) | `38.0` |

---

## 8. Geo & Location Data

Geographic context for targeting, analysis, and incrementality experiments.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `country` | string | ISO country code | `US` |
| `state` | string | US state abbreviation | `NY` |
| `dma_code` | string | Nielsen DMA code | `501` |
| `dma_name` | string | DMA name | `New York` |
| `zip_code` | string | USPS 5-digit zip | `10001` |
| `cbsa_code` | string | Core-Based Statistical Area | `35620` |
| `store_id` | string | Physical store for offline conversion linkage | `store_004_nyc_5th` |
| `store_distance_miles` | float | Distance from impression to nearest store | `0.8` |
| `geo_test_cell` | enum | Incrementality experiment assignment | `treatment`, `control`, `holdout` |
| `geo_population` | integer | Total population in geo | `8336817` |
| `geo_index_spend` | float | Spend per capita vs. national average | `1.42` |
| `mobility_index` | float | Foot traffic activity vs. baseline (SafeGraph, Placer) | `0.97` |
| `lat` | float | Latitude (for mobile geofencing) | `40.7589` |
| `lon` | float | Longitude | `-73.9851` |
| `geofence_id` | string | Named geofence zone | `gf_nycmidtown_pod1` |

---

## 9. Device & Technical Data

Technical characteristics of the device/environment where the ad was viewed.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `device_type` | enum | Form factor category | `desktop`, `mobile`, `tablet`, `ctv`, `smart_speaker` |
| `os` | enum | Operating system | `ios`, `android`, `windows`, `macos`, `tvos`, `roku_os` |
| `os_version` | string | OS version string | `iOS 18.3` |
| `browser` | enum | Web browser | `chrome`, `safari`, `firefox`, `edge` |
| `browser_version` | string | Browser version | `133.0` |
| `app_name` | string | App where ad was served | `Peacock` |
| `app_bundle_id` | string | App bundle identifier | `com.nbcuniversal.peacock` |
| `screen_resolution` | string | Display resolution | `1920x1080` |
| `connection_type` | enum | Network connection type | `wifi`, `4g`, `5g`, `ethernet` |
| `carrier` | string | Mobile carrier (if applicable) | `Verizon` |
| `itp_limited` | boolean | Safari/ITP tracking limitations apply | `true` |
| `is_atl_limited` | boolean | iOS App Tracking Transparency opted-out | `true` |
| `user_agent` | string | Raw user agent string (partially anonymized) | `Mozilla/5.0...` |
| `user_agent_client_hints` | object | Structured browser identity hint | `{brand: "Chrome", version: "133"}` |

---

## 10. First-Party & CRM Data

Data the advertiser (or we as a media seller) owns directly. Highest-value signal for targeting and lift measurement.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `crm_customer_id` | string | Internal CRM unique ID | `cust_00183228` |
| `hashed_email` | string | SHA-256 of email for clean room matching | `5f4dcc...` |
| `subscription_status` | enum | Subscription or product tier | `active`, `trial`, `lapsed`, `churned` |
| `product_tier` | string | Current product/plan | `premium_plus` |
| `ltv` | float | Estimated or actual lifetime value (USD) | `1240.00` |
| `account_age_days` | integer | Days since account creation | `842` |
| `last_purchase_date` | date | Most recent transaction | `2025-11-15` |
| `purchase_frequency` | float | Purchases per year | `3.2` |
| `average_order_value` | float | Mean transaction value | `182.50` |
| `churn_risk_score` | float | Propensity to cancel (0–1) | `0.38` |
| `upsell_propensity` | float | Likelihood to upgrade | `0.61` |
| `preferred_channel` | enum | Channel with highest engagement history | `email`, `push`, `ctv` |
| `nps_score` | integer | Net Promoter Score (0–10) | `8` |
| `opted_in_email` | boolean | Has opted in to marketing email | `true` |
| `opted_in_sms` | boolean | Has opted in to SMS marketing | `false` |
| `data_source` | enum | Originating system | `billing`, `website`, `crm`, `dmp`, `app` |
| `segment_label` | string | First-party audience segment name | `high_value_sports_fan` |

---

## 11. Third-Party Enrichment Data

External data appended to profiles or used as model inputs.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `hhi_bucket` | enum | Household income range (Experian, Neustar) | `$100k-$150k` |
| `home_ownership` | enum | Own vs. rent | `owner`, `renter` |
| `length_of_residence` | integer | Years at current address | `6` |
| `vehicle_segments` | string | Auto ownership profile (IHS Markit) | `suv_owner`, `new_car_intender` |
| `financial_segment` | string | Credit/financial behavior segment | `mass_affluent` |
| `retail_buyer_category` | string | Purchase propensity category | `consumer_electronics_buyer` |
| `sports_fan_index` | float | Sports content consumption index | `148.0` (vs. 100 base) |
| `tv_viewing_hours_wk` | float | Weekly TV viewing estimate (Nielsen panel) | `22.5` |
| `cord_cutter_flag` | boolean | Has canceled cable/satellite | `true` |
| `streaming_service_count` | integer | Number of active streaming subscriptions | `4` |
| `political_affiliation` | enum | Modeled political lean (use carefully/avoid) | — |
| `health_condition_flag` | enum | Health segment (heavily regulated — HIPAA/NAI) | — |
| `psychographic_segment` | string | Lifestyle/values segment (ValuesGraphics, Kantar) | `eco_conscious_achiever` |
| `provider_source` | string | Third-party data vendor | `Experian`, `Acxiom`, `Neustar`, `Oracle_Datacloud` |

**Regulatory note:** Sensitive categories (health, political, financial, religion) carry heightened compliance obligations (CCPA, CPRA, NAI Code, HIPAA). Handle with care.

---

## 12. Control & Baseline Variables

Exogenous signals used as covariates in MMM to prevent confounding.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `week` | date | Week start date | `2026-02-09` |
| `seasonality_index` | float | Cyclical demand index for the category (0–2, 1 = average) | `1.18` |
| `trend_index` | float | Long-run demand trend component | `1.04` |
| `promotions_active` | boolean | Was there an active sale or discount this period | `true` |
| `promotion_depth_pct` | float | Average discount depth during promo | `0.20` |
| `price_index` | float | Relative average selling price vs. baseline | `0.95` |
| `distribution_index` | float | Product availability / weighted distribution | `0.99` |
| `new_product_launch` | boolean | A new SKU or model launched this week | `false` |
| `pr_event_flag` | boolean | Earned media / PR event this period | `true` |
| `pr_event_name` | string | Name of PR moment | `CES_2026_announcement` |
| `macro_economic_index` | float | Consumer confidence or GDP proxy | `102.4` |
| `unemployment_rate` | float | Regional or national UE rate | `0.039` |
| `cpi_yoy` | float | Consumer Price Index year-over-year change | `0.028` |
| `search_volume_brand` | float | Google Trends index for brand name | `73.0` |
| `search_volume_category` | float | Google Trends index for category terms | `62.0` |
| `social_listening_mentions` | integer | Brand mentions across social this week | `14800` |
| `earned_media_score` | float | Volume × sentiment of press/social coverage | `0.62` |
| `competitive_activity_flag` | boolean | Major competitor ad blitz this period | `false` |
| `weather_anomaly` | float | Deviation from avg temperature (for weather-sensitive verticals) | `+8.2°F` |

---

## 13. Clean Room & Privacy-Safe Data

Constructs that enable cross-party data collaboration without sharing raw PII.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `clean_room_id` | string | Shared join key agreed upon by all parties | `cr_joinkeyv2` |
| `match_rate` | float | Share of records matched across data sets | `0.62` |
| `overlap_count` | integer | Number of matched entities (min-k anonymized) | `14200` |
| `unique_reach` | integer | Distinct households reached (aggregated) | `4200000` |
| `conversion_count_agg` | integer | Aggregated conversions (no user-level export) | `18420` |
| `cohort_id` | string | Anonymized audience cohort (Privacy Sandbox Topics) | `cohort_sports_fan_252` |
| `aggregation_threshold` | integer | Minimum cohort size for output (differential privacy) | `100` |
| `noise_epsilon` | float | Differential privacy epsilon parameter | `0.10` |
| `clean_room_vendor` | string | Platform used | `AWS Clean Rooms`, `Habu`, `InfoSum`, `Snowflake DCR` |
| `data_contributor_a` | string | First party in the join | `Comcast_Advertising` |
| `data_contributor_b` | string | Second party in the join | `Advertiser_Name` |
| `query_type` | enum | Type of analysis performed in the clean room | `lift_analysis`, `reach_frequency`, `overlap_report`, `audience_match` |

---

## 14. Attribution Output Data

Results produced by attribution models — inputs to planning and optimization.

### Multi-Touch Attribution (MTA) Output

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `conversion_id` | string | Conversion being attributed | `conv_00184` |
| `touchpoint_id` | string | Impression being credited | `imp_8a3f2b1c` |
| `channel` | string | Channel receiving credit | `ctv` |
| `creative_id` | string | Creative being credited | `cr_30sec_v2` |
| `credit_pct` | float | Share of conversion value assigned | `0.35` |
| `credit_value` | float | Dollar value of credit | `87.50` |
| `model_type` | enum | Attribution rule used | `last_touch`, `first_touch`, `linear`, `time_decay`, `data_driven`, `shapley` |
| `touchpoint_position` | enum | Position in the journey | `first`, `middle`, `last` |
| `days_before_conversion` | integer | Lead time of this touchpoint | `3` |
| `conversion_window_days` | integer | Attribution lookback applied | `28` |

### MMM Output (Aggregate)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `period` | date | Time period | `2026-Q1` |
| `channel` | string | Media channel | `ctv` |
| `attribution_pct` | float | Share of total conversions attributed | `0.35` |
| `incremental_conversions` | float | Lift above baseline caused by channel | `3250` |
| `baseline_conversions` | float | Organic/non-media conversions | `6000` |
| `cost_per_incremental_conversion` | float | CPA for attributed conversions | `78.50` |
| `roi` | float | Revenue per dollar spent | `2.14` |
| `mroi` | float | Marginal ROI at current spend level | `1.83` |
| `beta_coefficient` | float | Regression coefficient for channel | `0.42` |
| `credible_interval_low` | float | 2.5th percentile of posterior (Bayesian) | `0.31` |
| `credible_interval_high` | float | 97.5th percentile of posterior (Bayesian) | `0.54` |
| `saturation_level` | float | Current spend as fraction of saturation point | `0.72` |
| `adstock_decay` | float | Estimated carryover decay rate | `0.68` |
| `half_saturation_spend` | float | Spend level for half-max response (Hill param γ) | `95000.00` |

---

## 15. Incrementality & Experiment Data

Data captured from controlled tests — the gold standard for causal attribution.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `experiment_id` | string | Unique test identifier | `exp_ctv_geo_q1_2026` |
| `experiment_type` | enum | Test methodology | `geo_holdout`, `user_holdout`, `psa_test`, `ghost_ad`, `switchback` |
| `geo_or_cell_id` | string | Experimental unit | `dma_501` or `user_cluster_7` |
| `assignment` | enum | Treatment/control assignment | `treatment`, `control` |
| `treatment_spend` | float | Media spend in treatment cell this week | `88000.00` |
| `control_spend` | float | Media spend in control cell (0 for holdout) | `0.00` |
| `conversion_rate_treatment` | float | Conversion rate in treatment cell | `0.0041` |
| `conversion_rate_control` | float | Conversion rate in control cell | `0.0035` |
| `absolute_lift` | float | Difference in conversion rates | `0.0006` |
| `relative_lift_pct` | float | Lift as % of control rate | `0.171` |
| `p_value` | float | Statistical significance | `0.031` |
| `confidence_interval_low` | float | Lower bound of lift estimate | `0.0001` |
| `confidence_interval_high` | float | Upper bound of lift estimate | `0.0011` |
| `incremental_conversions_est` | float | Estimated total lift | `420` |
| `cost_per_incremental_conversion` | float | Test-derived CPA | `209.52` |
| `test_duration_weeks` | integer | Length of experiment | `4` |
| `power` | float | Statistical power achieved | `0.82` |
| `mde_pct` | float | Minimum detectable effect applied | `0.10` |
| `pre_experiment_balance_pct` | float | Similarity of cells in pre-period | `0.97` |

---

## 16. Platform API Data

Native metrics from ad platform APIs — used for pacing, optimization, and reconciliation.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `platform` | string | Ad platform name | `google_ads`, `meta`, `ttd`, `amazon_dsp` |
| `report_date` | date | Reporting day | `2026-02-15` |
| `account_id` | string | Platform account identifier | `act_123456789` |
| `campaign_id` | string | Platform campaign ID | `camp_98721` |
| `impressions` | integer | Impressions reported by platform | `4218000` |
| `clicks` | integer | Clicks reported by platform | `10820` |
| `conversions_platform` | integer | Conversions attributed by platform's own model | `842` |
| `view_through_conversions` | integer | VTC count (platform-attributed) | `310` |
| `spend` | float | Spend reported by platform | `88250.00` |
| `frequency` | float | Average exposures per unique user | `3.2` |
| `unique_reach` | integer | Unique users or households reached | `1318750` |
| `video_p25_rate` | float | % who watched 25% of video | `0.84` |
| `video_p50_rate` | float | % who watched 50% | `0.76` |
| `video_p75_rate` | float | % who watched 75% | `0.67` |
| `video_completion_rate` | float | % who watched 100% | `0.58` |
| `brand_lift_survey_lift` | float | Unaided awareness or purchase intent lift from brand lift study | `+4.2pp` |
| `search_lift_pct` | float | Lift in branded search queries (Meta/YouTube metric) | `+8.1%` |
| `data_freshness_lag_hours` | integer | How stale is this API data | `24` |

---

## 17. Data Availability by Attribution Method

| Data Domain | Rule-Based MTA | Data-Driven MTA | MMM | Incrementality Testing | Clean Room |
|------------|:-:|:-:|:-:|:-:|:-:|
| Impression events (user-level) | ✅ | ✅ | ❌ | ✅ | ✅ |
| Conversion events (user-level) | ✅ | ✅ | ❌ | ✅ | ✅ |
| Identity / User IDs | ✅ | ✅ | ❌ | Partial | ✅ |
| Aggregate spend/impressions | ✅ | ✅ | ✅ | ✅ | ✅ |
| Aggregate conversions | ✅ | ✅ | ✅ | ✅ | ✅ |
| Creative attributes | ✅ | ✅ | Partial | ✅ | ✅ |
| Geo data | ✅ | ✅ | ✅ | ✅ | ✅ |
| Device data | ✅ | ✅ | ❌ | Partial | ✅ |
| First-party CRM data | Partial | ✅ | ❌ | Partial | ✅ |
| Third-party enrichment | Partial | ✅ | ❌ | ❌ | Partial |
| Control/seasonality variables | ❌ | ❌ | ✅ | ✅ | ❌ |
| Linear TV GRPs | ❌ | Partial | ✅ | ✅ | Partial |
| ACR/CTV exposure data | Partial | ✅ | ✅ | ✅ | ✅ |
| Experiment cell assignments | ❌ | ❌ | ❌ | ✅ | ✅ |
| Platform API metrics | ✅ | ✅ | ✅ | ✅ | Partial |

**Cookie-dependent:** Rule-based MTA, Data-driven MTA  
**Privacy-safe:** MMM, Incrementality Testing, Clean Room  
**Post-cookie ready:** MMM ✅ | Clean Room ✅ | MTA ⚠️ (with consent/identity solution)  

---

## Key Concepts

**Adstock** — The carryover effect of advertising beyond the period it ran. A TV spot from week 1 still drives some response in weeks 2 and 3. Modeled with a geometric decay function.

**Attribution Window** — The lookback period from a conversion during which touchpoints receive credit. Common windows: 1-day click, 7-day click, 28-day view.

**Baseline Conversions** — Sales or conversions that would have occurred without any advertising (organic demand). MMM models subtract this to isolate media-driven lift.

**CAPI (Conversions API)** — Server-side conversion signal passed directly to platforms (Meta, Google, TikTok), bypassing browser-level tracking limitations. Improves match rate post-iOS 14.

**Clean Room** — A secure, privacy-preserving environment where two or more parties can run queries on joined data without either party seeing the other's raw records.

**Differential Privacy** — Adding calibrated statistical noise to aggregate outputs so no individual's data can be inferred. Parameterized by epsilon (ε).

**GRP (Gross Rating Point)** — Reach × Frequency. The traditional linear TV currency. 1 GRP = 1% of target audience reached once.

**Half-Saturation Point (γ)** — In the Hill equation for saturation, γ is the spend level that produces 50% of maximum response. Spend above this delivers rapidly diminishing returns.

**Incrementality** — The causal lift caused by advertising. True incrementality answers: "What conversions would NOT have happened without this specific ad exposure?"

**mROI (Marginal ROI)** — The additional return generated by spending one more dollar on a channel at its current spend level. mROI < ROI when diminishing returns are present.

**MTA (Multi-Touch Attribution)** — User-level attribution models that allocate conversion credit across all touchpoints in a consumer journey.

**MMM (Media Mix Modeling)** — Aggregate-level regression models that estimate each channel's contribution to conversions using time-series spend and outcome data.

**Saturation** — The phenomenon where additional ad spend yields progressively smaller incremental returns. Modeled with the Hill (S-curve) or Adbudg functions.

**Unified Measurement** — Approaches that combine MMM and MTA, using experiment-calibrated priors from incrementality tests to anchor both models to causal truth.
