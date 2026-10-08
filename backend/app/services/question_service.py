"""Deterministic Question Analysis and Answerability Service for A.D.A.N.

Implements PS08 Core Principle:
- Deterministic analysis before any code synthesis or LLM execution.
- Prefers 'CANNOT_DETERMINE' over fabricating an answer.
- Detects ambiguities requiring 'NEEDS_CLARIFICATION'.
- Strict evidence tracing based on the verified dataset profile.
"""

from typing import List, Optional, Set, Tuple
import re

from app.models.dataset import ColumnProfile, DatasetProfile
from app.models.question import QuestionAnalysisResponse, QuestionEvidence
from app.services.dataset_service import DatasetService


class QuestionService:
    """Service evaluating analytical question answerability against dataset profiles."""

    # Common aggregation and analytical intent keywords
    AGGREGATION_TERMS = {
        "total": "sum",
        "sum": "sum",
        "overall": "sum",
        "aggregate": "sum",
        "average": "mean",
        "avg": "mean",
        "mean": "mean",
        "median": "median",
        "minimum": "min",
        "min": "min",
        "lowest": "min",
        "maximum": "max",
        "max": "max",
        "highest": "max",
        "peak": "max",
        "count": "count",
        "how many": "count",
        "number of": "count",
    }

    # Stopwords to filter when extracting unknown concept keywords
    STOPWORDS = {
        "what", "is", "was", "the", "are", "were", "a", "an", "of", "in", "for",
        "to", "on", "at", "by", "from", "with", "about", "show", "tell", "me",
        "find", "calculate", "compute", "give", "dataset", "data", "table",
        "this", "that", "these", "those", "how", "much", "many", "there", "any",
        "please", "can", "you", "does", "do", "did", "which"
    }

    @classmethod
    def analyze_question(
        cls, dataset_id: str, question: str
    ) -> QuestionAnalysisResponse:
        """Deterministically evaluates if a question is ANSWERABLE, CANNOT_DETERMINE,

        or NEEDS_CLARIFICATION given the dataset profile.
        """
        # 1. Retrieve dataset profile
        profile = DatasetService.get_profile(dataset_id)
        if not profile:
            raise ValueError(f"Dataset with ID '{dataset_id}' not found.")

        q_clean = question.strip()
        q_lower = q_clean.lower()

        # 2. Check for Quarter Ambiguity (Case 4: NEEDS_CLARIFICATION)
        # e.g. "What was revenue in Q1?" -> calendar vs. fiscal quarter ambiguity
        quarter_match = re.search(r"\b(q[1-4]|quarter\s*[1-4])\b", q_lower)
        if quarter_match:
            has_calendar = "calendar" in q_lower
            has_fiscal = "fiscal" in q_lower
            if not has_calendar and not has_fiscal:
                q_term = quarter_match.group(0).upper().replace(" ", "")
                return QuestionAnalysisResponse(
                    dataset_id=dataset_id,
                    question=q_clean,
                    status="NEEDS_CLARIFICATION",
                    reason=(
                        f"The question references '{q_term}' without specifying whether it refers "
                        f"to the standard calendar quarter (Jan-Mar) or an organizational fiscal quarter."
                    ),
                    evidence=QuestionEvidence(
                        relevant_columns=cls._find_matched_columns(q_lower, profile),
                        missing_requirements=[
                            "Specification of quarter convention (calendar vs. fiscal quarter)"
                        ],
                    ),
                    interpretation="Quarter-based filtering requested, but quarter convention is ambiguous.",
                    suggested_next_step=(
                        f"Specify whether {q_term} refers to calendar {q_term} or fiscal {q_term}, "
                        f"and confirm the target year."
                    ),
                )

        # 3. Check for Temporal / Year Range Constraints (Case 3: CANNOT_DETERMINE)
        # Extract 4-digit years from question
        year_matches = [int(y) for y in re.findall(r"\b(19\d\d|20\d\d)\b", q_clean)]
        if year_matches:
            if not profile.date_ranges:
                return QuestionAnalysisResponse(
                    dataset_id=dataset_id,
                    question=q_clean,
                    status="CANNOT_DETERMINE",
                    reason=(
                        f"The question requests data for year {year_matches[0]}, but the dataset "
                        f"does not contain any date or timestamp columns."
                    ),
                    evidence=QuestionEvidence(
                        missing_requirements=[
                            f"Date or timestamp column covering year {year_matches[0]}"
                        ]
                    ),
                    interpretation=f"Temporal query for year {year_matches[0]} on non-temporal dataset.",
                    suggested_next_step=(
                        "Provide a dataset with date/timestamp columns or remove the year constraint."
                    ),
                )

            # Check if requested year falls within detected date ranges
            min_years = []
            max_years = []
            date_range_strs = []
            for dr in profile.date_ranges:
                date_range_strs.append(f"{dr.min_date[:10]} to {dr.max_date[:10]}")
                try:
                    min_years.append(int(dr.min_date[:4]))
                    max_years.append(int(dr.max_date[:4]))
                except (ValueError, TypeError):
                    continue

            if min_years and max_years:
                dataset_min_year = min(min_years)
                dataset_max_year = max(max_years)
                for requested_year in year_matches:
                    if (
                        requested_year < dataset_min_year
                        or requested_year > dataset_max_year
                    ):
                        avail_range = "; ".join(date_range_strs)
                        return QuestionAnalysisResponse(
                            dataset_id=dataset_id,
                            question=q_clean,
                            status="CANNOT_DETERMINE",
                            reason=(
                                f"The requested year ({requested_year}) is outside the available "
                                f"dataset date range ({avail_range})."
                            ),
                            evidence=QuestionEvidence(
                                available_date_range=avail_range,
                                missing_requirements=[
                                    f"Data records covering the year {requested_year}"
                                ],
                            ),
                            interpretation=(
                                f"Temporal query for year {requested_year}, but dataset only covers "
                                f"{dataset_min_year} through {dataset_max_year}."
                            ),
                            suggested_next_step=(
                                f"Adjust the query to within the available range ({avail_range}) "
                                f"or upload data covering {requested_year}."
                            ),
                        )

        # 4. Check for Duplicate Row Inquiries
        if re.search(r"\b(duplicate|duplicates|repeated rows?|dedup)\b", q_lower):
            col_names = [col.name for col in profile.columns]
            return QuestionAnalysisResponse(
                dataset_id=dataset_id,
                question=q_clean,
                status="ANSWERABLE",
                reason=(
                    f"The dataset profile deterministically tracks duplicate row counts "
                    f"({profile.duplicate_row_count} duplicate row(s) identified across all columns)."
                ),
                evidence=QuestionEvidence(
                    relevant_columns=col_names,
                    data_quality_notes=[
                        f"Dataset contains {profile.duplicate_row_count} duplicate row(s) out of {profile.row_count} total rows."
                    ],
                ),
                interpretation="Audit of duplicate records across the dataset schema.",
                suggested_next_step="Inspection of duplicate row frequency is ready for reporting.",
            )

        # 5. Check for Row Count / Dimensionality Inquiries
        if re.search(r"\b(how many (rows|records|entries)|total rows|row count)\b", q_lower):
            return QuestionAnalysisResponse(
                dataset_id=dataset_id,
                question=q_clean,
                status="ANSWERABLE",
                reason=(
                    f"The dataset contains deterministic row count metadata ({profile.row_count} rows)."
                ),
                evidence=QuestionEvidence(
                    relevant_columns=[col.name for col in profile.columns],
                    data_quality_notes=[f"Total rows: {profile.row_count}, Total columns: {profile.column_count}"],
                ),
                interpretation="Query asks for dataset record count.",
                suggested_next_step="Proceed to retrieve verified row count.",
            )

        # 6. Column and Concept Matching
        matched_columns = cls._find_matched_columns(q_lower, profile)
        detected_aggregation = cls._detect_aggregation(q_lower)

        # 7. Check if an unknown concept was specifically requested
        # e.g., "What is the total profit?" where profit is not in matched_columns
        unmatched_concepts = cls._find_unmatched_concepts(
            q_clean, profile, matched_columns
        )

        if unmatched_concepts:
            missing_concept = unmatched_concepts[0]
            return QuestionAnalysisResponse(
                dataset_id=dataset_id,
                question=q_clean,
                status="CANNOT_DETERMINE",
                reason=(
                    f"The dataset does not contain sufficient information to calculate {missing_concept}."
                ),
                evidence=QuestionEvidence(
                    relevant_columns=matched_columns,
                    missing_requirements=[
                        f"Column or data fields representing '{missing_concept}'"
                    ],
                ),
                interpretation=(
                    f"Query requests calculation involving '{missing_concept}', which is absent from dataset."
                ),
                suggested_next_step=(
                    f"Upload a dataset containing '{missing_concept}' or rephrase query using available columns."
                ),
            )

        # 8. If NO columns matched and question is too vague / underspecified
        if not matched_columns:
            return QuestionAnalysisResponse(
                dataset_id=dataset_id,
                question=q_clean,
                status="NEEDS_CLARIFICATION",
                reason=(
                    "The question does not specify which column, metric, or relationship to analyze."
                ),
                evidence=QuestionEvidence(
                    missing_requirements=[
                        "Specific column name or measurable attribute from dataset"
                    ]
                ),
                interpretation="General or ambiguous question with no identifiable column reference.",
                suggested_next_step=(
                    f"Specify one of the available columns ({', '.join(c.name for c in profile.columns[:5])}) "
                    f"and the desired calculation (e.g., total, average, min, max)."
                ),
            )

        # 9. Columns were matched -> Evaluate Compatibility & Data Quality
        relevant_cols_objs = [
            c for c in profile.columns if c.name in matched_columns
        ]

        # Check numeric requirement for mathematical aggregations
        if detected_aggregation in ("sum", "mean", "median"):
            non_numeric = [
                c.name for c in relevant_cols_objs if c.name not in profile.numeric_columns
            ]
            if non_numeric and len(non_numeric) == len(relevant_cols_objs):
                return QuestionAnalysisResponse(
                    dataset_id=dataset_id,
                    question=q_clean,
                    status="CANNOT_DETERMINE",
                    reason=(
                        f"The requested column '{non_numeric[0]}' is of non-numeric type "
                        f"('{relevant_cols_objs[0].dtype}') and cannot support a {detected_aggregation} calculation."
                    ),
                    evidence=QuestionEvidence(
                        relevant_columns=matched_columns,
                        missing_requirements=[
                            f"Numeric representation for column '{non_numeric[0]}'"
                        ],
                    ),
                    interpretation=f"{detected_aggregation.title()} calculation on non-numeric column.",
                    suggested_next_step=(
                        f"Choose a numeric column ({', '.join(profile.numeric_columns) or 'none available'}) "
                        f"or request a categorical frequency count."
                    ),
                )

        # Build data quality notes (Missing values & duplicates)
        data_quality_notes: List[str] = []
        for col_obj in relevant_cols_objs:
            if col_obj.missing_count > 0:
                if col_obj.missing_count == profile.row_count:
                    # 100% missing
                    return QuestionAnalysisResponse(
                        dataset_id=dataset_id,
                        question=q_clean,
                        status="CANNOT_DETERMINE",
                        reason=f"Column '{col_obj.name}' contains 100% missing values (0 non-null records).",
                        evidence=QuestionEvidence(
                            relevant_columns=[col_obj.name],
                            missing_requirements=[f"Valid data records for '{col_obj.name}'"],
                        ),
                        interpretation="Calculation requested on an entirely empty column.",
                        suggested_next_step="Provide data with populated records.",
                    )
                data_quality_notes.append(
                    f"Column '{col_obj.name}' contains {col_obj.missing_count} missing value(s) "
                    f"({col_obj.missing_percentage}%). Calculation is feasible but will require an explicit "
                    f"missing-data policy (e.g., omission or imputation)."
                )

        if profile.duplicate_row_count > 0:
            data_quality_notes.append(
                f"Dataset contains {profile.duplicate_row_count} duplicate row(s). "
                f"Deduplication policy may need to be specified."
            )

        # Date range context if dates exist
        available_date_str = None
        if profile.date_ranges:
            available_date_str = "; ".join(
                f"{dr.min_date[:10]} to {dr.max_date[:10]}" for dr in profile.date_ranges
            )

        agg_label = detected_aggregation or "analytical calculation"
        cols_label = ", ".join(matched_columns)

        return QuestionAnalysisResponse(
            dataset_id=dataset_id,
            question=q_clean,
            status="ANSWERABLE",
            reason=(
                f"The dataset contains the required column(s) ({cols_label}) "
                f"to support the requested {agg_label}."
            ),
            evidence=QuestionEvidence(
                relevant_columns=matched_columns,
                available_date_range=available_date_str,
                missing_requirements=[],
                data_quality_notes=data_quality_notes,
            ),
            interpretation=f"Perform {agg_label} on column(s) [{cols_label}].",
            suggested_next_step=(
                "Question is verified as answerable. Ready for code synthesis and calculation in subsequent phase."
            ),
        )

    @classmethod
    def _find_matched_columns(
        cls, q_lower: str, profile: DatasetProfile
    ) -> List[str]:
        """Finds columns in profile that are referenced in the question."""
        matched: List[str] = []
        q_norm = q_lower.replace("_", " ").replace("-", " ")

        for col in profile.columns:
            col_name_lower = col.name.lower()
            col_norm = col_name_lower.replace("_", " ").replace("-", " ")

            # 1. Exact match with word boundary
            pattern_exact = r"\b" + re.escape(col_name_lower) + r"\b"
            if re.search(pattern_exact, q_lower):
                if col.name not in matched:
                    matched.append(col.name)
                continue

            # 2. Normalized match with word boundary
            pattern_norm = r"\b" + re.escape(col_norm) + r"\b"
            if re.search(pattern_norm, q_norm):
                if col.name not in matched:
                    matched.append(col.name)
                continue

        return matched

    @classmethod
    def _detect_aggregation(cls, q_lower: str) -> Optional[str]:
        """Detects aggregation intent from question."""
        for term, agg in cls.AGGREGATION_TERMS.items():
            if re.search(r"\b" + re.escape(term) + r"\b", q_lower):
                return agg
        return None

    @classmethod
    def _find_unmatched_concepts(
        cls, q_clean: str, profile: DatasetProfile, matched_cols: List[str]
    ) -> List[str]:
        """Extracts candidate target concepts requested in the question that are NOT

        present in the dataset (e.g. 'profit', 'discount', 'churn').
        """
        q_lower = q_clean.lower()
        # Look for phrases following aggregation or asking verbs:
        # e.g., "total <concept>", "average <concept>", "what is the <concept>"
        patterns = [
            r"\b(?:total|sum|average|avg|mean|median|min|minimum|max|maximum)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            r"\b(?:what is the|what was the|what are the)\s+(?:total\s+|average\s+|mean\s+)?([a-zA-Z_][a-zA-Z0-9_]*)",
        ]

        unmatched: List[str] = []
        matched_cols_norm = {
            c.lower().replace("_", "").replace(" ", "") for c in matched_cols
        }
        all_cols_norm = {
            c.name.lower().replace("_", "").replace(" ", "") for c in profile.columns
        }

        for pat in patterns:
            for match in re.finditer(pat, q_lower):
                concept = match.group(1).strip()
                if not concept or concept in cls.STOPWORDS or concept in cls.AGGREGATION_TERMS:
                    continue
                concept_norm = concept.replace("_", "").replace(" ", "")
                if concept_norm not in all_cols_norm:
                    if concept not in unmatched:
                        unmatched.append(concept)

        return unmatched
