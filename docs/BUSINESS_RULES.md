# Business Rules Specification

## 1. Purpose

The deterministic business rules must run before the AI semantic analysis. They are intended to identify explicit missing information, unlikely consistency issues, and items that require auditor or AI review.

These rules are a PoC. They must be clearly marked as configurable until the client confirms the final mapping.

## 2. Rule 01 — Missing answer

If:

```text
E is empty
```

then:

```text
status = NEEDS_INFORMATION
```

### Notes

The AI should not invent an answer for an empty field. The item should be queued for clarification or auditor review.

## 3. Rule 02 — Missing reason

If:

```text
E = △ / ✕ / －
AND
F is empty
```

then:

```text
status = NEEDS_CONFIRMATION
reason = "回答理由が未記入のため、追加確認が必要です。"
```

### Notes

This is an example rule and must be treated as configurable until the client confirms the real business rule set.

## 4. Rule 03 — Possible contradiction

If:

```text
E = 〇
```

but the partner comment indicates partial implementation, exception, legacy-system limitation, planned implementation, or another condition that is inconsistent with full implementation:

```text
status = POSSIBLE_CONTRADICTION
```

### Notes

This should trigger AI semantic review. The rule itself is deterministic; the AI decides the degree and form of the contradiction.

## 5. Rule 04 — Not applicable

If:

```text
E = －
```

then the system should inspect whether the explanation in `F` sufficiently explains why the control is not applicable.

Possible outcomes:

- `SUPPORTED`
- `UNCLEAR`
- `NEEDS_CONFIRMATION`

### Notes

Do not automatically reject every `－`. The explanation quality matters.

## 6. Rule 05 — Ambiguous language

The system should detect language such as:

- 原則
- 一部
- 検討中
- 順次対応
- 予定
- 必要に応じて
- 適切に管理
- 基本的に
- 原則として
- 場合による

These phrases are not automatically failures, but they trigger semantic analysis when they may materially affect whether the control is actually implemented.

## 7. Rule 06 — Unsupported assumptions

The business rules engine must not assume:

- a control exists because the company is large
- a control is present simply because an answer uses a positive symbol
- a risk is severe without evidence

All rule outputs must remain evidence-based and traceable.

## 8. Output contract for rules

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

## 9. Failure-handling policy

When a rule cannot determine sufficiency because the evidence is missing or unclear, it must return:

- `UNKNOWN`
- `NEEDS_CONFIRMATION`

Not a confident negative classification.

## 10. Rule configuration policy

The business rules are intentionally configurable until the client confirms the final jurisdictional logic. They must be represented as a rule list, not as hardcoded hidden assumptions inside the LLM prompt.
