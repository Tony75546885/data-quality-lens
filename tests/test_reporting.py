from __future__ import annotations

import unittest

from data_quality_lens.models import ColumnProfile, DataQualityReport, QualityIssue
from data_quality_lens.reporting import render_json, render_markdown


class ReportingTests(unittest.TestCase):
    def test_render_markdown_contains_summary_and_issues(self) -> None:
        report = DataQualityReport(
            source_path="sample.csv",
            row_count=2,
            column_count=1,
            duplicate_rows=0,
            columns=[
                ColumnProfile(
                    name="score",
                    inferred_type="number",
                    total_values=2,
                    missing_values=0,
                    unique_values=2,
                    sample_values=["10", "11"],
                    min_value=10,
                    max_value=11,
                    mean=10.5,
                )
            ],
            issues=[
                QualityIssue(
                    severity="warning",
                    title="Example issue",
                    detail="Something should be reviewed.",
                    column="score",
                )
            ],
        )

        markdown = render_markdown(report)

        self.assertIn("# Data Quality Report", markdown)
        self.assertIn("- Rows: 2", markdown)
        self.assertIn("[WARNING] Example issue", markdown)
        self.assertIn("Column: `score`", markdown)

    def test_render_json_is_machine_readable(self) -> None:
        report = DataQualityReport(
            source_path="sample.csv",
            row_count=0,
            column_count=0,
            duplicate_rows=0,
            columns=[],
            issues=[],
        )

        payload = render_json(report)

        self.assertIn('"source_path": "sample.csv"', payload)
        self.assertTrue(payload.endswith("\n"))


if __name__ == "__main__":
    unittest.main()
