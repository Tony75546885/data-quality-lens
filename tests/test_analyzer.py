from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from data_quality_lens.analyzer import analyze_csv


class AnalyzeCsvTests(unittest.TestCase):
    def test_analyze_csv_profiles_columns(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "customers.csv"
            csv_path.write_text(
                "id,name,age,signup_date,active\n"
                "1,Ada,31,2024-01-05,true\n"
                "2,Jan,,2024-01-06,false\n"
                "3,Ola,29,2024-01-07,true\n",
                encoding="utf-8",
            )

            report = analyze_csv(csv_path)

        self.assertEqual(report.row_count, 3)
        self.assertEqual(report.column_count, 5)
        self.assertEqual(report.duplicate_rows, 0)
        self.assertEqual(
            {column.name: column.inferred_type for column in report.columns},
            {
                "id": "number",
                "name": "text",
                "age": "number",
                "signup_date": "date",
                "active": "boolean",
            },
        )
        self.assertTrue(
            any(
                issue.column == "age" and issue.title == "Missing values detected"
                for issue in report.issues
            )
        )

    def test_analyze_csv_detects_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "orders.csv"
            csv_path.write_text(
                "order_id,total\n"
                "A001,10.5\n"
                "A001,10.5\n"
                "A002,9999\n"
                "A003,12\n"
                "A004,11\n"
                "A005,13\n",
                encoding="utf-8",
            )

            report = analyze_csv(csv_path)

        self.assertEqual(report.duplicate_rows, 1)
        self.assertTrue(any(issue.title == "Duplicate rows detected" for issue in report.issues))

    def test_empty_dataset_returns_critical_issue(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "empty.csv"
            csv_path.write_text("", encoding="utf-8")

            report = analyze_csv(csv_path)

        self.assertEqual(report.row_count, 0)
        self.assertEqual(report.issues[0].severity, "critical")


if __name__ == "__main__":
    unittest.main()
