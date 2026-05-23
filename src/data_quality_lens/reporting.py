from __future__ import annotations

import json

from data_quality_lens.models import DataQualityReport, QualityIssue


def render_markdown(report: DataQualityReport) -> str:
    lines = [
        "# Data Quality Report",
        "",
        f"Source: `{report.source_path}`",
        "",
        "## Summary",
        "",
        f"- Rows: {report.row_count}",
        f"- Columns: {report.column_count}",
        f"- Duplicate rows: {report.duplicate_rows}",
        f"- Issues: {len(report.issues)}",
        "",
        "## Columns",
        "",
        "| Column | Type | Missing | Unique | Min | Max | Mean | Samples |",
        "| --- | --- | ---: | ---: | --- | --- | ---: | --- |",
    ]

    for column in report.columns:
        lines.append(
            "| {name} | {type} | {missing} ({missing_rate:.0%}) | {unique} | {min} | {max} | {mean} | {samples} |".format(
                name=_escape_pipe(column.name),
                type=column.inferred_type,
                missing=column.missing_values,
                missing_rate=column.missing_rate,
                unique=column.unique_values,
                min=_empty(column.min_value),
                max=_empty(column.max_value),
                mean=_empty(column.mean),
                samples=_escape_pipe(", ".join(column.sample_values)),
            )
        )

    lines.extend(["", "## Issues", ""])
    if not report.issues:
        lines.append("No data quality issues detected.")
    else:
        for issue in report.issues:
            lines.extend(_render_issue(issue))

    return "\n".join(lines).strip() + "\n"


def render_json(report: DataQualityReport) -> str:
    return json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n"


def _render_issue(issue: QualityIssue) -> list[str]:
    title = f"### [{issue.severity.upper()}] {issue.title}"
    column = f"Column: `{issue.column}`" if issue.column else "Dataset-level issue"
    lines = [title, "", column, "", issue.detail]
    if issue.examples:
        lines.extend(["", "Examples: " + ", ".join(f"`{example}`" for example in issue.examples)])
    lines.append("")
    return lines


def _empty(value: object) -> str:
    if value is None:
        return "-"
    return str(value)


def _escape_pipe(value: str) -> str:
    return value.replace("|", "\\|")
