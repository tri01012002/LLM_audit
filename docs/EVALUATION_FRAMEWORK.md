# Evaluation Framework

## 1. Objective

The PoC must evaluate whether AI can reduce the workload of a real human auditor while delivering usefully structured and evidence-grounded recommendations.

The evaluation framework must permit comparison between:

- human auditor A
- AI draft
- AI + auditor review

## 2. Efficiency metrics

### 2.1 Time reduction

Measure:

- human audit time
- AI-assisted audit time
- analysis time
- proposal-writing time
- review time

Compute:

```text
Time reduction % = ((Human time - AI-assisted time) / Human time) * 100
```

### 2.2 What to separate

The evaluation should separate:

- reading and normalization time
- deterministic-check time
- AI analysis time
- draft generation time
- auditor review time
- final approval time

This prevents a misleading aggregate metric.

## 3. Additional confirmation metrics

Compare:

- Auditor A
- AI
- AI + Auditor

Measure:

- number of confirmation requests
- actually necessary confirmations
- unnecessary confirmations
- missed confirmations

### Purpose

This determines whether the AI is generating useful clarifications or simply noisy prompts.

## 4. Quality evaluation

Compare:

```text
AI conclusion vs Auditor A
```

Categories:

- agreement
- disagreement
- major disagreement

For proposals:

- accepted without modification
- edited
- rejected

### Important rule

Do not invent a fake numerical “AI quality score” without a defined methodology. If a score is used, it must be grounded in explicit evaluation criteria.

## 5. Approval outcome metrics

Track:

- accepted without modification
- edited before approval
- rejected
- held for follow-up

These are useful to show whether the AI draft is operationally valuable.

## 6. Demo evaluation design

The system should separate:

- demo cases
- evaluation cases

The evaluation set must be unseen. It must not overlap with the few-shot or demo examples used for prompt testing.

## 7. Data collection requirements

For each item, record:

- item id
- source worksheet and row
- AI draft content
- auditor edit status
- final approved value
- time taken
- whether a confirmation was requested
- whether the request was necessary

## 8. Reporting format

A realistic evaluation dashboard should show:

- processing time by phase
- confirmation count by source
- acceptance rate of AI draft
- edit rate of AI draft
- disagreement rate with auditor A
- proportion of items requiring human override

## 9. Final principle

The evaluation is not about whether the AI is “better” in a vague sense. It is about whether the AI reduces the auditor’s workload while preserving audit quality and traceability.
