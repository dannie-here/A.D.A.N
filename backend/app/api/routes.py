"""API routes for A.D.A.N. backend."""

from typing import List
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.dataset import DatasetProfile, DatasetUploadResponse
from app.services.dataset_service import DatasetService
from app.services.health_service import HealthService

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

