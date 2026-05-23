from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Severity = Literal["info", "warning", "critical"]


@dataclass(frozen=True)
class QualityIssue:
    severity: Severity
    title: str
    detail: str
    column: str | None = None
    examples: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ColumnProfile:
    name: str
    inferred_type: str
    total_values: int
    missing_values: int
    unique_values: int
    sample_values: list[str]
    min_value: float | str | None = None
    max_value: float | str | None = None
    mean: float | None = None

    @property
    def missing_rate(self) -> float:
        if self.total_values == 0:
            return 0.0
        return self.missing_values / self.total_values

    @property
    def uniqueness_rate(self) -> float:
        present_values = self.total_values - self.missing_values
        if present_values == 0:
            return 0.0
        return self.unique_values / present_values


@dataclass(frozen=True)
class DataQualityReport:
    source_path: str
    row_count: int
    column_count: int
    duplicate_rows: int
    columns: list[ColumnProfile]
    issues: list[QualityIssue]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
