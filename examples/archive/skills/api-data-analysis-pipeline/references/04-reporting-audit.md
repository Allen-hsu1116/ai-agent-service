# Module 04: Reporting and Audit

Load this module when final response, audit trail, persistence, or reproducibility notes are needed.

## Goal

Produce a clear final report and preserve safe metadata for later inspection.

## Final Report Must Include

- analysis objective
- API source and date range
- filters used
- record count
- data quality notes
- key metrics
- main findings
- anomalies and risks
- recommended actions
- limitations and assumptions

## Evidence Rules

Every important claim should include evidence:

- count
- percentage
- time range
- segment name
- comparison baseline

Avoid unsupported claims.

## Safe Source Description

Good:

```text
API: /v1/orders
Date range: 2026-05-01 to 2026-05-31
Filters: status=paid
```

Bad:

```text
API: https://api.example.com/v1/orders?token=secret-token
```

## Audit Metadata

If persistence is supported, store safe metadata:

```json
{
  "objective": "Analyze revenue trend and anomalies",
  "api_path": "/v1/orders",
  "date_range": "2026-05-01 to 2026-05-31",
  "filters": {
    "status": "paid"
  },
  "records_analyzed": 12430,
  "loaded_skill_modules": [
    "references/01-api-retrieval.md",
    "references/02-validation-cleaning.md",
    "references/03-analysis-methods.md",
    "templates/analysis-report.md"
  ]
}
```

Do not store:

- API token
- bearer header
- cookies
- passwords
- raw personal data unless explicitly required and allowed

## Report Quality Checklist

- [ ] Findings are concise.
- [ ] Evidence is included.
- [ ] Data quality issues are visible.
- [ ] Recommendations are actionable.
- [ ] Assumptions and limitations are stated.
- [ ] Secrets are not exposed.
