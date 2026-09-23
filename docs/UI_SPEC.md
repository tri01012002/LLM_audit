# UI Specification

## 1. Primary UI model

The primary UI is workflow-oriented, not chat-centric. It is designed around the auditor’s review workflow rather than partner communication.

## 2. Screen 1 — Upload

```text
情報セキュリティチェック支援

① 監査票登録 → ② 分析 → ③ 確認 → ④ 出力

チェックリストを登録してください

[ Excelファイルを選択 ]

対象企業：...
チェック項目：128件
回答済み：...
未回答：...

[ 分析を開始する ]
```

### Required data shown

- filename
- partner/company name if available
- total checklist-item count
- answered count
- unanswered count
- workbook validation warnings

## 3. Screen 2 — Analysis dashboard

```text
分析結果

128 items

要対応
確認推奨
問題なし
未回答
```

### Required behavior

- show AI review-priority statuses
- do not present them as official final DLN classifications unless confirmed
- allow filters such as:
  - 要対応
  - 確認推奨
  - すべて
- show category-level summary if category metadata exists

## 4. Screen 3 — Auditor review panel

```text
┌─────────────────────────────────────────────────────────────┐
│ Checklist Item │ Partner Information │ AI Analysis           │
├────────────────┼────────────────────┼───────────────────────┤
│ 13-②           │ Question            │ Current State         │
│ MFA             │ Answer: △           │ ...                   │
│                 │                    │ Risk                  │
│ 17-③           │ Comment             │ ...                   │
│                 │                    │ Improvement Proposal  │
│ 21-②           │                    │ ...                   │
│                 │                    │ Evidence               │
│                 │                    │                       │
│                 │                    │ [根拠を確認する]       │
│                 │                    │ [承認]                 │
│                 │                    │ [修正]                 │
│                 │                    │ [保留]                 │
└─────────────────────────────────────────────────────────────┘
```

### Left panel

- item id
- question
- category
- status

### Center panel

- answer
- partner comment
- corrective response if available

### Right panel

- current assessment
- issue
- risk
- additional confirmation information
- improvement proposal
- evidence
- confidence

## 5. Evidence view

When the auditor clicks `根拠を確認する`, show:

```text
チェック項目
回答
調達先コメント

AIが参照した情報
----------------
Evidence 1
Evidence 2

評価基準
----------------
Only if an actual approved criterion exists

過去提言
----------------
Only if historical reference exists
```

The evidence source must not be invented.

## 6. Review actions

Each AI result must support:

- [AI Draft]
- [編集]
- [承認]
- [保留]
- [却下]

Track the audit metadata:

- `ai_value`
- `auditor_final_value`
- `review_status`
- `reviewer`
- `review_timestamp`
- `edit_reason`

Allowed review statuses:

- `ACCEPTED`
- `EDITED`
- `REJECTED`
- `ON_HOLD`

## 7. UI constraints

- no chat-first interface as the main demo path
- no implicit partner simulation as the main workflow
- maintain clear separation between raw source data and review output
- provide immediate readout of risky or incomplete items
- make auditability obvious to the human reviewer
