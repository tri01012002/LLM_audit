# Implementation Plan

## Phase 1 — Repository audit and architecture documentation

Status: completed for the required documents.

Required artifacts:

- ARCHITECTURE_GAP_ANALYSIS.md
- TARGET_ARCHITECTURE.md
- MICROSOFT_FIRST_ARCHITECTURE.md
- DATA_MODEL.md
- AI_ANALYSIS_SPEC.md
- BUSINESS_RULES.md
- EVALUATION_FRAMEWORK.md
- UI_SPEC.md

## Phase 2 — Normalized checklist data model

Tasks:

- define `ChecklistItem` model
- define `ChecklistWorkbook` model
- define `AIAnalysisResult` and review records
- maintain source traceability and row/column metadata

## Phase 3 — Excel ingestion and validation

Tasks:

- redesign `xlsx_extractor.py` around the real checklist table structure
- read workbook metadata and preserve sheet mapping
- validate workbook headers and warning states
- detect missing/invalid fields early

## Phase 4 — Deterministic business rule engine

Tasks:

- add `core/business_rules.py`
- implement missing-answer and missing-comment checks
- implement not-applicable and ambiguity detection rules
- keep all rules explicit, configurable, and evidence-based

## Phase 5 — AI analysis engine

Tasks:

- implement provider abstraction for LLM calls
- run AI only for flagged or complex items
- produce structured evidence-grounded analysis
- avoid unsupported recommendations

## Phase 6 — Structured AI output

Tasks:

- finalize contract for `AIAnalysisResult`
- validate output with schema enforcement
- enforce evidence and risk separation
- prevent silent mixing of fact/inference/recommendation

## Phase 7 — Auditor review UI

Tasks:

- replace chat-first flow with upload and dashboard views
- create the three-panel auditor review screen
- add evidence-view, edit, approve, hold, reject actions
- persist review decision state

## Phase 8 — Approved result persistence

Tasks:

- store approved values and review metadata
- track item-level state and final classification
- keep raw original data immutable

## Phase 9 — Excel export

Tasks:

- write approved values back to the original workbook columns
- preserve original questions and comments
- mark unapproved items clearly
- maintain source row mapping

## Phase 10 — Evaluation metrics

Tasks:

- measure time reduction
- measure confirmation quality
- compare AI, auditor, and AI+auditor outcomes
- report results without fake numeric “quality score" fabrication

## Phase 11 — Demo dataset

Tasks:

- create demo cases and evaluation cases separately
- ensure evaluation data remains unseen by the demo logic
- cover missing answer, contradiction, partial implementation, ambiguity, etc.

## Phase 12 — Final polish and demo flow

Tasks:

- ensure the result is clearly auditor-centric
- keep legacy components minimal and not primary
- test the end-to-end upload → analysis → review → export flow

## Final note

The implementation should stay deliberately simple, because the objective is to demonstrate whether AI can meaningfully reduce human auditor workload while preserving human control and evidence quality.
