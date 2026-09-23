# AI Analysis Specification

## 1. Role of the AI

The AI is not the final decision-maker. Its responsibility is to analyze only the items that require semantic interpretation after deterministic rules are applied.

The AI does not decide the final audit result on its own. It produces a structured draft that the human auditor may accept, edit, reject, or hold.

## 2. Inputs

The AI receives:

- normalized checklist item
- raw partner answer
- raw partner comment
- business-rule outputs
- optionally reference data if approved by client
- historical examples only as non-binding guidance

## 3. Required outputs

The AI must answer these questions for each item:

1. What is the current state?
2. Is the partner answer sufficiently supported?
3. Is there ambiguity?
4. Is there contradiction?
5. What evidence supports the conclusion?
6. Is additional confirmation required?
7. What risk can be reasonably inferred?
8. What improvement proposal is appropriate?
9. What information is still missing?

## 4. Evidence hierarchy

The AI must explicitly distinguish:

```text
FACT
    What the Partner explicitly said

INFERENCE
    What can reasonably be inferred from the Partner information

RECOMMENDATION
    What should be improved
```

### Example

```text
FACT:
Partner states that MFA is implemented only on some systems.

INFERENCE:
The implementation scope appears incomplete.

RISK:
Incomplete MFA coverage may leave some authentication paths less protected.

RECOMMENDATION:
Review the remaining systems and establish a plan to expand MFA coverage.
```

## 5. Hallucination policy

The AI must never invent:

- certifications
- policies
- incidents
- vulnerabilities
- controls
- regulations
- standards
- evidence
- historical decisions
- customer requirements

If the evidence is insufficient, the output must use:

- `UNKNOWN`
- `NEEDS_CONFIRMATION`

The model must not produce confident recommendations from missing data.

## 6. Structured output contract

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

This structure prevents unsupported claims by requiring explicit evidence and keeping the output narrowly scoped.

## 7. Decision boundaries

The AI may do semantic analysis, but it may not finalize:

- result classification
- final corrective action request
- final audit verdict
- final export values

Those remain under auditor authority.

## 8. Handling unsupported inference

If the raw partner response is vague or incomplete, the AI must return:

- `information_sufficiency = UNKNOWN` or `INSUFFICIENT`
- `additional_confirmation_required = true`
- `confirmation_request_draft` containing a precise question to ask the partner or auditor

## 9. Quality expectation

The AI should prefer:

- precise evidence references
- narrow, defensible inferences
- clear questions when the evidence is insufficient
- concrete but non-final recommendations

It should avoid broad speculative statements.

## 10. Final rule

AI analysis is useful only when it is grounded in the actual checklist evidence and remains subordinate to the human auditor’s final judgement.
