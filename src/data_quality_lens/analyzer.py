from __future__ import annotations

import csv
import math
from collections import Counter
from datetime import date
from pathlib import Path

from data_quality_lens.models import ColumnProfile, DataQualityReport, QualityIssue

MISSING_MARKERS = {"", "na", "n/a", "null", "none", "-"}


def analyze_csv(path: str | Path, *, max_examples: int = 5) -> DataQualityReport:
    csv_path = Path(path)
    rows = _read_csv(csv_path)

    if not rows:
        return DataQualityReport(
            source_path=str(csv_path),
            row_count=0,
            column_count=0,
            duplicate_rows=0,
            columns=[],
            issues=[
                QualityIssue(
                    severity="critical",
                    title="Empty dataset",
                    detail="The file contains no data rows.",
                )
            ],
        )

    fieldnames = list(rows[0].keys())
    duplicate_rows = _count_duplicate_rows(rows, fieldnames)
    profiles = [
        _profile_column(name, [row.get(name, "") for row in rows], max_examples=max_examples)
        for name in fieldnames
    ]

    issues = _detect_dataset_issues(rows, duplicate_rows)
    for profile in profiles:
        issues.extend(_detect_column_issues(profile))
        raw_values = [row.get(profile.name, "") for row in rows]
        issues.extend(_detect_outliers(profile, raw_values, max_examples))

    return DataQualityReport(
        source_path=str(csv_path),
        row_count=len(rows),
        column_count=len(fieldnames),
        duplicate_rows=duplicate_rows,
        columns=profiles,
        issues=issues,
    )


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        return [dict(row) for row in reader]


def _count_duplicate_rows(rows: list[dict[str, str]], fieldnames: list[str]) -> int:
    normalized_rows = [
        tuple(_normalize(row.get(field, "")) for field in fieldnames)
        for row in rows
    ]
    counts = Counter(normalized_rows)
    return sum(count - 1 for count in counts.values() if count > 1)


def _profile_column(name: str, values: list[str], *, max_examples: int) -> ColumnProfile:
    normalized_values = [_normalize(value) for value in values]
    present_values = [value for value in normalized_values if not _is_missing(value)]
    inferred_type = _infer_type(present_values)
    unique_values = len(set(present_values))
    sample_values = list(dict.fromkeys(present_values[: max_examples * 2]))[:max_examples]

    numeric_values = [_to_float(value) for value in present_values]
    numeric_values = [value for value in numeric_values if value is not None]

    if inferred_type == "number" and numeric_values:
        return ColumnProfile(
            name=name,
            inferred_type=inferred_type,
            total_values=len(values),
            missing_values=len(values) - len(present_values),
            unique_values=unique_values,
            sample_values=sample_values,
            min_value=round(min(numeric_values), 4),
            max_value=round(max(numeric_values), 4),
            mean=round(sum(numeric_values) / len(numeric_values), 4),
        )

    return ColumnProfile(
        name=name,
        inferred_type=inferred_type,
        total_values=len(values),
        missing_values=len(values) - len(present_values),
        unique_values=unique_values,
        sample_values=sample_values,
        min_value=min(present_values) if present_values else None,
        max_value=max(present_values) if present_values else None,
    )


def _infer_type(values: list[str]) -> str:
    if not values:
        return "empty"

    checks = {
        "number": _to_float,
        "date": _to_date,
        "boolean": _to_bool,
    }
    for type_name, converter in checks.items():
        matches = sum(converter(value) is not None for value in values)
        if matches / len(values) >= 0.9:
            return type_name

    return "text"


def _detect_dataset_issues(rows: list[dict[str, str]], duplicate_rows: int) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    if duplicate_rows:
        issues.append(
            QualityIssue(
                severity="warning",
                title="Duplicate rows detected",
                detail=f"Found {duplicate_rows} duplicate row(s) across {len(rows)} records.",
            )
        )
    return issues


def _detect_column_issues(profile: ColumnProfile) -> list[QualityIssue]:
    issues: list[QualityIssue] = []

    if profile.missing_rate >= 0.4:
        issues.append(
            QualityIssue(
                severity="critical",
                title="High missing-value rate",
                detail=f"{profile.missing_rate:.0%} of values are missing.",
                column=profile.name,
            )
        )
    elif profile.missing_values:
        issues.append(
            QualityIssue(
                severity="warning",
                title="Missing values detected",
                detail=f"{profile.missing_values} value(s) are missing.",
                column=profile.name,
            )
        )

    if profile.uniqueness_rate == 1.0 and profile.total_values >= 10:
        issues.append(
            QualityIssue(
                severity="info",
                title="Column looks like an identifier",
                detail="Every non-empty value is unique.",
                column=profile.name,
            )
        )
    elif 0 < profile.uniqueness_rate <= 0.05 and profile.total_values >= 20:
        issues.append(
            QualityIssue(
                severity="info",
                title="Low-cardinality column",
                detail=f"Only {profile.unique_values} unique value(s) appear in this column.",
                column=profile.name,
            )
        )

    return issues


def _detect_outliers(
    profile: ColumnProfile, raw_values: list[str], max_examples: int
) -> list[QualityIssue]:
    if profile.inferred_type != "number":
        return []

    values = [_to_float(_normalize(value)) for value in raw_values]
    numeric_values = [value for value in values if value is not None]
    if len(numeric_values) < 5:
        return []

    mean = sum(numeric_values) / len(numeric_values)
    variance = sum((value - mean) ** 2 for value in numeric_values) / len(numeric_values)
    standard_deviation = math.sqrt(variance)
    if standard_deviation == 0:
        return []

    outliers = [
        value
        for value in numeric_values
        if abs((value - mean) / standard_deviation) >= 3
    ]
    if not outliers:
        return []

    examples = [str(round(value, 4)) for value in outliers[:max_examples]]
    return [
        QualityIssue(
            severity="warning",
            title="Possible numeric outliers",
            detail=f"Found {len(outliers)} value(s) at least 3 standard deviations from the mean.",
            column=profile.name,
            examples=examples,
        )
    ]


def _normalize(value: str | None) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _is_missing(value: str) -> bool:
    return value.casefold() in MISSING_MARKERS


def _to_float(value: str) -> float | None:
    try:
        return float(value.replace(",", "."))
    except ValueError:
        return None


def _to_date(value: str) -> date | None:
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            from datetime import datetime

            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _to_bool(value: str) -> bool | None:
    normalized = value.casefold()
    if normalized in {"true", "yes", "y", "1", "tak"}:
        return True
    if normalized in {"false", "no", "n", "0", "nie"}:
        return False
    return None
