"""Dataset storage and lifecycle service for A.D.A.N.

Implements safe multipart file processing, secure internal UUID assignment,
storage quota enforcement, and integration with the deterministic profiler.
"""

import json
import os
import uuid
from typing import List, Optional
from fastapi import HTTPException, UploadFile

from app.config import settings
from app.models.dataset import DatasetProfile
from app.services.profiler_service import ProfilerService

ALLOWED_EXTENSIONS = {
    ".csv": "csv",
    ".xlsx": "xlsx",
    ".xls": "xlsx",
}


class DatasetService:
    """Service handling dataset upload, persistence, and profile caching."""

    @staticmethod
    def get_storage_path(dataset_id: str, extension: str) -> str:
        """Returns the safe local storage path for a dataset."""
        safe_ext = extension.lower()
        return os.path.join(settings.DATA_DIR, f"{dataset_id}{safe_ext}")

    @staticmethod
    def get_profile_path(dataset_id: str) -> str:
        """Returns the profile metadata storage path."""
        return os.path.join(settings.DATA_DIR, f"{dataset_id}_profile.json")

    @classmethod
    async def save_and_profile_upload(cls, file: UploadFile) -> DatasetProfile:
        """Validates, safely writes, and profiles an uploaded dataset."""
        original_filename = file.filename or "unnamed_dataset"
        # Sanitize filename base
        safe_filename = os.path.basename(original_filename)

        # 1. Validate file extension
        _, ext = os.path.splitext(safe_filename)
        ext_lower = ext.lower()
        if ext_lower not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unsupported file format '{ext}'. "
                    f"Only CSV (.csv) and Excel (.xlsx, .xls) files are supported."
                ),
            )

        file_type = ALLOWED_EXTENSIONS[ext_lower]

        # 2. Generate safe UUID dataset identifier
        dataset_id = str(uuid.uuid4())
        dest_path = cls.get_storage_path(dataset_id, ext_lower)

        # 3. Stream and write file with size limits
        total_size = 0
        chunk_size = 1024 * 64  # 64 KB chunks

        try:
            with open(dest_path, "wb") as buffer:
                while True:
                    chunk = await file.read(chunk_size)
                    if not chunk:
                        break
                    total_size += len(chunk)

                    if total_size > settings.MAX_UPLOAD_SIZE_BYTES:
                        buffer.close()
                        if os.path.exists(dest_path):
                            os.remove(dest_path)
                        raise HTTPException(
                            status_code=413,
                            detail=(
                                f"File exceeds maximum allowed upload size of "
                                f"{settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB."
                            ),
                        )
                    buffer.write(chunk)

            # Check for empty file
            if total_size == 0:
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded file is empty (0 bytes). Please upload a valid dataset.",
                )

            # 4. Load dataframe and generate deterministic profile
            try:
                df = ProfilerService.load_dataframe(dest_path, file_type)
                profile = ProfilerService.profile_dataframe(
                    df=df,
                    dataset_id=dataset_id,
                    filename=safe_filename,
                    file_type=file_type,
                    file_size_bytes=total_size,
                )
            except ValueError as ve:
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                raise HTTPException(status_code=400, detail=str(ve)) from ve
            except Exception as exc:
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to profile dataset: {str(exc)}",
                ) from exc

            # 5. Persist deterministic profile JSON for fast retrieval
            profile_path = cls.get_profile_path(dataset_id)
            with open(profile_path, "w", encoding="utf-8") as pf:
                json.dump(profile.model_dump(), pf, indent=2)

            return profile

        except HTTPException:
            # Re-raise explicit HTTP exceptions
            raise
        except Exception as exc:
            # Clean up on unexpected error
            if os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except OSError:
                    pass
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while saving the dataset: {str(exc)}",
            ) from exc

    @classmethod
    def get_profile(cls, dataset_id: str) -> Optional[DatasetProfile]:
        """Retrieves a cached dataset profile by dataset ID."""
        # Sanitize dataset_id to prevent directory traversal
        clean_id = os.path.basename(dataset_id.strip())
        profile_path = cls.get_profile_path(clean_id)

        if not os.path.exists(profile_path):
            return None

        try:
            with open(profile_path, "r", encoding="utf-8") as pf:
                data = json.load(pf)
                return DatasetProfile(**data)
        except Exception:
            return None

    @classmethod
    def list_datasets(cls) -> List[DatasetProfile]:
        """Lists all profiled datasets stored in the local application data directory."""
        results: List[DatasetProfile] = []
        if not os.path.exists(settings.DATA_DIR):
            return results

        for fname in os.listdir(settings.DATA_DIR):
            if fname.endswith("_profile.json"):
                profile_path = os.path.join(settings.DATA_DIR, fname)
                try:
                    with open(profile_path, "r", encoding="utf-8") as pf:
                        data = json.load(pf)
                        results.append(DatasetProfile(**data))
                except Exception:
                    continue
        return results
