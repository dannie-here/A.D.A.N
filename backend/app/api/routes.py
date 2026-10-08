"""API routes for A.D.A.N. backend."""

from typing import List
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.dataset import DatasetProfile, DatasetUploadResponse
from app.models.question import QuestionAnalysisRequest, QuestionAnalysisResponse
from app.services.dataset_service import DatasetService
from app.services.health_service import HealthService
from app.services.question_service import QuestionService

router = APIRouter()



@router.get("/health", tags=["System"])
def health_check() -> dict:
    """System health check endpoint.

    Returns the application status, current environment, and version.
    """
    return HealthService.get_health_status()


@router.post(
    "/datasets/upload",
    response_model=DatasetUploadResponse,
    tags=["Datasets"],
    summary="Upload and profile a CSV or Excel dataset",
)
async def upload_dataset(file: UploadFile = File(...)) -> DatasetUploadResponse:
    """Accepts a multipart CSV or Excel file upload, performs security validation,

    saves the file safely, and computes a comprehensive deterministic profile.
    """
    profile = await DatasetService.save_and_profile_upload(file)
    return DatasetUploadResponse(
        status="success",
        message=f"Dataset '{profile.filename}' uploaded and profiled successfully.",
        dataset_id=profile.dataset_id,
        profile=profile,
    )


@router.get(
    "/datasets/{dataset_id}",
    response_model=DatasetProfile,
    tags=["Datasets"],
    summary="Retrieve deterministic profile of an uploaded dataset",
)
def get_dataset_profile(dataset_id: str) -> DatasetProfile:
    """Returns the pre-computed deterministic profile for a specific dataset ID."""
    profile = DatasetService.get_profile(dataset_id)
    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset with ID '{dataset_id}' not found.",
        )
    return profile


@router.get(
    "/datasets",
    response_model=List[DatasetProfile],
    tags=["Datasets"],
    summary="List all uploaded datasets and their profiles",
)
def list_datasets() -> List[DatasetProfile]:
    """Returns all available profiled datasets in the local store."""
    return DatasetService.list_datasets()


@router.post(
    "/questions/analyze",
    response_model=QuestionAnalysisResponse,
    tags=["Questions"],
    summary="Analyze question answerability against a dataset profile",
)
def analyze_question(request: QuestionAnalysisRequest) -> QuestionAnalysisResponse:
    """Evaluates question answerability deterministically against the dataset schema and profile.

    Adheres strictly to the PS08 Core Principle:
    - ANSWERABLE: Sufficient information exists to identify required fields and calculations.
    - CANNOT_DETERMINE: Required information, fields, or date ranges are missing.
    - NEEDS_CLARIFICATION: Question has multiple materially different interpretations or is underspecified.
    """
    # 1. Validate dataset_id parameter
    clean_dataset_id = request.dataset_id.strip() if request.dataset_id else ""
    if not clean_dataset_id:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ERROR",
                "source": "Question Analysis API",
                "reason": "dataset_id must not be empty or blank.",
                "evidence": f"dataset_id = '{request.dataset_id}'",
                "recovery_retry": "Provide a valid dataset_id of an uploaded dataset.",
                "final_status": "ANALYSIS FAILED",
            },
        )

    # 2. Validate question parameter
    clean_question = request.question.strip() if request.question else ""
    if not clean_question:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ERROR",
                "source": "Question Analysis API",
                "reason": "Question must not be empty or composed solely of whitespace.",
                "evidence": f"question = '{request.question}'",
                "recovery_retry": "Provide a clear, non-empty analytical question.",
                "final_status": "ANALYSIS FAILED",
            },
        )

    if len(clean_question) > 1000:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ERROR",
                "source": "Question Analysis API",
                "reason": "Question exceeds maximum allowed length of 1000 characters.",
                "evidence": f"length = {len(clean_question)}",
                "recovery_retry": "Shorten your question to under 1000 characters.",
                "final_status": "ANALYSIS FAILED",
            },
        )

    # 3. Verify dataset existence
    profile = DatasetService.get_profile(clean_dataset_id)
    if not profile:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "ERROR",
                "source": "Question Analysis API",
                "reason": "The selected dataset could not be found.",
                "evidence": f"dataset_id = {clean_dataset_id}",
                "recovery_retry": "Select an available dataset and submit the question again.",
                "final_status": "ANALYSIS FAILED",
            },
        )

    # 4. Perform deterministic answerability analysis
    try:
        return QuestionService.analyze_question(
            dataset_id=clean_dataset_id,
            question=clean_question,
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ERROR",
                "source": "Question Analysis Service",
                "reason": str(ve),
                "evidence": f"dataset_id = {clean_dataset_id}",
                "recovery_retry": "Review your parameters and try again.",
                "final_status": "ANALYSIS FAILED",
            },
        ) from ve
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ERROR",
                "source": "Unknown",
                "reason": "Could not determine the underlying cause from available information.",
                "evidence": f"error = '{str(exc)}'",
                "recovery_retry": "Verify backend health and retry request.",
                "final_status": "ANALYSIS FAILED",
            },
        ) from exc
