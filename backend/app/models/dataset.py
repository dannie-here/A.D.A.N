"""Pydantic schemas for datasets and deterministic data profiling."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ColumnProfile(BaseModel):
    """Deterministic profile information for an individual column."""

    name: str = Field(..., description="Column name")
    dtype: str = Field(..., description="Inferred physical/data type")
    missing_count: int = Field(..., description="Count of missing/null values")
    missing_percentage: float = Field(
        ..., description="Percentage of missing values (0.0 to 100.0)"
    )


class NumericStats(BaseModel):
    """Deterministic summary statistics for a numeric column."""

    min: float = Field(..., description="Minimum value")
    max: float = Field(..., description="Maximum value")
    mean: float = Field(..., description="Arithmetic mean")
    median: float = Field(..., description="Median value")


class DateRange(BaseModel):
    """Deterministic date range detected for a date-like column."""

    column_name: str = Field(..., description="Column name")
    min_date: str = Field(..., description="Earliest ISO formatted date/timestamp")
    max_date: str = Field(..., description="Latest ISO formatted date/timestamp")


class DatasetProfile(BaseModel):
    """Complete deterministic profile of an uploaded dataset."""

    dataset_id: str = Field(..., description="Secure UUID identifier")
    filename: str = Field(..., description="Sanitized original filename")
    file_type: str = Field(..., description="File format type ('csv' or 'xlsx')")
    file_size_bytes: int = Field(..., description="Total file size in bytes")
    row_count: int = Field(..., description="Total row count")
    column_count: int = Field(..., description="Total column count")
    columns: List[ColumnProfile] = Field(..., description="Per-column profile specs")
    duplicate_row_count: int = Field(..., description="Count of duplicate rows")
    numeric_columns: List[str] = Field(
        default_factory=list, description="Names of verified numeric columns"
    )
    numeric_statistics: Dict[str, NumericStats] = Field(
        default_factory=dict, description="Numeric summary statistics keyed by column name"
    )
    date_ranges: List[DateRange] = Field(
        default_factory=list, description="Detected date ranges for date-like columns"
    )
    created_at: str = Field(..., description="UTC ISO timestamp of dataset registration")


class DatasetUploadResponse(BaseModel):
    """Response returned upon successful dataset upload."""

    status: str = Field(default="success", description="Status code string")
    message: str = Field(..., description="Human-readable status message")
    dataset_id: str = Field(..., description="Unique dataset identifier")
    profile: DatasetProfile = Field(..., description="Deterministic dataset profile")
