from __future__ import annotations

import io
from copy import deepcopy

from openpyxl import Workbook, load_workbook

from core.business_rules import evaluate_business_rules
from core.checklist_models import AIAnalysisResult, ChecklistItem


def analyze_item(item: ChecklistItem) -> AIAnalysisResult:
    rule = evaluate_business_rules(item)
    answer = item.partner_answer or ""
    comment = item.partner_comment or ""
    combined = f"{answer} {comment}".strip()

    if rule["status"] == "NEEDS_INFORMATION":
        return AIAnalysisResult(
            item_id=item.item_id,
            status="NEEDS_INFORMATION",
            current_assessment="回答が未記入のため、補足情報が必要です。",
            evidence=[f"質問: {item.question}", f"回答欄: '{answer}'"],
            issue_or_risk="Missing information",
            confirmation_required=True,
            confirmation_reason="回答が未記入のため、追加確認が必要です。",
            improvement_proposal="該当項目について回答を再確認し、必要に応じて根拠を追加してください。",
            missing_information=["回答欄の記入", "必要に応じて補足理由"],
            confidence="HIGH",
            fact=f"Partner answer: {answer or 'empty'}",
            inference="情報が不足しているため、評価を確定できません。",
            recommendation="回答の再確認と必要な補足の依頼を提案します。",
        )

    if rule["status"] in {"NEEDS_CONFIRMATION", "NEEDS_REVIEW"}:
        return AIAnalysisResult(
            item_id=item.item_id,
            status=rule["status"],
            current_assessment="回答または理由が不十分であり、確認が必要です。",
            evidence=[f"質問: {item.question}", f"コメント: {comment or '未記載'}", f"回答: {answer}"] if comment else [f"質問: {item.question}", f"回答: {answer}"],
            issue_or_risk="Insufficient explanation or ambiguity",
            confirmation_required=True,
            confirmation_reason=rule["reason"] or "追加確認が必要です。",
            improvement_proposal="回答の理由または実装範囲を補足し、必要に応じて証跡を共有してください。",
            missing_information=["実装状況の詳細", "補足理由", "対象範囲"],
            confidence="MEDIUM",
            fact=f"Partner answer: {answer}",
            inference="現時点では説明の十分性が不足しています。",
            recommendation="補足情報を依頼し、回答の正確性を確保してください。",
        )

    if rule["status"] == "POSSIBLE_CONTRADICTION":
        return AIAnalysisResult(
            item_id=item.item_id,
            status="POSSIBLE_CONTRADICTION",
            current_assessment="回答は実施済みと見える一方、コメントに例外や一部対応の表現が含まれており、実装範囲が曖昧です。",
            evidence=[f"質問: {item.question}", f"回答: {answer}", f"コメント: {comment}"],
            issue_or_risk="Possible contradiction between declaration and explanatory text",
            confirmation_required=True,
            confirmation_reason="実装範囲や例外条件が不明確です。",
            improvement_proposal="対象範囲、例外、実装されている対象システム、実施時期を確認してください。",
            missing_information=["例外条件", "対象範囲", "実装済み対象"],
            confidence="MEDIUM",
            fact=f"Partner answer: {answer}",
            inference="コメントから条件付きまたは部分的な対応が想定されます。",
            recommendation="例外条件と実装範囲の明確化を依頼してください。",
        )

    if rule["status"] == "SUPPORTED_NA":
        return AIAnalysisResult(
            item_id=item.item_id,
            status="SUPPORTED_NA",
            current_assessment="対象外とする説明が記載されており、概ね妥当と判断できます。",
            evidence=[f"質問: {item.question}", f"回答: {answer}", f"コメント: {comment}"],
            issue_or_risk=None,
            confirmation_required=False,
            confirmation_reason=None,
            improvement_proposal="対象外の理由を簡潔に文書化し、必要に応じて適用範囲を再確認してください。",
            missing_information=[],
            confidence="MEDIUM",
            fact=f"Partner answer: {answer}",
            inference="対象外の説明が十分に示されているように見えます。",
            recommendation="対象外の理由と適用範囲の説明を維持してください。",
        )

    return AIAnalysisResult(
        item_id=item.item_id,
        status="NORMAL",
        current_assessment="現時点では回答が概ね整合しており、追加確認は不要とみられます。",
        evidence=[f"質問: {item.question}", f"回答: {answer}", f"コメント: {comment or 'なし'}"],
        issue_or_risk=None,
        confirmation_required=False,
        confirmation_reason=None,
        improvement_proposal="文書管理の実務が継続していることを確認し、根拠の保持を継続してください。",
        missing_information=[],
        confidence="MEDIUM",
        fact=f"Partner answer: {answer}",
        inference="記載内容から、基準を満たしている可能性が高いです。",
        recommendation="必要に応じて証跡の保管と更新の継続を推奨します。",
    )


