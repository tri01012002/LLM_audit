from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ChecklistItem(BaseModel):
    item_id: str = Field(description="Unique checklist item id such as 1-① or 13-02")
    source_row: int = Field(description="Original Excel row number")
    source_sheet: str = Field(description="Original worksheet name")
    source_columns: list[str] = Field(default_factory=list)
    category: str = ""
    question: str = ""
    detail: str = ""
    partner_answer: str = ""
    partner_comment: str = ""
    confirmation_required: bool | None = None
    confirmation_reason: str | None = None
    interview_document_request: str | None = None
    corrective_action_required: bool | None = None
    corrective_action_request: str | None = None
    corrective_action_response: str | None = None
    result_classification: str | None = None
    auditor_comment: str | None = None
    source_raw: dict[str, str] = Field(default_factory=dict)


class AIAnalysisResult(BaseModel):
    item_id: str
    status: str = "REVIEW"
    current_assessment: str = ""
    evidence: list[str] = Field(default_factory=list)
    issue_or_risk: str | None = None
    confirmation_required: bool = False
    confirmation_reason: str | None = None
    improvement_proposal: str | None = None
    missing_information: list[str] = Field(default_factory=list)
    confidence: str = "MEDIUM"
    fact: str = ""
    inference: str = ""
    recommendation: str = ""


class ReviewDecision(BaseModel):
    item_id: str
    final_assessment: str = ""
    final_proposal: str = ""
    review_status: str = "ACCEPTED"
    reviewer: str = "Auditor"
    edit_reason: str | None = None
