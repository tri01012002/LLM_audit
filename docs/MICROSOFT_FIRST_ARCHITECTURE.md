# Microsoft-First Architecture Assessment

## 1. Purpose

The client explicitly asked to evaluate whether the existing Microsoft environment should be considered before defaulting to a custom LLM backend. This document compares the likely operating models for the audit assistant.

## 2. Decision framing

The architecture choice must be based on:

- tenant security and governance
- file handling in Excel / Microsoft 365
- the need for auditor review and approval
- evidence traceability to source worksheets
- low-friction deployment in the client environment

The guidance is not to assume Option C is the default. Microsoft-first maturity must be evaluated against the actual client environment.

## 3. Option A — Microsoft 365 / Copilot-first

```text
Microsoft 365
      ↓
Excel
      ↓
Copilot / Microsoft AI capabilities
      ↓
AI analysis
      ↓
Auditor review
```

### This option may be suitable when

- the client already uses Microsoft 365 heavily
- Excel is the primary source of truth
- the organization wants to minimize custom application work
- the required AI capability is mostly summarization, drafting, and review assistance

### Risks / unknowns

- direct Copilot capability for structured audit logic and row-level evidence extraction must be verified with the client
- governance and data boundaries may be more tightly controlled than a custom app
- output quality and reproducibility may vary depending on tenant configuration

Status: TO_BE_VERIFIED_WITH_CLIENT

## 4. Option B — Microsoft 365 + custom AI backend

```text
Microsoft 365 / Excel
      ↓
Integration layer
      ↓
Custom AI analysis service
      ↓
Auditor review
      ↓
Excel
```

### This is the most balanced path for this PoC

This architecture provides:

- Excel as the authoritative source
- custom logic for deterministic rules and item normalization
- AI analysis via configurable providers
- clear separation between AI draft and auditor approval
- easier evaluation and logging than a pure Copilot-only flow

### Advantages

- better model control
- easier auditing and prompt versioning
- better candidate evaluation
- more explicit governance boundaries
- easier export and validation logic

### Disadvantages

- more implementation work
- needs explicit integration layer to Excel and M365
- must manage authentication and authorization carefully

## 5. Option C — Fully custom application

```text
Excel upload
      ↓
Custom backend
      ↓
LLM
      ↓
Custom UI
      ↓
Excel export
```

### This is useful when

- the client’s environment does not support a Microsoft-first integration
- custom review logic must be tightly controlled
- the product must be portable beyond the current tenant

### Advantages

- full control over architecture and data flow
- easiest to prototype and evaluate for research
- simplest to run in a lab or demo environment

### Disadvantages

- more development effort
- less natural Microsoft 365 compatibility
- extra security and deployment burden
- more risk of recreating a tool that the client already has in-house

## 6. Comparison table

| Dimension | Option A: Copilot-first | Option B: M365 + custom AI | Option C: Custom app |
|---|---|---|---|
| Security | Good if tenant policy is aligned; verify controls | Strong, configurable | Strong but depends on implementation |
| Authentication | Microsoft identity | Microsoft identity + custom boundary | Custom identity model |
| Authorization | Tenant-level and app-level policy | Clear custom boundaries | Full responsibility |
| Data governance | Strong if within M365 | Strong with custom guardrails | Must be designed from scratch |
| Excel integration | Excellent | Excellent | Requires custom export/import |
| Auditability | Moderate to strong depending on platform | Strong | Strong |
| Deployment complexity | Low to medium | Medium | Medium to high |
| Development effort | Low | Medium | High |
| Extensibility | Constrained by platform | High | High |
| Model control | Low to medium | High | High |
| Evaluation capability | Somewhat limited | Strong | Strong |
| Cost | Possibly lower if already licensed | Moderate | Moderate to high |
| Client compatibility | High in M365 environments | High | Medium |

## 7. Recommended direction for this PoC

For the prototype, the preferred direction is Option B unless the client confirms that Option A already covers the required structured audit workflow.

Why:

- the business problem is a structured checklist workflow
- the deterministic logic and review gate require explicit control
- the AI must produce evidence-based draft results and remain subordinate to auditor approval
- a custom backend gives clearer evaluation and easier export logic

## 8. Important caveat

The system must not claim that Microsoft Copilot or Microsoft AI is performing a task unless the client has verified the actual capability in their tenant.

Where the capability is uncertain, it must be labelled as:

`TO_BE_VERIFIED_WITH_CLIENT`

## 9. Final recommendation

Use a Microsoft-first approach as the design constraint, but keep the actual implementation provider-abstracted so the system can run with:

- Microsoft 365 integration when available
- custom AI backend when required
- a configurable provider layer for future extension

This avoids hard-coding a single architecture while staying aligned with the client environment.
