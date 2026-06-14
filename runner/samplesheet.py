from __future__ import annotations

import csv
from pathlib import Path

from runner.schema import InputSchema


def validate(path: Path, input_schema: InputSchema) -> list[str]:
    issues: list[str] = []
    if not path.exists():
        return [f"samplesheet not found: {path}"]
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        header = set(reader.fieldnames or [])
        for col in input_schema.columns:
            if col.required and col.name not in header:
                issues.append(f"missing required column '{col.name}'")
        rows = list(reader)
    if not rows:
        issues.append("samplesheet has no data rows")
    base = path.parent
    for i, row in enumerate(rows, start=2):
        for col in input_schema.columns:
            val = (row.get(col.name) or "").strip()
            if col.required and not val:
                issues.append(f"row {i}: empty required '{col.name}'")
            if col.is_path and val and "://" not in val:
                p = Path(val)
                if not p.is_absolute():
                    p = base / p
                if not p.exists():
                    issues.append(f"row {i}: file not found for '{col.name}': {val}")
    return issues
