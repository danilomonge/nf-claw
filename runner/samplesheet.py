from __future__ import annotations

import csv
from pathlib import Path

from runner.schema import InputSchema


def validate(path: Path, input_schema: InputSchema) -> list[str]:
    issues: list[str] = []
    if not path.is_file():
        # Covers both a missing path and one that exists but is a directory — reading either as a
        # samplesheet would otherwise raise FileNotFoundError/IsADirectoryError as a raw traceback.
        return [f"samplesheet not found or not a file: {path}"]
    named = [c for c in input_schema.columns if c.name]
    # Read as utf-8-sig so a leading UTF-8 BOM (common in spreadsheet-exported CSVs) is stripped:
    # otherwise a leading BOM stays glued to the first header (it reads as `\ufeffsample`) and a
    # required column looks missing.
    # No-op when there is no BOM.
    # A non-text file (e.g. an .xlsx or other binary handed in by mistake) would raise
    # UnicodeDecodeError; report it as a clear samplesheet issue instead of a raw traceback.
    try:
        if not named:
            # Headerless, one value per line (e.g. nf-core/fetchngs accession list). csv.DictReader
            # would mistake the first value for a header; just require >=1 non-empty value. Per-value
            # pattern checks are delegated to nf-schema, exactly as for named-column samplesheets.
            values = [ln.strip() for ln in path.read_text(encoding="utf-8-sig").splitlines()
                      if ln.strip()]
            return [] if values else ["input file has no values"]
        # nf-schema picks the parser from the file extension; mirror that exactly so a `.tsv`
        # (e.g. nf-core/airrflow, which mandates `.tsv`) is split on TAB, not read as one CSV column.
        delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
        with path.open(newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh, delimiter=delimiter)
            header = set(reader.fieldnames or [])
            for col in named:
                if col.required and col.name not in header:
                    issues.append(f"missing required column '{col.name}'")
            rows = list(reader)
    except UnicodeDecodeError:
        return [f"samplesheet is not valid UTF-8 text: {path} "
                "(is it a real .csv/.tsv, not a binary file such as .xlsx?)"]
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
