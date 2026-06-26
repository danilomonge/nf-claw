"""Turn a failed Nextflow run into an actionable hint.

When `nextflow run` exits non-zero, `execution.run` passes its stderr (and the run's relevant
paths) here. We match a small set of high-confidence failure signatures seen in real runs and
return the exact nfclaw fix for each, so the caller stops guessing and the error names the
remedy. No signature → empty list (the raw log is still surfaced by the caller).
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable


def diagnose(stderr: str, *, paths: Iterable[Path] = ()) -> list[str]:
    """Zero or more actionable hints for a failed run, from known stderr signatures and the
    run's paths. Each hint names the concrete nfclaw flag (and links docs/known-issues.md)."""
    low = stderr.lower()
    hints: list[str] = []

    if ("network is unreachable" in low or "unknownhostexception" in low
            or "no route to host" in low or "raw.githubusercontent.com" in low
            or "nfcore_custom.config" in low):
        hints.append(
            "the JVM/host could not reach the network (e.g. GitHub for remote configs). On an "
            "IPv6-only host, retry with --nxf-env NXF_JVM_ARGS=-Djava.net.preferIPv6Addresses=true, "
            "or --nxf-env NXF_OFFLINE=true to skip remote config fetches.")

    if ("unexpected input" in low or "unexpected token" in low
            or "invalid include source" in low):
        hints.append(
            "a Nextflow config-parser error — often a newer Nextflow rejecting an older release's "
            "config. Pin the engine the release targets with --nxf-ver X.Y.Z (see "
            "docs/compatibility.md); a config file missing at this release is an upstream bug "
            "(see docs/known-issues.md).")

    if "busco-data.ezlab.org" in low or "file_versions.tsv" in low:
        hints.append(
            "a tool tried to download a database at run time without network. Skip it (e.g. "
            "--skip-busco true) or pre-provide the database.")

    if "samtools_faidx ([])" in low:
        hints.append(
            "SAMTOOLS_FAIDX got an empty input — bamtofastq routes a dummy channel here when no "
            "reference is given. Provide --fasta/--genome (upstream bug, see docs/known-issues.md).")

    if "invalid escape sequence" in low and "unicycler" in low:
        hints.append(
            "the Unicycler container is not Python-3.12-compatible. Use another assembler: "
            "--assembler megahit.")

    spaced = [str(p) for p in paths if " " in str(p)]
    if spaced:
        hints.append(
            "a path contains spaces (" + "; ".join(spaced) + ") — many bioinformatics tools and "
            "Nextflow's work directory mishandle spaces. Use a space-free --outdir, or "
            "--nxf-env NXF_WORK=/a/space-free/dir (see docs/known-issues.md).")

    return hints
