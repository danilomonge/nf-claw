from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OutputsReport:
    pipeline_info: Path | None
    multiqc_report: Path | None
    files: tuple[str, ...]


def collect(outdir: Path) -> OutputsReport:
    pinfo = outdir / "pipeline_info"
    mqc = next(iter(sorted(outdir.glob("**/multiqc_report.html"))), None)
    files = tuple(sorted(str(p.relative_to(outdir)) for p in outdir.rglob("*") if p.is_file()))
    return OutputsReport(pipeline_info=pinfo if pinfo.is_dir() else None,
                         multiqc_report=mqc, files=files)