def analyze_checklist_items(items: list[ChecklistItem]) -> dict[str, AIAnalysisResult]:
    results: dict[str, AIAnalysisResult] = {}
    for item in items:
        results[item.item_id] = analyze_item(item)
    return results


def export_reviewed_workbook(original_bytes: bytes, items: list[ChecklistItem], decisions: dict[str, dict[str, str]], output_path: str) -> str:
    workbook = load_workbook(io.BytesIO(original_bytes), data_only=False)
    sheet = None
    for ws in workbook.worksheets:
        for row in ws.iter_rows(min_row=1, max_row=min(25, ws.max_row), values_only=True):
            if row and any(isinstance(v, str) and 'チェック項目' in v for v in row):
                sheet = ws
                break
        if sheet:
            break

    if sheet is None:
        raise ValueError("レビュー対象のチェックリストシートを見つけられませんでした。")

    header_lookup = {}
    header_row = None
    for idx, row in enumerate(sheet.iter_rows(min_row=1, max_row=sheet.max_row, values_only=True), start=1):
        row_text = [str(v).strip() if v is not None else '' for v in row]
        if any('チェック項目' in cell for cell in row_text):
            header_row = idx
            for col_idx, cell in enumerate(row_text, start=1):
                header_lookup[str(cell).strip()] = col_idx
            break

    if header_row is None:
        raise ValueError("ヘッダーを特定できませんでした。")

    for item in items:
        decision = decisions.get(item.item_id, {})
        row_no = item.source_row
        if row_no < 1:
            continue
        if "G" in header_lookup:
            pass
        for col_idx, header_name in enumerate([
            '確認要否\n（弊社）',
            '面談要望/資料提出依頼事項',
            '是正有無\n（弊社）',
            '是正依頼事項（弊社）',
            '是正依頼回答（質問事項があった場合）',
            '結果区分\n（弊社）',
            'コメント（弊社）',
        ], start=7):
            if col_idx <= sheet.max_column:
                sheet.cell(row=row_no, column=col_idx, value='')

        confirmation_required = decision.get('confirmation_required', False)
        if isinstance(confirmation_required, str):
            confirmation_required = confirmation_required.lower() == 'true'
        g_value = '要' if confirmation_required else ''
        h_value = decision.get('confirmation_reason') or ''
        i_value = '有' if decision.get('issue_or_risk') else ''
        j_value = decision.get('final_proposal') or decision.get('improvement_proposal') or ''
        l_value = decision.get('review_status') or decision.get('status') or ''
        m_value = decision.get('final_assessment') or ''

        sheet.cell(row=row_no, column=7, value=g_value)
        sheet.cell(row=row_no, column=8, value=h_value)
        sheet.cell(row=row_no, column=9, value=i_value)
        sheet.cell(row=row_no, column=10, value=j_value)
        sheet.cell(row=row_no, column=12, value=l_value)
        sheet.cell(row=row_no, column=13, value=m_value)

    workbook.save(output_path)
    return output_path
