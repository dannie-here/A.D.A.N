"""Pydantic schemas for Question Analysis & Answerability (Phase 3)."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class QuestionAnalysisRequest(BaseModel):
    """Incoming request to analyze question answerability against a dataset."""

    dataset_id: str = Field(default="", description="UUID of the selected dataset")
    question: str = Field(
        default="",
        description="Natural-language analytical query",
    )



class QuestionEvidence(BaseModel):
    """Concrete evidence gathered from the deterministic dataset profile."""

    relevant_columns: List[str] = Field(
        default_factory=list, description="Columns found relevant to the query"
    )
    available_date_range: Optional[str] = Field(
        default=None, description="Available date range in the dataset if applicable"
    )
    available_values: List[str] = Field(
        default_factory=list, description="Sampled or available categorical values"
    )
    missing_requirements: List[str] = Field(
        default_factory=list,
        description="Required fields or timeframes missing from dataset",
    )
    data_quality_notes: List[str] = Field(
        default_factory=list,
        description="Deterministic observations regarding nulls or duplicate rows",
    )


class QuestionAnalysisResponse(BaseModel):
    """Structured answerability decision and evidence."""

    dataset_id: str = Field(..., description="Dataset identifier")
    question: str = Field(..., description="Original submitted question")
    status: str = Field(
        ...,
        description="Classification: 'ANSWERABLE', 'CANNOT_DETERMINE', or 'NEEDS_CLARIFICATION'",
    )
    reason: str = Field(..., description="Clear explanation for the classification")
    evidence: QuestionEvidence = Field(
        ..., description="Deterministic evidence supporting the decision"
    )
    interpretation: str = Field(
        ..., description="How the question was interpreted in relation to dataset schema"
    )
    suggested_next_step: str = Field(
        ..., description="Actionable next step for user or subsequent phase"
    )


class ADANErrorResponse(BaseModel):
    """Standardized A.D.A.N. error response structure."""

    error: str = Field(default="ERROR", description="Error marker")
    source: str = Field(..., description="Originating subsystem or API")
    reason: str = Field(..., description="Primary cause of failure")
    evidence: str = Field(..., description="Verifiable facts and parameters")
    recovery_retry: str = Field(..., description="Actionable recovery steps")
    final_status: str = Field(
        default="ANALYSIS FAILED", description="Terminal state indicator"
    )
