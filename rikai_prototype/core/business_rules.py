from __future__ import annotations

from typing import Any

VAGUE_PATTERNS = [
    "原則", "一部", "検討中", "順次対応", "必要に応じて", "適切に管理",
    "基本的に", "場合による", "随時", "要検討", "可能な範囲", "問題ありません",
    "問題なし", "yes", "done", "implemented", "対応済み",
]
EXPLICIT_INCOMPLETENESS_PATTERNS = [
    "未実施", "実施していない", "まだ実施", "未導入", "導入していない",
    "未完了", "完了していない", "部分的", "一部のみ", "一部対応",
    "限定的", "条件付き", "例外", "対象外", "対応予定", "実施予定",
    "今後対応", "将来対応", "planned", "not implemented", "not yet implemented",
    "partially implemented", "partial", "exception", "under review",
]
BENIGN_REVIEW_PATTERNS = [
    "定期的にレビュー", "年次レビュー", "レビューを実施", "review is performed",
    "review is conducted", "定期的にチェック", "チェックを実施",
]


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return " ".join(text.split())


def evaluate_business_rules(item: Any) -> dict[str, Any]:
    answer = normalize_text(getattr(item, "partner_answer", ""))
    comment = normalize_text(getattr(item, "partner_comment", ""))
    combined = f"{answer} {comment}".strip()
    lower = combined.lower()
    explicit_incompleteness = any(pattern.lower() in lower for pattern in EXPLICIT_INCOMPLETENESS_PATTERNS)
    benign_review = any(pattern.lower() in lower for pattern in BENIGN_REVIEW_PATTERNS)
    vague_language = any(pattern.lower() in lower for pattern in VAGUE_PATTERNS)

    status = "NORMAL"
    reason = ""
    needs_confirmation = False
    possible_contradiction = False

    if not answer:
        status = "NEEDS_INFORMATION"
        reason = "回答が未記入のため、追加確認が必要です。"
        needs_confirmation = True
    elif answer in {"△", "✕", "－"} and not comment:
        status = "NEEDS_CONFIRMATION"
        reason = "回答理由が未記入のため、追加確認が必要です。"
        needs_confirmation = True
    elif answer in {"✕", "×"}:
        status = "NEEDS_REVIEW"
        reason = "未実施の回答であるため、未実施の理由、影響範囲、改善計画の確認が必要です。"
        needs_confirmation = True
    elif answer == "〇" and explicit_incompleteness and not benign_review:
        status = "POSSIBLE_CONTRADICTION"
        reason = "〇の回答に対して、条件付きや一部対応の表現が含まれており、実装の範囲が不明確です。"
        possible_contradiction = True
        needs_confirmation = True
    elif answer == "－":
        if comment:
            status = "SUPPORTED_NA"
            reason = "該当しない理由が記載されており、対象外の説明として概ね妥当です。"
        else:
            status = "NEEDS_CONFIRMATION"
            reason = "対象外の説明が不足しているため、追加確認が必要です。"
            needs_confirmation = True

    if status == "NORMAL" and vague_language and not benign_review:
        status = "NEEDS_REVIEW"
        reason = "曖昧な表現が含まれており、実装の実態を確認する必要があります。"
        needs_confirmation = True

    if status == "NORMAL" and answer == "△":
        status = "NEEDS_CONFIRMATION"
        reason = "△の回答であるため、実装範囲、未完了部分、根拠資料の確認が必要です。"
        needs_confirmation = True

    return {
        "status": status,
        "reason": reason,
        "needs_confirmation": needs_confirmation,
        "possible_contradiction": possible_contradiction,
        "has_ambiguous_language": vague_language,
        "has_explicit_incompleteness": explicit_incompleteness,
        "answer": answer,
        "comment": comment,
    }
