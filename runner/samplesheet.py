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
        if path.suffix.lower() not in (".csv", ".tsv"):
            # Some nf-core pipelines (notably Sarek) accept JSON/YAML inputs while also shipping a
            # tabular schema_input.json. We cannot parse those formats with DictReader, so only the
            # existence check above is local; nf-schema performs the format-specific validation.
            return []
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
        values = {col.name: (row.get(col.name) or "").strip() for col in named}
        for trigger, required in input_schema.dependent_required:
            if values.get(trigger):
                for req in required:
                    if not values.get(req):
                        issues.append(f"row {i}: '{trigger}' requires '{req}'")
        branches = input_schema.any_of_dependent_required
        if branches and not _any_branch_satisfied(values, branches):
            issues.append(f"row {i}: {_any_of_message(branches)}")
    return issues


def _branch_satisfied(values: dict[str, str], branch: tuple[str, tuple[str, ...]]) -> bool:
    trigger, required = branch
    return not values.get(trigger) or all(values.get(req) for req in required)


def _any_branch_satisfied(
    values: dict[str, str],
    branches: tuple[tuple[tuple[str, tuple[str, ...]], ...], ...],
) -> bool:
    return any(all(_branch_satisfied(values, requirement) for requirement in option)
               for option in branches)


def _any_of_message(branches: tuple[tuple[tuple[str, tuple[str, ...]], ...], ...]) -> str:
    options: list[str] = []
    triggers = sorted({trigger for option in branches for trigger, _ in option})
    if len(triggers) == 1 and all(len(option) == 1 and option[0][0] == triggers[0]
                                  for option in branches):
        reqs = [req for option in branches for req in option[0][1]]
        return (f"when '{triggers[0]}' is set, provide one of: "
                + ", ".join(f"'{req}'" for req in reqs))
    for option in branches:
        parts: list[str] = []
        for trigger, required in option:
            reqs = ", ".join(f"'{req}'" for req in required)
            parts.append(f"{reqs} when '{trigger}' is set")
        options.append(" and ".join(parts))
    if len(triggers) == 1:
        return f"when '{triggers[0]}' is set, provide one of: {', '.join(options)}"
    return f"provide one of these conditional column sets: {', '.join(options)}"
