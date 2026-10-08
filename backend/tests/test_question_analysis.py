"""Unit and integration tests for Phase 3: Question Analysis & Answerability."""

import io
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings

client = TestClient(app)

TEST_CSV_DATA = (
    "id,product,unit_price,revenue,units_sold,order_date\n"
    "1,Widget,10.5,105.0,10,2022-01-15\n"
    "2,Gadget,25.0,,0,2022-03-20\n"
    "3,Doohickey,15.0,150.0,10,2022-05-10\n"
    "1,Widget,10.5,105.0,10,2022-01-15\n"
)


@pytest.fixture(autouse=True)
def setup_test_data_dir(tmp_path, monkeypatch):
    """Isolate dataset storage to a temporary directory for each test run."""
    test_dir = str(tmp_path / "test_data")
    monkeypatch.setattr(settings, "DATA_DIR", test_dir)
    import os
    os.makedirs(test_dir, exist_ok=True)


@pytest.fixture
def uploaded_dataset_id():
    """Uploads a deterministic test dataset and returns its dataset_id."""
    file_bytes = io.BytesIO(TEST_CSV_DATA.encode("utf-8"))
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("sales_records.csv", file_bytes, "text/csv")},
    )
    assert response.status_code == 200
    return response.json()["dataset_id"]


