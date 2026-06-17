from __future__ import annotations

import csv
from pathlib import Path

from runner.schema import InputSchema


def validate(path: Path, input_schema: InputSchema) -> list[str]:
    issues: list[str] = []
    if not path.exists():
        return [f"samplesheet not found: {path}"]
    named = [c for c in input_schema.columns if c.name]
    if not named:
        # Headerless, one value per line (e.g. nf-core/fetchngs accession list). csv.DictReader
        # would mistake the first value for a header; just require >=1 non-empty value. Per-value
        # pattern checks are delegated to nf-schema, exactly as for named-column samplesheets.
        values = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        return [] if values else ["input file has no values"]
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        header = set(reader.fieldnames or [])
        for col in named:
            if col.required and col.name not in header:
                issues.append(f"missing required column '{col.name}'")
        rows = list(reader)
    if not rows:
        issues.append("samplesheet has no data rows")
    base = path.parent
    for i, row in enumerate(rows, start=2):
        for col in named:
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
