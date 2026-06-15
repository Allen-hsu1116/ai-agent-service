# Module 03: Analysis Methods

Load this module when the user asks for trend analysis, segmentation, top contributors, anomaly detection, risk scoring, or statistical interpretation.

## Goal

Select analysis methods that match the business objective and produce evidence-backed findings.

## Recommended Analysis Sequence

Use this sequence unless the objective suggests otherwise:

1. Descriptive summary.
2. Trend analysis.
3. Segmentation.
4. Top contributors.
5. Anomaly detection.
6. Risk flags.
7. Recommended actions.

## Descriptive Summary

Compute:

- record count
- date range
- totals
- averages
- min / max
- key status counts

Example:

```text
Total revenue: 1,240,000
Orders: 12,430
Average order value: 99.76
Date range: 2026-05-01 to 2026-05-31
```

## Trend Analysis

Use for time series questions.

Common metrics:

- daily / weekly total
- period-over-period change
- moving average
- growth rate
- spike and drop dates

Report both direction and magnitude:

```text
Revenue increased 8.4% compared with the previous 30-day period.
```

## Segmentation

Group by relevant dimensions:

- channel
- product
- region
- customer segment
- priority
- category
- status

Identify both volume and rate changes.

## Top Contributors

Use top N ranking to explain drivers:

- top products by revenue
- top regions by ticket volume
- top customers by usage
- top categories by error count

Avoid over-explaining tiny contributors.

## Anomaly Detection

Start simple:

- sudden spikes or drops
- values above mean plus 2 standard deviations
- missing days
- unusually high error rate
- repeated duplicates

If data volume is small, avoid strong statistical claims. Say "potential anomaly" instead.

## Risk Flags

Flag items requiring attention:

- severe anomaly
- missing required data
- fast negative trend
- concentration risk
- SLA breach
- inventory below threshold

## Recommendation Rules

Each recommendation must include evidence.

Good:

```text
Investigate June 12 B2B spike because one order contributed 41% of that day’s revenue.
```

Bad:

```text
Improve sales.
```

## Verification Checklist

- [ ] Analysis method matches objective.
- [ ] Findings include supporting numbers.
- [ ] Anomalies are labeled with severity or confidence.
- [ ] Recommendations are tied to evidence.
- [ ] Limitations are explicitly stated.