def test_1_valid_answerable_question(uploaded_dataset_id):
    """1. Verify that 'What is the total revenue?' is classified as ANSWERABLE."""
    response = client.post(
        "/api/questions/analyze",
        json={
            "dataset_id": uploaded_dataset_id,
            "question": "What is the total revenue?",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ANSWERABLE"
    assert "revenue" in data["evidence"]["relevant_columns"]
    assert "revenue" in data["reason"].lower()
    assert data["interpretation"] != ""
    assert data["suggested_next_step"] != ""


def test_2_answerable_numeric_aggregation(uploaded_dataset_id):
    """2. Verify that 'What is the average unit_price?' is classified as ANSWERABLE."""
    response = client.post(
        "/api/questions/analyze",
        json={
            "dataset_id": uploaded_dataset_id,
            "question": "What is the average unit_price?",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ANSWERABLE"
    assert "unit_price" in data["evidence"]["relevant_columns"]


def test_3_cannot_determine_missing_profit(uploaded_dataset_id):
    """3. Verify that 'What is the total profit?' returns CANNOT_DETERMINE."""
    response = client.post(
        "/api/questions/analyze",
        json={
            "dataset_id": uploaded_dataset_id,
            "question": "What is the total profit?",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CANNOT_DETERMINE"
    assert "profit" in data["reason"].lower()
    assert any("profit" in req.lower() for req in data["evidence"]["missing_requirements"])


def test_4_cannot_determine_unavailable_year(uploaded_dataset_id):
    """4. Verify that 'What was revenue in 2035?' returns CANNOT_DETERMINE due to date range."""
    response = client.post(
        "/api/questions/analyze",
        json={
            "dataset_id": uploaded_dataset_id,
            "question": "What was revenue in 2035?",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CANNOT_DETERMINE"
    assert "2035" in data["reason"]
    assert data["evidence"]["available_date_range"] is not None
    assert any("2035" in req for req in data["evidence"]["missing_requirements"])


def test_5_needs_clarification_quarter_ambiguity(uploaded_dataset_id):
    """5. Verify that 'What was revenue in Q1?' returns NEEDS_CLARIFICATION for quarter convention."""
    response = client.post(
        "/api/questions/analyze",
        json={
            "dataset_id": uploaded_dataset_id,
            "question": "What was revenue in Q1?",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "NEEDS_CLARIFICATION"
    assert "q1" in data["reason"].lower()
    assert any(
        "quarter" in req.lower()
        for req in data["evidence"]["missing_requirements"]
    )
    assert "calendar" in data["suggested_next_step"].lower()


def test_6_missing_column_discount(uploaded_dataset_id):
    """6. Verify that 'What is the average discount?' returns CANNOT_DETERMINE."""
    response = client.post(
        "/api/questions/analyze",
        json={
            "dataset_id": uploaded_dataset_id,
            "question": "What is the average discount?",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CANNOT_DETERMINE"
    assert "discount" in data["reason"].lower()
    assert any("discount" in req.lower() for req in data["evidence"]["missing_requirements"])


def test_7_blank_question_rejection(uploaded_dataset_id):
    """7. Verify that blank or whitespace-only questions are rejected with HTTP 400 and A.D.A.N. error structure."""
    response = client.post(
        "/api/questions/analyze",
        json={
            "dataset_id": uploaded_dataset_id,
            "question": "     ",
        },
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["error"] == "ERROR"
    assert detail["source"] == "Question Analysis API"
    assert "whitespace" in detail["reason"].lower()
    assert detail["final_status"] == "ANALYSIS FAILED"


def test_8_invalid_dataset_id():
    """8. Verify that non-existent dataset IDs are rejected with HTTP 404 and A.D.A.N. error structure."""
    response = client.post(
        "/api/questions/analyze",
        json={
            "dataset_id": "non_existent_uuid_99999",
            "question": "What is the total revenue?",
        },
    )
    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["error"] == "ERROR"
    assert detail["source"] == "Question Analysis API"
    assert "could not be found" in detail["reason"].lower()
    assert "non_existent_uuid_99999" in detail["evidence"]
    assert detail["final_status"] == "ANALYSIS FAILED"


def test_9_dataset_with_missing_values(uploaded_dataset_id):
    """9. Verify that missing values are documented in evidence notes without invalidating answerability."""
    # revenue has 1 null value out of 4 rows (25.0%)
    response = client.post(
        "/api/questions/analyze",
        json={
            "dataset_id": uploaded_dataset_id,
            "question": "What is the total revenue?",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ANSWERABLE"
    notes = data["evidence"]["data_quality_notes"]
    assert any("missing value" in n.lower() and "revenue" in n.lower() for n in notes)


def test_10_dataset_with_duplicate_rows(uploaded_dataset_id):
    """10. Verify duplicate row detection in answerability evidence and duplicate row queries."""
    # Query specific to duplicates
    dup_res = client.post(
        "/api/questions/analyze",
        json={
            "dataset_id": uploaded_dataset_id,
            "question": "How many duplicate rows exist?",
        },
    )
    assert dup_res.status_code == 200
    dup_data = dup_res.json()
    assert dup_data["status"] == "ANSWERABLE"
    assert any("duplicate" in n.lower() for n in dup_data["evidence"]["data_quality_notes"])


def test_11_analyzer_never_invents_columns(uploaded_dataset_id):
    """11. Verify that the analyzer never invents non-existent columns in evidence."""
    questions = [
        "What is the total profit?",
        "What is the customer churn?",
        "What is the tax rate?",
        "What is the average discount?",
    ]
    valid_cols = {"id", "product", "unit_price", "revenue", "units_sold", "order_date"}

    for q in questions:
        response = client.post(
            "/api/questions/analyze",
            json={"dataset_id": uploaded_dataset_id, "question": q},
        )
        assert response.status_code == 200
        data = response.json()
        for col in data["evidence"]["relevant_columns"]:
            assert col in valid_cols, f"Invented column '{col}' detected for question '{q}'!"


def test_12_analyzer_never_produces_numerical_answer(uploaded_dataset_id):
    """12. Verify that the analyzer never outputs calculated numerical answers in Phase 3."""
    questions = [
        "What is the total revenue?",
        "What is the average unit_price?",
        "How many rows are in the dataset?",
        "What is the maximum units_sold?",
    ]
    disallowed_keys = {
        "result", "calculated_value", "numerical_result", "answer",
        "computed_metric", "final_answer", "numeric_value"
    }

    for q in questions:
        response = client.post(
            "/api/questions/analyze",
            json={"dataset_id": uploaded_dataset_id, "question": q},
        )
        assert response.status_code == 200
        data = response.json()
        # Verify no numerical answer payload is embedded
        for key in disallowed_keys:
            assert key not in data, f"Found disallowed calculation key '{key}' in Phase 3 response!"
