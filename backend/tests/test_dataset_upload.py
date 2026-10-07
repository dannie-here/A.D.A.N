"""Unit and integration tests for Phase 2: Dataset Upload & Deterministic Profiling."""

import io
import pytest
import pandas as pd
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings

client = TestClient(app)

KNOWN_CSV_DATA = (
    "id,name,age,salary,joined_date\n"
    "1,Alice,25,50000.0,2022-01-15\n"
    "2,Bob,30,,2022-03-20\n"
    "3,Charlie,,75000.0,2022-05-10\n"
    "1,Alice,25,50000.0,2022-01-15\n"
)



@pytest.fixture(autouse=True)
def setup_test_data_dir(tmp_path, monkeypatch):
    """Isolate dataset storage to a temporary directory for each test run."""
    test_dir = str(tmp_path / "test_data")
    monkeypatch.setattr(settings, "DATA_DIR", test_dir)
    import os
    os.makedirs(test_dir, exist_ok=True)


def test_successful_csv_upload():
    """Verify that a valid CSV file uploads successfully and returns a profile."""
    file_bytes = io.BytesIO(KNOWN_CSV_DATA.encode("utf-8"))
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("employees.csv", file_bytes, "text/csv")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "dataset_id" in data
    assert data["profile"]["filename"] == "employees.csv"
    assert data["profile"]["file_type"] == "csv"


def test_successful_xlsx_upload():
    """Verify that a valid XLSX file uploads and is profiled deterministically."""
    df = pd.DataFrame({
        "item_code": [101, 102, 103],
        "cost": [12.5, 45.0, 99.9],
        "in_stock": [True, False, True],
    })
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine="openpyxl")
    excel_buffer.seek(0)

    response = client.post(
        "/api/datasets/upload",
        files={
            "file": (
                "inventory.xlsx",
                excel_buffer,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["profile"]["file_type"] == "xlsx"
    assert data["profile"]["row_count"] == 3
    assert data["profile"]["column_count"] == 3


def test_unsupported_file_rejection():
    """Verify that unsupported file formats are rejected with HTTP 400."""
    dummy_pdf = io.BytesIO(b"%PDF-1.4 dummy content")
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("unsupported.pdf", dummy_pdf, "application/pdf")},
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_empty_dataset_handling():
    """Verify that uploading an empty 0-byte file is rejected with HTTP 400."""
    empty_file = io.BytesIO(b"")
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("empty.csv", empty_file, "text/csv")},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_correct_row_and_column_counts():
    """Verify that row and column counts are deterministically accurate."""
    file_bytes = io.BytesIO(KNOWN_CSV_DATA.encode("utf-8"))
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("test_counts.csv", file_bytes, "text/csv")},
    )
    assert response.status_code == 200
    profile = response.json()["profile"]
    assert profile["row_count"] == 4
    assert profile["column_count"] == 5
    assert len(profile["columns"]) == 5


def test_correct_missing_value_counts():
    """Verify missing/null count and percentage per column on known dataset."""
    file_bytes = io.BytesIO(KNOWN_CSV_DATA.encode("utf-8"))
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("test_nulls.csv", file_bytes, "text/csv")},
    )
    assert response.status_code == 200
    cols = {c["name"]: c for c in response.json()["profile"]["columns"]}

    assert cols["id"]["missing_count"] == 0
    assert cols["id"]["missing_percentage"] == 0.0

    assert cols["age"]["missing_count"] == 1
    assert cols["age"]["missing_percentage"] == 25.0

    assert cols["salary"]["missing_count"] == 1
    assert cols["salary"]["missing_percentage"] == 25.0


def test_correct_duplicate_row_count():
    """Verify that duplicate rows are correctly counted."""
    # Rows 1 and 4 are identical in KNOWN_CSV_DATA
    file_bytes = io.BytesIO(KNOWN_CSV_DATA.encode("utf-8"))
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("test_duplicates.csv", file_bytes, "text/csv")},
    )
    assert response.status_code == 200
    assert response.json()["profile"]["duplicate_row_count"] == 1


def test_correct_numeric_statistics():
    """Verify min, max, mean, and median on numeric columns for a known dataset."""
    file_bytes = io.BytesIO(KNOWN_CSV_DATA.encode("utf-8"))
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("test_stats.csv", file_bytes, "text/csv")},
    )
    assert response.status_code == 200
    stats = response.json()["profile"]["numeric_statistics"]

    # age valid values: [25, 30, 25] -> min=25, max=30, mean=26.6667, median=25.0
    assert "age" in stats
    assert stats["age"]["min"] == 25.0
    assert stats["age"]["max"] == 30.0
    assert abs(stats["age"]["mean"] - 26.6667) < 0.01
    assert stats["age"]["median"] == 25.0

    # salary valid values: [50000.0, 75000.0, 50000.0] -> min=50000, max=75000, median=50000
    assert "salary" in stats
    assert stats["salary"]["min"] == 50000.0
    assert stats["salary"]["max"] == 75000.0
    assert abs(stats["salary"]["mean"] - 58333.3333) < 0.01
    assert stats["salary"]["median"] == 50000.0


def test_date_range_detection():
    """Verify deterministic date range detection for date-like columns."""
    file_bytes = io.BytesIO(KNOWN_CSV_DATA.encode("utf-8"))
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("test_dates.csv", file_bytes, "text/csv")},
    )
    assert response.status_code == 200
    date_ranges = response.json()["profile"]["date_ranges"]
    assert len(date_ranges) >= 1

    date_col = next((d for d in date_ranges if d["column_name"] == "joined_date"), None)
    assert date_col is not None
    assert "2022-01-15" in date_col["min_date"]
    assert "2022-05-10" in date_col["max_date"]


def test_profile_endpoint_retrieval():
    """Verify that GET /api/datasets/{dataset_id} returns the pre-computed profile."""
    file_bytes = io.BytesIO(KNOWN_CSV_DATA.encode("utf-8"))
    upload_res = client.post(
        "/api/datasets/upload",
        files={"file": ("orders.csv", file_bytes, "text/csv")},
    )
    dataset_id = upload_res.json()["dataset_id"]

    # Retrieve profile via GET
    get_res = client.get(f"/api/datasets/{dataset_id}")
    assert get_res.status_code == 200
    profile = get_res.json()
    assert profile["dataset_id"] == dataset_id
    assert profile["filename"] == "orders.csv"
    assert profile["row_count"] == 4
    assert profile["column_count"] == 5

    # Test non-existent ID
    missing_res = client.get("/api/datasets/non_existent_uuid_12345")
    assert missing_res.status_code == 404
