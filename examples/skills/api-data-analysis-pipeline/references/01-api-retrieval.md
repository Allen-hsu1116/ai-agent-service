# Module 01: API Retrieval

Load this module when the task needs API request planning, authentication context, pagination, retries, or endpoint validation.

## Goal

Retrieve data from a read-only API safely and reproducibly.

## Required Inputs

- `${API_BASE_URL}`
- `${API_ENDPOINT}`
- `${AUTH_CONTEXT}` without secret values
- `${DATE_RANGE}`
- `${FILTERS}`
- Pagination style, if known

## Request Planning Steps

1. Identify endpoint and HTTP method.
2. Confirm the request is read-only.
3. Define query params.
4. Define timeout and retry policy.
5. Define pagination strategy.
6. Define expected response shape.

## Pagination Patterns

Common patterns:

- `page` + `page_size`
- `offset` + `limit`
- `next_page_token`
- `cursor`
- response `next` URL

Always stop if:

- no next cursor exists
- max page guard is reached
- API returns repeated cursor
- API returns non-success status

## Safe Error Reporting

Report:

- HTTP status code
- safe error summary
- endpoint path without secrets
- retry attempts used

Do not report:

- bearer token
- cookies
- API key
- full signed URLs

## Example Request Plan

```json
{
  "endpoint": "/v1/orders",
  "method": "GET",
  "params": {
    "start_date": "${START_DATE}",
    "end_date": "${END_DATE}",
    "page_size": 500
  },
  "pagination": "next_page_token",
  "timeout_seconds": 30,
  "max_retries": 3,
  "max_pages": 100
}
```

## Retrieval Checklist

- [ ] Request is read-only.
- [ ] Query params match objective.
- [ ] Pagination strategy is defined.
- [ ] Timeout and retry policy are defined.
- [ ] Secrets are not logged.
- [ ] Raw response shape is checked before analysis.
