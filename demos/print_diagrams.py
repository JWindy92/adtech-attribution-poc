#!/usr/bin/env python3
"""
Print visual diagrams for presentations
"""

def print_architecture():
    print("\n" + "=" * 80)
    print("PLUGGABLE ARCHITECTURE - Attribution Innovation Platform")
    print("=" * 80)
    print("""
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │   DATA SOURCE   │───▶│  TRANSFORMER    │───▶│     MODEL       │───▶│   OPTIMIZER     │
    │   (Pluggable)   │    │   (Pluggable)   │    │   (Pluggable)   │    │   (Pluggable)   │
    └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
            │                       │                      │                       │
       ┌────┴────┐            ┌─────┴─────┐          ┌────┴────┐            ┌─────┴─────┐
       │   CSV   │            │  Adstock  │          │Bayesian │            │   SciPy   │
       │Databricks│           │Saturation │          │   MMM   │            │Constrained│
       │   API   │            │ Custom    │          │Spend-Prop│           │Multi-Obj  │
       └─────────┘            └───────────┘          └─────────┘            └───────────┘

    Benefits:
      ✓ Swap components without breaking the system
      ✓ Test different models side-by-side
      ✓ Add new data sources in days, not months
      ✓ Extensible to any attribution approach
    """)


def print_data_journey():
    print("\n" + "=" * 80)
    print("DATA JOURNEY - Event-Level to Strategic Decisions")
    print("=" * 80)
    print("""
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │ STEP 1: Event-Level Data (MTA Domain)                                       │
    ├──────────────────────────────────────────────────────────────────────────────┤
    │  Impression: {user_id: "abc123", channel: "CTV", timestamp: "2026-02-24"}   │
    │  Conversion: {user_id: "abc123", value: $150, timestamp: "2026-02-25"}      │
    │                                                                              │
    │  Volume: ~20,000 events/week                                                │
    │  Privacy: Contains PII (user IDs, behavior)                                 │
    │  Use Case: User journey analysis, last-click attribution                    │
    └──────────────────────────────────────────────────────────────────────────────┘
                                        ↓
                              [ AGGREGATION ]
                                        ↓
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │ STEP 2: Weekly Aggregate Data (MMM Domain)                                  │
    ├──────────────────────────────────────────────────────────────────────────────┤
    │  Week 1: {ctv_spend: $80K, search_spend: $35K, conversions: 2,500}         │
    │  Week 2: {ctv_spend: $85K, search_spend: $38K, conversions: 2,650}         │
    │                                                                              │
    │  Volume: 4 channels × 52 weeks = 208 data points                            │
    │  Privacy: No PII, fully anonymized                                          │
    │  Use Case: Channel effectiveness, budget allocation                         │
    └──────────────────────────────────────────────────────────────────────────────┘
                                        ↓
                            [ BAYESIAN MMM MODEL ]
                                        ↓
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │ STEP 3: Attribution Results                                                 │
    ├──────────────────────────────────────────────────────────────────────────────┤
    │  CTV:        30% of conversions, $25 CPC, β=0.84 ± 0.04                    │
    │  Linear TV:  28% of conversions, $27 CPC, β=0.83 ± 0.05                    │
    │  Search:     24% of conversions, $22 CPC, β=0.81 ± 0.05                    │
    │  Social:     18% of conversions, $30 CPC, β=0.81 ± 0.05                    │
    └──────────────────────────────────────────────────────────────────────────────┘
                                        ↓
                              [ OPTIMIZATION ]
                                        ↓
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │ STEP 4: Strategic Recommendations                                           │
    ├──────────────────────────────────────────────────────────────────────────────┤
    │  Current: CTV $6M, Linear $8M, Search $4M, Social $2M                       │
    │  Optimal: CTV $7.2M (+$1.2M), Linear $7M (-$1M), Search $4.5M, Social $2M  │
    │                                                                              │
    │  Expected Impact: +8% conversions with same budget                          │
    │  Revenue Lift: $XXX,XXX annually                                            │
    └──────────────────────────────────────────────────────────────────────────────┘
    """)


def print_mta_vs_mmm():
    print("\n" + "=" * 80)
    print("MTA vs. MMM - Complementary Approaches")
    print("=" * 80)
    print("""
    ┌────────────────────────────────────┬────────────────────────────────────┐
    │  Multi-Touch Attribution (MTA)     │  Media Mix Modeling (MMM)          │
    ├────────────────────────────────────┼────────────────────────────────────┤
    │  Data: Event-level (user journeys) │  Data: Aggregate (weekly totals)   │
    │  Granularity: Individual paths     │  Granularity: Channel-level        │
    │  Speed: Real-time                  │  Speed: Weekly/monthly updates     │
    │  Privacy: Requires user tracking   │  Privacy: No PII, fully safe       │
    │  Best For:                         │  Best For:                         │
    │    • Digital channels (clicks)     │    • TV/offline channels           │
    │    • Last-click optimization       │    • Budget allocation             │
    │    • Short conversion windows      │    • Long-term planning            │
    │  Vendors: Clarivoy, Adobe, Google  │  Vendors: Meta Robyn, Recast.ai    │
    │                                    │                                    │
    │  Example Output:                   │  Example Output:                   │
    │  "User saw CTV → clicked Search    │  "CTV drives 30% of conversions    │
    │   → converted"                     │   with 25% of budget"              │
    │  Attribution: 100% to Search       │  Attribution: 30% to CTV           │
    └────────────────────────────────────┴────────────────────────────────────┘
                                        ↓
                            ┌───────────────────────┐
                            │  UNIFIED ATTRIBUTION  │
                            ├───────────────────────┤
                            │  Combines both:       │
                            │  • MTA for digital    │
                            │  • MMM for TV/offline │
                            │  • Calibrate MTA with │
                            │    MMM coefficients   │
                            │                       │
                            │  → Best of both worlds│
                            └───────────────────────┘
    """)


