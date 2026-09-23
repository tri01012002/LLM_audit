from __future__ import annotations

import os
import uuid
import hashlib
from pathlib import Path

import streamlit as st

from core.ai_analyzer import analyze_checklist_items, export_reviewed_workbook
from core.business_rules import evaluate_business_rules
from core.checklist_models import ChecklistItem, ReviewDecision
from core.excel_parser import parse_checklist_workbook

st.set_page_config(page_title="AI Audit Assistant", page_icon="🛡️", layout="wide")


def _safe_session_state():
    if "checklist_items" not in st.session_state:
        st.session_state.checklist_items = []
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = {}
    if "review_decisions" not in st.session_state:
        st.session_state.review_decisions = {}
    if "uploaded_file_name" not in st.session_state:
        st.session_state.uploaded_file_name = ""
    if "uploaded_file_bytes" not in st.session_state:
        st.session_state.uploaded_file_bytes = None
    if "uploaded_file_hash" not in st.session_state:
        st.session_state.uploaded_file_hash = ""


def _summarize_counts(items):
    counts = {"total": len(items), "answered": 0, "unanswered": 0, "needs_confirmation": 0, "possible_contradiction": 0}
    for item in items:
        if item.partner_answer:
            counts["answered"] += 1
        else:
            counts["unanswered"] += 1
        rule = evaluate_business_rules(item)
        if rule["status"] in {"NEEDS_CONFIRMATION", "NEEDS_INFORMATION", "NEEDS_REVIEW"}:
            counts["needs_confirmation"] += 1
        if rule["status"] == "POSSIBLE_CONTRADICTION":
            counts["possible_contradiction"] += 1
    return counts


def _display_row(item: ChecklistItem):
    st.markdown(f"### {item.item_id}: {item.question or item.detail}")
    col1, col2, col3 = st.columns([1.2, 1.2, 2])
    with col1:
        st.write("**Answer**")
        st.write(item.partner_answer or "(未回答)")
        st.write("**Comment**")
        st.write(item.partner_comment or "(未記載)")
    with col2:
        st.write("**Rule**")
        rule = evaluate_business_rules(item)
        st.write(rule["status"])
        if rule["reason"]:
            st.caption(rule["reason"])
        st.write("**Source**")
        st.write(f"Sheet: {item.source_sheet}")
        st.write(f"Row: {item.source_row}")
    with col3:
        result = st.session_state.analysis_results.get(item.item_id)
        if result:
            st.write("**AI Current Assessment**")
            st.write(result.current_assessment)
            st.write("**Issue / Risk**")
            st.write(result.issue_or_risk or "-")
            st.write("**Proposal**")
            st.write(result.improvement_proposal or "-")
            st.write("**Evidence**")
            for e in result.evidence:
                st.write(f"- {e}")
        else:
            st.info("AI analysis not available yet.")

    decision = st.session_state.review_decisions.get(item.item_id, {})
    final_assessment = st.text_area(
        "Final assessment",
        value=decision.get("final_assessment", (st.session_state.analysis_results.get(item.item_id).current_assessment if st.session_state.analysis_results.get(item.item_id) else "")),
        key=f"assessment_{item.item_id}",
    )
    final_proposal = st.text_area(
        "Final improvement proposal",
        value=decision.get("final_proposal", (st.session_state.analysis_results.get(item.item_id).improvement_proposal if st.session_state.analysis_results.get(item.item_id) else "")),
        key=f"proposal_{item.item_id}",
    )
    status = st.selectbox(
        "Review status",
        ["ACCEPTED", "EDITED", "REJECTED", "ON_HOLD"],
        index=["ACCEPTED", "EDITED", "REJECTED", "ON_HOLD"].index(decision.get("review_status", "ACCEPTED")),
        key=f"status_{item.item_id}",
    )
    if st.button("Save review", key=f"save_{item.item_id}"):
        st.session_state.review_decisions[item.item_id] = {
            "final_assessment": final_assessment,
            "final_proposal": final_proposal,
            "review_status": status,
            "reviewer": "Auditor",
            "confirmation_required": str(bool(result.confirmation_required)) if (result := st.session_state.analysis_results.get(item.item_id)) else "False",
            "issue_or_risk": (result.issue_or_risk if result else ""),
            "improvement_proposal": final_proposal,
            "status": (result.status if result else "REVIEW"),
        }
        st.success(f"Saved review for {item.item_id}")


def _run_analysis(items):
    st.session_state.analysis_results = analyze_checklist_items(items)


