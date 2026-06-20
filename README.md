# Data Quality Lens

Data Quality Lens is a small but complete Python portfolio project: a command-line
tool that inspects CSV files, detects common data quality problems, and generates
human-readable Markdown reports plus machine-readable JSON summaries.

[![CI](https://github.com/Tony75546885/data-quality-lens/actions/workflows/ci.yml/badge.svg)](https://github.com/Tony75546885/data-quality-lens/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

It demonstrates:

- clean `src/` package structure
- typed Python with dataclasses
- CSV parsing without heavyweight dependencies
- schema inference and data profiling
- issue detection for missing values, duplicates, cardinality, and outliers
- CLI design with `argparse`
- automated tests and GitHub Actions CI

## Example

```bash
python -m data_quality_lens examples/customers.csv --report report.md --json report.json
```

The generated report answers questions like:

- Which columns contain missing values?
- Which fields look numeric, dates, booleans, or text?
- Are there duplicate rows?
- Are numeric values unusually far from the rest of the dataset?
- Which columns have very high or very low uniqueness?

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Usage

```bash
dqlens examples/customers.csv --report report.md --json report.json
```

Useful options:

```bash
dqlens data.csv --max-examples 8
dqlens data.csv --report quality.md
dqlens data.csv --json quality.json
```

## Project Structure

```text
src/data_quality_lens/
  analyzer.py      # dataset profiling and quality checks
  cli.py           # command-line interface
  models.py        # report dataclasses
  reporting.py     # Markdown and JSON rendering
tests/             # focused test suite
examples/          # sample CSV for quick demo
```

## Development

```bash
PYTHONPATH=src python -m unittest discover -s tests
ruff check .
```

## Why This Belongs In A Portfolio

This project is intentionally practical: it solves a real workflow problem while
showing Python fundamentals that employers care about, including maintainable
module boundaries, tests, CLI ergonomics, typed data structures, and readable
output.
