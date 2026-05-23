from __future__ import annotations

import argparse
from pathlib import Path

from data_quality_lens.analyzer import analyze_csv
from data_quality_lens.reporting import render_json, render_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dqlens",
        description="Profile a CSV file and generate a data quality report.",
    )
    parser.add_argument("csv_path", type=Path, help="Path to the CSV file to analyze.")
    parser.add_argument("--report", type=Path, help="Write a Markdown report to this path.")
    parser.add_argument("--json", type=Path, help="Write a JSON report to this path.")
    parser.add_argument(
        "--max-examples",
        type=int,
        default=5,
        help="Maximum number of example values to include per column or issue.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    report = analyze_csv(args.csv_path, max_examples=args.max_examples)
    markdown = render_markdown(report)

    if args.report:
        args.report.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)

    if args.json:
        args.json.write_text(render_json(report), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
