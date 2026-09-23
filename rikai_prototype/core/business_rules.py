from __future__ import annotations

from typing import Any

AMBIGUOUS_PATTERNS = [
    "原則", "一部", "検討中", "順次対応", "予定", "必要に応じて",
    "適切に管理", "基本的に", "原則として", "場合による", "随時",
    "要検討", "可能な範囲", "一部対応",
]
PARTIAL_PATTERNS = [
    "一部", "一部実施", "一部対応", "限定的", "一部のみ", "一部で",
    "一部のみ実施", "一部を除き", "一部対象", "一部です",
    "一部は", "一部は対応", "条件付き", "一部対応のみ",
]
CONTRADICTION_PATTERNS = [
    "部分的", "予定", "順次", "検討中", "条件付き", "一部のみ",
    "例外", "legacy", "従来", "既存", "対象外", "限定的", "将来",
    "対応予定", "今後対応", "適用外", "一部対応",
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
    elif answer == "〇" and any(p in comment for p in CONTRADICTION_PATTERNS):
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

    if status == "NORMAL" and any(p in comment for p in AMBIGUOUS_PATTERNS):
        status = "NEEDS_REVIEW"
        reason = "曖昧な表現が含まれており、実装の実態を確認する必要があります。"
        needs_confirmation = True

    if status == "NORMAL" and any(p in comment for p in PARTIAL_PATTERNS):
        status = "POSSIBLE_CONTRADICTION"
        reason = "コメントに部分対応の記載があり、実装範囲が不完全かどうかを確認する必要があります。"
        possible_contradiction = True
        needs_confirmation = True

    return {
        "status": status,
        "reason": reason,
        "needs_confirmation": needs_confirmation,
        "possible_contradiction": possible_contradiction,
        "has_ambiguous_language": any(p in comment for p in AMBIGUOUS_PATTERNS),
        "answer": answer,
        "comment": comment,
    }
