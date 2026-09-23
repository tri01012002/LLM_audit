# Data Model

## 1. Scope

The repository must replace the hearing-sheet model with a checklist-oriented audit model. The data model must represent the actual Excel checklist, preserve source traceability, and support the human review workflow.

## 2. Core entity: ChecklistItem

```python
class ChecklistItem:
    item_id: str
    main_question_id: str
    category: str
    question: str

    partner_answer: str
    partner_comment: str

    confirmation_required: str | None
    confirmation_request: str | None

    corrective_action_required: str | None
    corrective_action_request: str | None

    corrective_action_response: str | None

    result_classification: str | None
    auditor_comment: str | None

    source_sheet: str
    source_row: int
    source_columns: list[str]
    source_cell_refs: list[str]
```

### Notes

- `item_id` should follow the checklist’s natural item numbering, for example `13-02`.
- `source_sheet`, `source_row`, and `source_columns` keep the origin of every item.
- `source_cell_refs` should preserve precise locations such as `E42`, `F42`, `G42`, `H42`.
- The model should also retain unparsed raw values when needed for audit review.

## 3. Workbook-level representation

```python
class ChecklistWorkbook:
    workbook_name: str
    partner_company: str | None
    sheet_names: list[str]
    items: list[ChecklistItem]
    validation_warnings: list[str]
    metadata: dict[str, str]
```

This ensures the app can show one workbook summary, count of total items, answered count, and outstanding count.

## 4. Deterministic rule result

```python
class RuleResult:
    item_id: str
    status: str
    severity: str | None
    reason: str | None
    rule_id: str
    is_blocking: bool = False
    evidence_refs: list[str]
```

Possible status values include:

- `SUPPORTED`
- `NEEDS_INFORMATION`
- `NEEDS_CONFIRMATION`
- `POSSIBLE_CONTRADICTION`
- `UNCLEAR`
- `UNKNOWN`

## 5. AI analysis output

```python
class AIAnalysisResult:
    item_id: str

    current_state: str
    information_sufficiency: str
    issue_type: str | None
    evidence: list[str]

    risk: str | None
    additional_confirmation_required: bool
    additional_confirmation_reason: str | None
    confirmation_request_draft: str | None

    corrective_action_required: bool | None
    improvement_proposal: str | None
    auditor_comment_draft: str | None

    confidence: str
    source_item_id: str
```

### Allowed values

`information_sufficiency` may be:

- `SUFFICIENT`
- `PARTIALLY_SUFFICIENT`
- `INSUFFICIENT`
- `UNKNOWN`

`issue_type` may be:

- `NONE`
- `MISSING_INFORMATION`
- `AMBIGUITY`
- `CONTRADICTION`
- `PARTIAL_IMPLEMENTATION`
- `OTHER`

## 6. Auditor review records

```python
class ReviewRecord:
    item_id: str
    ai_value: str | None
    auditor_final_value: str | None
    review_status: str
    reviewer: str | None
    review_timestamp: str | None
    edit_reason: str | None
```

Possible `review_status` values:

- `ACCEPTED`
- `EDITED`
- `REJECTED`
- `ON_HOLD`

## 7. Approved result

```python
class ApprovedResult:
    item_id: str
    assessment: str | None
    confirmation_request: str | None
    corrective_action: str | None
    classification: str | None
    auditor_note: str | None
    final_status: str
```

This object represents the state after the auditor acts as the final decision-maker.

## 8. Evidence object

```python
class EvidenceRef:
    type: str
    source: str
    cell_ref: str | None
    text: str
```

Examples:

- `partner_answer`
- `partner_comment`
- `rule_check`
- `historical_reference`

## 9. Traceability requirement

Every normalized item must retain a direct mapping back to the original workbook:

```text
item_id = "13-02"
source_sheet = "A. Security Controls"
source_row = 42
source_columns = ["E", "F", "G", "H", "I", "J"]
```

This is required for auditability and for `根拠を確認する` evidence review.

## 10. Design constraints

- The model must not silently mix facts, inferences, and recommendations.
- The AI must produce structured output only.
- The workflow must preserve the original Excel structure for export.
- The review state must remain separate from raw source data.