def _page_upload():
    st.title("AI Audit Assistant")
    st.caption("Upload answered checklist Excel → analyze → review → export")

    uploaded = st.file_uploader("Choose Excel file", type=["xlsx", "xlsm"], accept_multiple_files=False)
    if uploaded is not None:
        uploaded_bytes = uploaded.getvalue()
        uploaded_hash = hashlib.sha256(uploaded_bytes).hexdigest()
        if uploaded_hash != st.session_state.uploaded_file_hash:
            try:
                items = parse_checklist_workbook(uploaded_bytes)
                st.session_state.uploaded_file_name = uploaded.name
                st.session_state.uploaded_file_bytes = uploaded_bytes
                st.session_state.checklist_items = items
                st.session_state.analysis_results = {}
                st.session_state.review_decisions = {}
                st.session_state.uploaded_file_hash = uploaded_hash
            except Exception as exc:
                st.session_state.uploaded_file_name = ""
                st.session_state.uploaded_file_bytes = None
                st.session_state.checklist_items = []
                st.session_state.analysis_results = {}
                st.session_state.review_decisions = {}
                st.session_state.uploaded_file_hash = ""
                st.error(f"Failed to parse workbook: {exc}")

        if st.session_state.checklist_items:
            items = st.session_state.checklist_items
            counts = _summarize_counts(items)
            st.success(f"{len(items)} items parsed successfully.")
            st.write(f"Answered: {counts['answered']} | Unanswered: {counts['unanswered']} | Needs confirmation: {counts['needs_confirmation']} | Possible contradiction: {counts['possible_contradiction']}")
            if st.button("Analyze checklist"):
                _run_analysis(items)
                st.rerun()

    if st.session_state.checklist_items:
        counts = _summarize_counts(st.session_state.checklist_items)
        st.subheader("Summary")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total", counts["total"])
        col2.metric("Answered", counts["answered"])
        col3.metric("Unanswered", counts["unanswered"])
        col4.metric("Needs review", counts["needs_confirmation"])

        st.dataframe(
            [
                {
                    "Item": item.item_id,
                    "Answer": item.partner_answer or "",
                    "Comment": item.partner_comment or "",
                    "Status": evaluate_business_rules(item)["status"],
                    "Source": f"{item.source_sheet}:{item.source_row}",
                }
                for item in st.session_state.checklist_items
            ],
            use_container_width=True,
        )

        if st.button("Run analysis again"):
            _run_analysis(st.session_state.checklist_items)
            st.rerun()

        if st.session_state.analysis_results:
            st.subheader("AI review results")
            for item in st.session_state.checklist_items:
                result = st.session_state.analysis_results.get(item.item_id)
                if not result:
                    continue
                with st.expander(f"{item.item_id} — {item.question or item.detail}"):
                    st.write("**Status:**", result.status)
                    st.write("**Assessment:**", result.current_assessment)
                    st.write("**Issue / Risk:**", result.issue_or_risk or "-")
                    st.write("**Evidence:**")
                    for e in result.evidence:
                        st.write(f"- {e}")
                    st.write("**Confirmation required:**", bool(result.confirmation_required))
                    st.write("**Proposal:**", result.improvement_proposal or "-")

                    decision = st.session_state.review_decisions.get(item.item_id, {})
                    final_assessment = st.text_area("Final assessment", value=decision.get("final_assessment", result.current_assessment), key=f"final_assess_{item.item_id}")
                    final_proposal = st.text_area("Final proposal", value=decision.get("final_proposal", result.improvement_proposal or ""), key=f"final_prop_{item.item_id}")
                    review_status = st.selectbox("Status", ["ACCEPTED", "EDITED", "REJECTED", "ON_HOLD"], index=["ACCEPTED", "EDITED", "REJECTED", "ON_HOLD"].index(decision.get("review_status", "ACCEPTED")), key=f"rev_status_{item.item_id}")
                    if st.button("Save item review", key=f"item_review_{item.item_id}"):
                        st.session_state.review_decisions[item.item_id] = {
                            "final_assessment": final_assessment,
                            "final_proposal": final_proposal,
                            "review_status": review_status,
                            "reviewer": "Auditor",
                            "confirmation_required": str(result.confirmation_required),
                            "confirmation_reason": result.confirmation_reason or "",
                            "issue_or_risk": result.issue_or_risk,
                            "status": result.status,
                        }
                        st.success(f"Saved review for {item.item_id}")

            if st.button("Export reviewed workbook"):
                output_path = os.path.join(os.getcwd(), f"reviewed_{uuid.uuid4().hex[:8]}.xlsx")
                try:
                    for item in st.session_state.checklist_items:
                        if item.item_id not in st.session_state.review_decisions:
                            st.session_state.review_decisions[item.item_id] = {
                                "final_assessment": st.session_state.analysis_results.get(item.item_id).current_assessment if st.session_state.analysis_results.get(item.item_id) else "",
                                "final_proposal": st.session_state.analysis_results.get(item.item_id).improvement_proposal if st.session_state.analysis_results.get(item.item_id) else "",
                                "review_status": "ACCEPTED",
                                "reviewer": "Auditor",
                                "confirmation_required": str(bool(st.session_state.analysis_results.get(item.item_id).confirmation_required)) if st.session_state.analysis_results.get(item.item_id) else "False",
                                "confirmation_reason": (st.session_state.analysis_results.get(item.item_id).confirmation_reason if st.session_state.analysis_results.get(item.item_id) else ""),
                                "issue_or_risk": (st.session_state.analysis_results.get(item.item_id).issue_or_risk if st.session_state.analysis_results.get(item.item_id) else ""),
                                "status": (st.session_state.analysis_results.get(item.item_id).status if st.session_state.analysis_results.get(item.item_id) else "REVIEW"),
                            }
                    export_reviewed_workbook(st.session_state.uploaded_file_bytes, st.session_state.checklist_items, {k: v for k, v in st.session_state.review_decisions.items()}, output_path)
                    with open(output_path, "rb") as f:
                        st.download_button("Download reviewed Excel", f.read(), file_name=os.path.basename(output_path), mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    st.success(f"Reviewed workbook exported to: {output_path}")
                except Exception as exc:
                    st.error(f"Export failed: {exc}")


def main():
    _safe_session_state()
    _page_upload()


if __name__ == "__main__":
    main()
