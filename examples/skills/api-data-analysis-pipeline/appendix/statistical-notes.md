# Appendix: Statistical Notes

Load this appendix only when the user asks for deeper statistical explanation, confidence scoring, or anomaly methodology details.

## When to Load

- The user asks how anomaly thresholds were chosen.
- The user wants confidence levels or statistical caveats.
- The analysis involves small samples or noisy time series.
- A stakeholder needs methodology details.

## Simple Anomaly Heuristics

For early MVP analysis, prefer explainable heuristics:

- value greater than mean plus 2 standard deviations
- value lower than mean minus 2 standard deviations
- sudden day-over-day change above a defined threshold
- missing expected time bucket
- category share changes above a defined threshold

## Caveats

- Small sample sizes make standard deviation unstable.
- Seasonality can make simple thresholds misleading.
- One-time business events may look like anomalies but be valid.
- Missing or delayed API data can create false drops.

## Reporting Language

Use cautious language when confidence is limited:

```text
This is a potential anomaly, not a confirmed incident, because the sample size is small and no seasonality adjustment was applied.
```

Avoid overstating:

```text
This proves fraud occurred.
```
