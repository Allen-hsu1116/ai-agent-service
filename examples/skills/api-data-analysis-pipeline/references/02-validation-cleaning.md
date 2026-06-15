# Module 02: Validation and Cleaning

Load this module when the task needs schema checks, missing value handling, duplicate handling, type conversion, or normalization.

## Goal

Turn raw API responses into reliable analysis-ready records.

## Validation Checklist

Check before analysis:

- Required fields exist.
- Field types match the expected schema.
- Date fields can be parsed.
- Numeric fields can be converted safely.
- IDs are unique or duplicates are explainable.
- Missing values are counted.
- Categorical values are normalized.

## Cleaning Steps

1. Parse timestamps into a consistent timezone.
2. Convert numeric strings to numbers.
3. Normalize category labels.
4. Remove or flag duplicate records.
5. Keep counts for dropped, repaired, and unknown records.
6. Preserve raw values when transformation is uncertain.

## Missing Data Policy

- If a field is optional, report missing count.
- If a field is required for the objective, stop or label the analysis as limited.
- Do not silently impute values unless the user explicitly asks for it or the method is documented.

## Duplicate Policy

Prefer deduplication by stable ID, for example:

```text
order_id
ticket_id
customer_id + timestamp + event_type
```

Report:

- duplicate count
- deduplication key
- whether duplicates were removed or only flagged

## Schema Drift Handling

If expected fields are missing or renamed:

1. Report the missing fields.
2. Check whether safe aliases exist.
3. Avoid guessing if aliases are ambiguous.
4. Ask for updated API schema when necessary.

## Data Quality Output

Include a concise quality summary:

```markdown
## 資料品質檢查

- Required fields: pass
- Missing values: 23 rows missing `customer_segment`, labeled as `unknown`
- Duplicates: 4 duplicate `order_id` rows removed
- Cleaning performed: parsed timestamps, converted `amount` to number, normalized channel labels
```

## Verification Checklist

- [ ] Required fields checked.
- [ ] Missing values counted.
- [ ] Duplicates handled.
- [ ] Type conversions documented.
- [ ] Any limitation is visible in the final report.
