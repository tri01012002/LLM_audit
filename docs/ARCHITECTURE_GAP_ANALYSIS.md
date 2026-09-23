# Architecture Gap Analysis

## 1. Repository audit summary

The current repository is a prototype for a hearing-sheet workflow, not an AI audit assistant for an answered security checklist. The codebase centers on:

- `rikai_prototype/app.py` entry point that launches a Streamlit chat experience
- `ui/chat_app.py` which orchestrates a partner-chat demo and hearing-sheet review flow
- `agents/hearing_sheet_agent.py` for hearing-sheet construction and revision
- `agents/analysis_agent.py` for generic partner-answer analysis
- `agents/report_agent.py` for narrative report generation
- `storage/local_store.py` for simulated partner inbox/outbox and local JSON/XLSX persistence
- `ingestion/xlsx_extractor.py` for a text-extraction pass that converts spreadsheet content into markdown-like text
- `core/schemas.py` for hearing-sheet models and generic analysis output

This is a valid prototype for a conversational questionnaire workflow, but it does not match the requested product direction: an AI Audit Assistant that works from an already answered checklist and supports human auditor approval.

## 2. Current architecture

```text
Auditor
 → Hearing Sheet generation
 → Partner communication
 → Partner response
 → AI analysis
 → Report generation
```

### Current behavior

The repository’s actual flow is:

1. Auditor enters a survey/instruction.
2. The app creates a hearing sheet from raw text or uploaded files.
3. A simulated partner or inbox/outbox workflow receives the sheet.
4. A partner returns an answer file.
5. The system analyzes the answer using `analysis_agent.py`.
6. `report_agent.py` generates a narrative report.
7. The auditor reviews the result in the chat UI.

This approach is product-incorrect for the client brief because the real workflow starts from a completed governance/security checklist, not a questionnaire-generation conversation.

## 3. Required architecture

```text
Answered Checklist
 → Excel Parser
 → Normalized Checklist Items
 → Deterministic Business Rules
 → AI Semantic Analysis
 → AI Draft Assessment
 → Auditor Review
 → Approved Result
 → Excel Export
```

### Required behavior

1. The system ingests an already answered checklist Excel file.
2. The workbook is parsed and normalized to item-level records with source traceability.
3. Deterministic rules flag missing/contradictory/ambiguous data.
4. The AI performs only semantic interpretation of ambiguous or complex items.
5. The AI produces draft assessment/proposals, not final decisions.
6. The human auditor reviews, edits, and approves each item.
7. Approved result is exported back to the Excel structure without losing traceability.

## 4. Gap analysis

### A. Product/UX mismatch

The current UI is chat-first and partner-centric. The required UI is workflow-oriented and auditor-centric. The user should start with file upload and analysis dashboard, not with message prompts or partner simulation.

### B. Data-model mismatch

The model in `core/schemas.py` is built around `HearingSheet`, `SheetTable`, and `QARow` abstractions. This is appropriate for a textual survey sheet, but not for a real audit checklist with:

- main questions and detailed checklist items
- answer states `〇`, `△`, `✕`, `－`
- partner answer and partner comment separation
- confirmation, corrective action, and result-classification fields
- source row/column traceability

### C. Workflow mismatch

The current flow exposes a partner-message model and report generation. The required flow explicitly adds:

- Excel ingestion as the first-class entry point
- deterministic rule engine
- AI semantic analysis over selected cases only
- auditor review and approval gate
- export back to the client’s Excel structure

### D. Business-rule gap

There is no deterministic rule engine in the repo. The project currently relies on a generic LLM analysis pass without explicit rules for:

- missing answer
- missing reason
- contradiction of positive answer with explanatory comment
- not-applicable cases with insufficient explanation
- ambiguous language such as “原則”, “順次対応”, “予定”, etc.

### E. Evidence and non-hallucination gap

The current prompts and schemas do not enforce a separation between:

- facts from partner data
- inferences from those facts
- recommendations

The repo also does not enforce evidence traceability back to source Excel cells/rows.

### F. Evaluation gap

There is no framework for AI-vs-human audit evaluation, time measurement, or confirmation quality measurement. The current repository is optimized for demo storytelling instead of demo usefulness.

## 5. Components to KEEP

These components are reusable and should be preserved or adapted:

- Excel parsing utilities in `ingestion/xlsx_extractor.py`
- local persistence patterns in `storage/local_store.py`
- configuration abstraction in `configs.py`
- model/provider abstraction potential in `core/llm.py`
- structured-output patterns in `core/schemas.py`
- general local storage and session concepts

## 6. Components to MODIFY

These are core components that must be redesigned to fit the required product:

- `core/schemas.py`: replace hearing-sheet-only models with audit checklist models and AI analysis contracts
- `agents/analysis_agent.py`: refocus from generic hearing-sheet analysis to checklist semantic analysis
- `ui/chat_app.py`: replace chat-centric flow with upload + analysis dashboard + auditor review screens
- `ingestion/xlsx_extractor.py`: redesign into a true checklist parser and row-level mapper
- `prompts/*`: rewrite system prompts to emphasize evidence-grounded, deterministic-first analysis
- `storage/local_store.py`: introduce checklist persistence, audit review state, and approved export support

## 7. Components to REMOVE

These are not central to the required product and should be demoted or removed from the primary demo flow:

- partner-tagging simulation
- @Partner chat flow as the primary path
- inbox/outbox simulation as the primary business workflow
- hearing-sheet generation as the product center
- generic report generation without auditor gates
- free-form chat-first UI

These may remain temporarily for backward compatibility or demo fallback, but they are not the client’s required path.

## 8. Components to CREATE

The following are required additions:

- `core/business_rules.py` for deterministic evaluation logic
- normalized checklist data model with source traceability
- review/approval state model for each item and overall checklist
- AI output schema for current state, evidence, risk, confirmation request, improvement proposal
- Excel export layer that writes approved values back into the original workbook structure
- evaluation metrics layer for efficiency and quality comparison
- Microsoft-first architecture decision document

## 9. Refactor decision

The repository should not be rewritten blindly. The correct strategy is to preserve reusable parsing, persistence, and provider-facing patterns while replacing the product center from “chat-based hearing sheet” to “audit-checklist intelligence with human review.”

This means the refactor is architectural as much as it is code-level. The code currently solves the wrong problem; the replacement must solve the actual business problem described by the client.

## 10. Conclusion

The repository is not failing due to a single bug; it is built around the wrong product concept. The required work is a product refactor, not a narrow bug fix. The target system must be evidence-grounded, deterministic-first, auditor-controlled, and Excel-centric.

No implementation should begin before the architecture and data contracts are defined in the required documents.
