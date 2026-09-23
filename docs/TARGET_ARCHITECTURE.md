# Target Architecture

## 1. Product objective

The target product is an AI Audit Assistant that helps a human security auditor assess a completed checklist, identify gaps and contradictions, draft a risk-based assessment, and support auditor review and approval before export back to Excel.

The human auditor remains the final authority. The AI assists, but does not replace the reviewer.

## 2. High-level system architecture

```text
                    ┌───────────────────┐
                    │   Excel Checklist │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   Excel Parser     │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Normalize Items    │
                    └─────────┬─────────┘
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
        ┌─────────────────┐       ┌─────────────────┐
        │ Business Rules  │       │ Reference Data  │
        │ deterministic   │       │ optional        │
        └────────┬────────┘       └────────┬────────┘
                 │                         │
                 └────────────┬────────────┘
                              ▼
                    ┌───────────────────┐
                    │   AI Analysis      │
                    └─────────┬─────────┘
                              ▼
                    ┌───────────────────┐
                    │ AI Draft Results   │
                    └─────────┬─────────┘
                              ▼
                    ┌───────────────────┐
                    │ Auditor Review     │
                    └─────────┬─────────┘
                              ▼
                    ┌───────────────────┐
                    │ Approved Results   │
                    └─────────┬─────────┘
                              ▼
                    ┌───────────────────┐
                    │ Excel Export       │
                    └───────────────────┘
```

## 3. Core principles

1. Evidence-first: every conclusion must tie to source data.
2. Deterministic before AI: rules process missing/ambiguous/contradictory data first.
3. Human approval final: the auditor chooses the final classification and wording.
4. Traceability: every normalized item keeps row/column/source metadata.
5. Structured outputs only: avoid free-form narrative as the primary contract.
6. Simplicity: no unnecessary microservices or heavy orchestration.

## 4. Functional modules

### 4.1 Excel parser

Purpose: load workbook, identify the checklist structure, and map source cells to normalized records.

Responsibilities:

- accept uploaded `.xlsx` and `.xlsm`
- preserve workbook metadata and source worksheets
- detect header rows and source cell references
- map the relevant columns for partner answer, comments, and result fields
- keep raw cell content for traceability

### 4.2 Normalized checklist model

Purpose: convert spreadsheet data into a structured internal representation of each item.

Key features:

- item-level identification
- question and category linkage
- partner answer/comment separation
- result field and auditor notes separation
- row/column traceability
- ability to round-trip back to Excel

### 4.3 Deterministic business rules

Purpose: flag issues before any LLM reasoning.

Examples:

- missing answer
- missing reason when answer is non-fully-positive
- potential contradiction between answer and comment
- ambiguous not-applicable explanation
- insufficient or vague phrasing

The purpose is not to make a final audit judgment, but to mark items that need AI or auditor review.

### 4.4 AI semantic analysis

Purpose: interpret ambiguous, contradictory, or context-heavy items only when needed.

The AI is responsible for:

- assessing current state
- assessing information sufficiency
- identifying risk and ambiguity
- drafting confirmation questions
- recommending improvement actions

It is not responsible for making final audit classification decisions.

### 4.5 Auditor review and approval

Purpose: let the real decision-maker validate and edit AI suggestions.

The auditor can:

- accept
- edit
- reject
- hold
- approve final summary

### 4.6 Excel export

Purpose: write the approved values back into the client’s spreadsheet structure while preserving original evidence and unapproved fields.

## 5. Key data flow

```text
Upload answered checklist
 → parser validates workbook
 → normalize rows into ChecklistItem objects
 → run deterministic checks
 → pass flagged items to AI semantic analysis
 → produce structured draft results
 → auditor reviews and edits each item
 → approved values saved into review state
 → Excel export writes approved fields back to workbook
```

## 6. Non-goals for this PoC

The system should not center on:

- partner messaging
- generic chat-based questionnaire generation
- iterative partner polling
- hearing-sheet generation as a product output
- autonomous agent loops for sending emails or messages

These may exist in legacy code or for compatibility, but they must not be the core of the demo.

## 7. Recommended implementation boundary

The PoC should keep the architecture simple enough to demonstrate value quickly:

- one backend service
- single app or UI entry point
- local structured data and persistence
- optional provider abstraction for LLM selection
- no microservices unless required later

## 8. Success criteria for the target system

A demo is successful when it can:

1. upload an answered checklist Excel file
2. normalize all 128 checklist items
3. run deterministic checks
4. surface AI-assisted analysis for relevant items
5. show risk, evidence, and additional-confirmation needs
6. allow auditor review and editing
7. export an approved Excel result
8. show evaluation metrics

This is the business value the client wants to validate.