def print_trends_roadmap():
    print("\n" + "=" * 80)
    print("2026 ATTRIBUTION TRENDS - Industry Landscape")
    print("=" * 80)
    print("""
    Trend 1: Performance Over Platforms
           └─ ✅ MMM (Built), Unified Attribution (Roadmap), Incrementality (Q3)

    Trend 2: End of TV vs. Digital Divide
           └─ ✅ Architecture supports unified video (Built), CTV+Linear (Ready)

    Trend 3: World Cup 2026 Real-Time Lab
           └─ 🔨 Real-time attribution (Q2), Event-driven modeling (Q3)

    Trend 4: CTV Connects Reach to Relevance
           └─ 🔨 Clean room matching (Q2), Household attribution (Q3)

    Trend 5: Data Reawakens with Creativity
           └─ 🎯 Creative testing (Q2), DCO measurement (Q3)

    Trend 6: Collaboration Economy
           └─ 🎯 Clean rooms (Q2), Federated learning (Q4)

    Trend 7: APAC Leads Innovation
           └─ 📋 Mobile attribution (Q3), DOOH (Q4)

    Trend 8: Gen Z and Dynamic Identity
           └─ 📋 Real-time segmentation (Q4), Social listening (Q3)

    Legend:  ✅ Built    🔨 In Progress    🎯 Next Quarter    📋 Planned
    """)


def print_value_proposition():
    print("\n" + "=" * 80)
    print("VALUE PROPOSITION - Why This Matters")
    print("=" * 80)
    print("""
    ┌──────────────────────────────────────────────────────────────────────┐
    │                        THE PROBLEM                                   │
    ├──────────────────────────────────────────────────────────────────────┤
    │  Current State (Comcast Advertising):                               │
    │    • Advertisers spend $24.5M/year on our inventory (CTV, Linear)   │
    │    • They use vendor attribution (Clarivoy) - last-click only       │
    │    • We can't prove incremental lift from our inventory             │
    │    • Pricing based on CPM, not marginal ROI                         │
    │    • No visibility into advertiser saturation/upsell opportunities  │
    │    • Sales team lacks data-driven upsell justification              │
    └──────────────────────────────────────────────────────────────────────┘
                                    ↓
    ┌──────────────────────────────────────────────────────────────────────┐
    │                        THE SOLUTION                                  │
    ├──────────────────────────────────────────────────────────────────────┤
    │  Internal MMM gives us directional intelligence:                    │
    │    ✓ Estimate incremental lift from our CTV/Linear inventory        │
    │    ✓ Identify saturation points (upsell headroom vs. diminishing)   │
    │    ✓ Quantify marginal ROI for pricing strategy                     │
    │    ✓ Privacy-safe analysis (aggregate data only)                    │
    │    ✓ Supplement vendor attribution with cross-channel view          │
    └──────────────────────────────────────────────────────────────────────┘
                                    ↓
    ┌──────────────────────────────────────────────────────────────────────┐
    │                        THE IMPACT                                    │
    ├──────────────────────────────────────────────────────────────────────┤
    │  Business Value (Internal Use Only):                                │
    │    • Identify advertisers with upsell headroom: "You could spend    │
    │      20% more on CTV before hitting diminishing returns"            │
    │    • Data-driven pricing: Charge premium for high-ROI inventory     │
    │    • Yield optimization: Shift inventory to highest-value advertisers│
    │    • Sales enablement: Prove incremental value vs. competitors      │
    │    • Prevent churn: Flag over-saturated advertisers before they cut │
    │                                                                      │
    │  Timeline to Value:                                                  │
    │    Week 1-2:  Databricks integration (real advertiser campaigns)    │
    │    Week 3-6:  Validation against incrementality tests               │
    │    Week 7-12: Pilot with sales team, test recommendations           │
    │    Quarter 2: Integrate into yield/pricing workflows                │
    └──────────────────────────────────────────────────────────────────────┘
    """)


def main():
    print("\n")
    print("🎨 PRESENTATION VISUALS - Attribution Innovation Lab")
    print("=" * 80)
    
    options = {
        '1': ('Architecture Diagram', print_architecture),
        '2': ('Data Journey', print_data_journey),
        '3': ('MTA vs. MMM Comparison', print_mta_vs_mmm),
        '4': ('Trends Roadmap', print_trends_roadmap),
        '5': ('Value Proposition', print_value_proposition),
        'all': ('Print All Diagrams', lambda: [f() for _, f in sorted([(k, v[1]) for k, v in options.items() if k != 'all'])])
    }
    
    print("\nAvailable diagrams:")
    for key, (name, _) in options.items():
        print(f"  [{key}] {name}")
    
    choice = input("\nSelect diagram (or 'all'): ").strip()
    
    if choice in options:
        options[choice][1]()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        choice = sys.argv[1]
        options = {
            'arch': print_architecture,
            'journey': print_data_journey,
            'comparison': print_mta_vs_mmm,
            'trends': print_trends_roadmap,
            'value': print_value_proposition,
            'all': lambda: [print_architecture(), print_data_journey(), print_mta_vs_mmm(), print_trends_roadmap(), print_value_proposition()]
        }
        if choice in options:
            options[choice]()
        else:
            main()
    else:
        main()
