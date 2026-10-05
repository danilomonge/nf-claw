from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OutputsReport:
    pipeline_info: Path | None
    multiqc_report: Path | None
    files: tuple[str, ...]


def is_nextflow_internal(rel: Path) -> bool:
    """Whether a path (relative to the outdir) is a Nextflow engine internal, not a result.
    When Nextflow launches from the outdir its state lands there: the `.nextflow/` directory and
    `.nextflow.log*` files. Those are never pipeline outputs."""
    head = rel.parts[0] if rel.parts else ""
    return head == ".nextflow" or head.startswith(".nextflow.log")


def is_result(rel: Path) -> bool:
    """Whether a path (relative to the outdir) is one of the run's results: not Nextflow's own state
    and not nfclaw's `provenance/` bundle, which describes the run rather than being part of it."""
    in_bundle = len(rel.parts) > 1 and rel.parts[0] == "provenance"
    return not in_bundle and not is_nextflow_internal(rel)


def collect(outdir: Path) -> OutputsReport:
    pinfo = outdir / "pipeline_info"
    mqc = next(iter(sorted(outdir.glob("**/multiqc_report.html"))), None)
    files = tuple(sorted(str(rel) for p in outdir.rglob("*")
                         if p.is_file() and is_result(rel := p.relative_to(outdir))))
    return OutputsReport(pipeline_info=pinfo if pinfo.is_dir() else None,
                         multiqc_report=mqc, files=files)
