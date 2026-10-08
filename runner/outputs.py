from __future__ import annotations

import errno
import os
from collections.abc import Iterator
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
    in_bundle = bool(rel.parts) and rel.parts[0] == "provenance"
    return not in_bundle and not is_nextflow_internal(rel)


def result_files(outdir: Path) -> Iterator[Path]:
    """Enumerate results without hiding unreadable trees or dangling published symlinks.

    pathlib's recursive glob suppresses directory scan errors on newer Python versions. An
    incomplete inventory must never be reported as a successful scientific comparison.
    Follow published directory symlinks, preserving their result paths, and reject cycles.
    """
    def walk(directory: Path, ancestors: frozenset[Path]) -> Iterator[Path]:
        real = directory.resolve()
        if real in ancestors:
            raise OSError(errno.ELOOP, "cyclic result directory symlink", str(directory))
        with os.scandir(directory) as entries:
            for entry in sorted(entries, key=lambda e: e.name):
                path = directory / entry.name
                if not is_result(path.relative_to(outdir)):
                    continue
                if entry.is_dir(follow_symlinks=True):
                    yield from walk(path, ancestors | {real})
                elif entry.is_file(follow_symlinks=True):
                    yield path
                else:
                    raise OSError(errno.EINVAL, "result is missing or not a regular file", str(path))

    yield from walk(outdir, frozenset())


def collect(outdir: Path) -> OutputsReport:
    pinfo = outdir / "pipeline_info"
    paths = sorted(result_files(outdir))
    mqc = next((p for p in paths if p.name == "multiqc_report.html"), None)
    files = tuple(p.relative_to(outdir).as_posix() for p in paths)
    return OutputsReport(pipeline_info=pinfo if pinfo.is_dir() else None,
                         multiqc_report=mqc, files=files)
