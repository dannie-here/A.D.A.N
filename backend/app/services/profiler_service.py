"""Deterministic profiling service for datasets using pandas and openpyxl.

Strict adherence to PS08 principles:
- Computes mathematical and physical facts deterministically.
- Never guesses, hallucinates, or estimates types or dates without proof.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
import os
import re
import pandas as pd
import numpy as np

from app.models.dataset import (
    ColumnProfile,
    DatasetProfile,
    DateRange,
    NumericStats,
)


class ProfilerService:
    """Deterministic profiling service."""

    @staticmethod
    def load_dataframe(file_path: str, file_type: str) -> pd.DataFrame:
        """Loads dataset file into a pandas DataFrame safely without executing code."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_type = file_type.lower()
        if file_type == "csv":
            try:
                # Read CSV deterministically
                df = pd.read_csv(file_path)
            except Exception as exc:
                raise ValueError(f"Failed to parse CSV file: {str(exc)}") from exc
        elif file_type in ("xlsx", "xls"):
            try:
                # Read Excel deterministically using openpyxl
                df = pd.read_excel(file_path, engine="openpyxl")
            except Exception as exc:
                raise ValueError(f"Failed to parse Excel file: {str(exc)}") from exc
        else:
            raise ValueError(f"Unsupported file type: '{file_type}'. Supported: 'csv', 'xlsx'")

        if df.empty and len(df.columns) == 0:
            raise ValueError("The uploaded dataset contains no columns or data.")

        return df

    @staticmethod
    def profile_dataframe(
        df: pd.DataFrame,
        dataset_id: str,
        filename: str,
        file_type: str,
        file_size_bytes: int,
    ) -> DatasetProfile:
        """Calculates a comprehensive deterministic profile for a DataFrame."""
        row_count = int(len(df))
        column_count = int(len(df.columns))

        if row_count == 0 and column_count == 0:
            raise ValueError("The uploaded dataset is empty.")

        # 1. Duplicates count
        duplicate_rows = int(df.duplicated().sum()) if row_count > 0 else 0

        # 2. Per-column profile
        columns_profile: List[ColumnProfile] = []
        numeric_columns: List[str] = []
        numeric_statistics: Dict[str, NumericStats] = {}
        date_ranges: List[DateRange] = []

        for col in df.columns:
            col_name = str(col)
            series = df[col]
            missing_count = int(series.isna().sum())
            missing_pct = (
                round(float((missing_count / row_count) * 100), 2)
                if row_count > 0
                else 0.0
            )

            # Determine clean dtype string
            dtype_str = str(series.dtype)

            # Check for boolean explicitly
            is_bool = pd.api.types.is_bool_dtype(series)

            # Check for numeric (excluding boolean)
            is_numeric = pd.api.types.is_numeric_dtype(series) and not is_bool

            if is_bool:
                dtype_str = "boolean"
            elif is_numeric:
                numeric_columns.append(col_name)
                # Compute numeric stats if non-null values exist
                valid_num = series.dropna()
                if len(valid_num) > 0:
                    try:
                        numeric_statistics[col_name] = NumericStats(
                            min=round(float(valid_num.min()), 4),
                            max=round(float(valid_num.max()), 4),
                            mean=round(float(valid_num.mean()), 4),
                            median=round(float(valid_num.median()), 4),
                        )
                    except Exception:
                        # If conversion fails for any unstandard numeric type
                        pass

            # Detect date-like columns deterministically
            detected_range = ProfilerService._detect_date_range(series, col_name)
            if detected_range:
                date_ranges.append(detected_range)
                if not is_numeric and not is_bool:
                    dtype_str = "datetime"

            columns_profile.append(
                ColumnProfile(
                    name=col_name,
                    dtype=dtype_str,
                    missing_count=missing_count,
                    missing_percentage=missing_pct,
                )
            )

        return DatasetProfile(
            dataset_id=dataset_id,
            filename=filename,
            file_type=file_type,
            file_size_bytes=file_size_bytes,
            row_count=row_count,
            column_count=column_count,
            columns=columns_profile,
            duplicate_row_count=duplicate_rows,
            numeric_columns=numeric_columns,
            numeric_statistics=numeric_statistics,
            date_ranges=date_ranges,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def _detect_date_range(series: pd.Series, col_name: str) -> Optional[DateRange]:
        """Strict deterministic date-like detection without guessing."""
        # 1. Native datetime dtype
        if pd.api.types.is_datetime64_any_dtype(series):
            valid = series.dropna()
            if len(valid) > 0:
                return DateRange(
                    column_name=col_name,
                    min_date=str(valid.min().isoformat()),
                    max_date=str(valid.max().isoformat()),
                )
            return None

        # 2. Exclude numeric or boolean series from accidental string conversion
        if pd.api.types.is_numeric_dtype(series) or pd.api.types.is_bool_dtype(series):
            return None

        # 3. String / Object inspection
        valid_strings = series.dropna().astype(str).str.strip()
        if len(valid_strings) == 0:
            return None

        # Verify whether strings contain typical date delimiter characters (- or / or :)
        # to avoid parsing arbitrary words or plain numbers as dates
        sample = valid_strings.head(20)
        has_date_delimiters = any(
            bool(re.search(r"[-/:]", val)) and any(char.isdigit() for char in val)
            for val in sample
        )
        if not has_date_delimiters:
            return None

        try:
            # Deterministically attempt parsing
            parsed = pd.to_datetime(valid_strings, errors="coerce")
            valid_parsed = parsed.dropna()
            # Require at least 85% successful parsing rate among non-null strings
            if len(valid_parsed) / len(valid_strings) >= 0.85 and len(valid_parsed) > 0:
                # Ensure plausible year range (between 1900 and 2150) to reject arbitrary numbers
                min_yr = valid_parsed.min().year
                max_yr = valid_parsed.max().year
                if 1900 <= min_yr <= 2150 and 1900 <= max_yr <= 2150:
                    return DateRange(
                        column_name=col_name,
                        min_date=str(valid_parsed.min().isoformat()),
                        max_date=str(valid_parsed.max().isoformat()),
                    )
        except Exception:
            return None

        return None
