"""Cleaning for the UCI Algerian Forest Fires Dataset.

The raw CSV is not a plain table: it is two stacked per-region blocks, each
with its own title line and its own repeated header line, and the column
names carry stray whitespace (e.g. ``" RH"``, ``"Rain "``). There is also one
row (14/07/2012, Sidi-Bel Abbes) where a missing comma merges the DC and ISI
columns into a single token (``"14.6 9"``); this was found by diffing the
expected column count against every row in the file, not assumed away.

``_parse_raw_rows`` depends only on the standard library so it can be unit
-checked without the rest of the ML stack installed. ``load_clean_dataframe``
wraps it with pandas for the training/inference code.
"""

import csv
import io
from pathlib import Path
from typing import Any

RAW_FEATURE_COLUMNS = ["Temperature", "RH", "Ws", "Rain"]
FWI_COLUMNS = ["FFMC", "DMC", "DC", "ISI", "BUI", "FWI"]
ALL_FEATURE_COLUMNS = RAW_FEATURE_COLUMNS + FWI_COLUMNS
LABEL_COLUMN = "fire"

# This order MUST match exactly the feature order sent by
# backend/routers/risk.py to model.predict_proba(). Make this the single
# source of truth so training and inference can never silently drift out
# of sync (a very common bug class in ML: feature-order mismatch).
PRODUCTION_FEATURE_ORDER = ["Temperature", "RH", "Rain", "Ws"]

_REGION_TITLES = {
    "Bejaia Region Dataset": "Bejaia",
    "Sidi-Bel Abbes Region Dataset": "Sidi-Bel Abbes",
}
_EXPECTED_COLUMNS = 14


def _split_into_region_blocks(lines: list[str]) -> list[tuple[str, list[str]]]:
    blocks: list[tuple[str, list[str]]] = []
    current_region: str | None = None
    current_lines: list[str] = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if line in _REGION_TITLES:
            if current_region is not None:
                blocks.append((current_region, current_lines))
            current_region = _REGION_TITLES[line]
            current_lines = []
            continue
        current_lines.append(line)

    if current_region is not None:
        blocks.append((current_region, current_lines))

    return blocks


def _fix_malformed_row(line: str) -> str:
    """Split a token like ``"14.6 9"`` (merged DC/ISI) back into two fields.

    Only rows with a short-by-one comma count are touched; a correctly
    formed row is returned unchanged.
    """
    if line.count(",") == _EXPECTED_COLUMNS - 2:
        parts = line.split(",")
        for i, part in enumerate(parts):
            if " " in part.strip():
                left, right = part.strip().split(" ", 1)
                parts[i] = left
                parts.insert(i + 1, right)
                break
        line = ",".join(parts)
    return line


def _parse_raw_rows(csv_text: str) -> list[dict[str, Any]]:
    lines = csv_text.splitlines()
    blocks = _split_into_region_blocks(lines)

    rows: list[dict[str, Any]] = []
    for region, block_lines in blocks:
        header_line, *data_lines = block_lines
        fieldnames = [name.strip() for name in header_line.split(",")]

        for line in data_lines:
            line = _fix_malformed_row(line)
            reader = csv.DictReader(io.StringIO(line), fieldnames=fieldnames)
            row = next(reader)

            if len(row) != _EXPECTED_COLUMNS:
                raise ValueError(f"Unexpected column count in row: {line!r}")

            cleaned = {k.strip(): v.strip() for k, v in row.items()}
            cleaned["region"] = region
            cleaned[LABEL_COLUMN] = 1 if cleaned["Classes"].startswith("fire") else 0
            rows.append(cleaned)

    return rows


def load_clean_dataframe(csv_path: Path):
    import pandas as pd

    raw_text = csv_path.read_text(encoding="utf-8", errors="replace")
    rows = _parse_raw_rows(raw_text)
    df = pd.DataFrame(rows)

    numeric_columns = ["day", "month", "year"] + ALL_FEATURE_COLUMNS
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="raise")

    df["date"] = pd.to_datetime(df[["year", "month", "day"]])
    df = df.drop(columns=["Classes", "day", "month", "year"])

    return df.sort_values("date").reset_index(drop=True)
