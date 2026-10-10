"""Recorded runtime corrections for the fingerprinted fastqrepair 1.1.1 release.

The pinned repository stays unchanged. Generated task recipes use this standalone
splitter, repair a missing shell continuation, and preserve distinct publications.
The complete helper source is embedded into the recorded config, so replay does
not depend on the installed nfclaw version or the original helper path.
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import os
import re
import shlex
import sys
from contextlib import ExitStack
from pathlib import Path

SUPPORTED_COMMIT = "70a38209407b9367a9ff7ab8b26d84cb1983ea18"


def _source() -> bytes:
    return globals().get("_NFCLAW_COMPAT_SOURCE") or Path(__file__).read_bytes()


def recipe_digest() -> str:
    return hashlib.sha256(_source()).hexdigest()


def _command() -> str:
    encoded = base64.b64encode(_source()).decode("ascii")
    bootstrap = f"import base64; _NFCLAW_COMPAT_SOURCE=base64.b64decode('{encoded}'); exec(_NFCLAW_COMPAT_SOURCE)"
    return shlex.join(["python3", "-c", bootstrap])


def _open_source(path: Path):
    return gzip.open(path, "rb") if path.suffix == ".gz" else path.open("rb")


def _scan(path: Path) -> tuple[int, bool, str]:
    count, framed = 0, True
    digest = hashlib.sha256()
    with _open_source(path) as handle:
        while header := handle.readline():
            sequence, plus, quality = handle.readline(), handle.readline(), handle.readline()
            for line in (header, sequence, plus, quality):
                digest.update(line)
            if (not header.startswith(b"@") or not plus.startswith(b"+") or not sequence
                    or not quality or len(sequence.rstrip(b"\r\n")) != len(quality.rstrip(b"\r\n"))):
                framed = False
                for block in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(block)
                break
            count += 1
    return count, framed, digest.hexdigest()


def scatter(path: Path, splits: int, prefix: str, folder: Path, *,
            extension: str = "fastq.gz", suffix: str = "") -> list[Path]:
    if splits < 1 or Path(prefix).name != prefix or not prefix or "/" in suffix:
        raise ValueError("invalid chunk count or filename prefix/suffix")
    count, framed, original_digest = _scan(path)
    n = min(splits, count) if framed and count else 1
    if not framed:
        print("nfclaw: ambiguous FASTQ framing; preserve the complete input in one chunk before wiping",
              file=sys.stderr)
    folder.mkdir(parents=True, exist_ok=False)
    width = max(3, len(str(n - 1)))
    files = []
    digest = hashlib.sha256()
    with _open_source(path) as source:
        for index in range(n):
            target = folder / f"{prefix}_{index:0{width}d}{'_' + suffix if suffix else ''}.{extension}"
            files.append(target)
            with ExitStack() as stack:
                raw = stack.enter_context(target.open("xb"))
                output = (stack.enter_context(gzip.GzipFile(filename="", mode="wb", fileobj=raw,
                                                           compresslevel=6, mtime=0))
                          if extension.endswith(".gz") else raw)
                if not framed or not count:
                    for block in iter(lambda: source.read(1024 * 1024), b""):
                        output.write(block)
                        digest.update(block)
                else:
                    size = count // n + (index < count % n)
                    for _ in range(size * 4):
                        line = source.readline()
                        if not line:
                            raise ValueError("FASTQ input changed after framing check")
                        output.write(line)
                        digest.update(line)
        if source.read(1) or digest.hexdigest() != original_digest:
            raise ValueError("FASTQ input changed between framing and splitting")
    return files


def patch_task(kind: str, path: Path) -> None:
    source = path.read_text()
    if kind == "scatter":
        needle = "wipertools \\\n    fastqscatter \\\n"
        version = "wipertools fastqscatter: $(wipertools fastqscatter --version)"
        if source.count(needle) != 1 or source.count(version) != 1:
            raise ValueError("unrecognized pinned scatter task; runtime correction refused")
        command = _command()
        corrected = source.replace(needle, command + " scatter \\\n", 1).replace(
            version, f"nfclaw_record_scatter: $({command} version)", 1)
    elif kind == "repair":
        corrected, matches = re.subn(r"(?m)^(\s*threads=\d+)\n", r"\1 \\\n", source)
        if matches != 1 or "qin=" not in source:
            raise ValueError("unrecognized pinned repair task; runtime correction refused")
    else:
        raise ValueError("unknown task correction")
    temp = path.with_name(path.name + ".nfclaw.tmp")
    try:
        temp.write_text(corrected)
        temp.chmod(path.stat().st_mode & 0o777)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def write_config(target: Path) -> Path:
    command = _command()
    scatter_hook = json.dumps(command + " patch scatter .command.sh")
    repair_hook = json.dumps(command + " patch repair .command.sh")
    salt = recipe_digest()[:16]
    config = """// nfclaw runtime correction for fastqrepair 1.1.1; pinned source is unchanged.
process {
    withName: 'WIPERTOOLS_FASTQSCATTER' {
        beforeScript = SCATTER_HOOK
        ext.prefix = { "${meta.id}__nfclaw_RECIPE" }
    }
    withName: 'WIPERTOOLS_FASTQGATHER' {
        ext.prefix = { "${meta.id}_gather__nfclaw_RECIPE" }
    }
    withName: 'BBMAP_REPAIR' {
        beforeScript = REPAIR_HOOK
        ext.prefix = { "${meta.id}__nfclaw_RECIPE" }
        publishDir = [path: { "${params.outdir}/repaired" }, mode: "${-> params.publish_dir_mode}",
            overwrite: true, saveAs: { filename ->
                if (filename == 'versions.yml') return null
                if (filename.endsWith('.repair.sh.log')) return "${meta.id}.repair.sh.log"
                if (filename.endsWith('_1_repaired.fastq.gz')) return "${meta.id}_1.fastq.gz"
                if (filename.endsWith('_2_repaired.fastq.gz')) return "${meta.id}_2.fastq.gz"
                if (filename.endsWith('_singleton.fastq.gz')) return "${meta.id}_singleton.fastq.gz"
                throw new IllegalStateException("Unexpected BBMAP_REPAIR publication: ${filename}")
            }]
    }
    withName: 'WIPERTOOLS_REPORTGATHER' {
        publishDir = [path: { "${params.outdir}/repaired" }, mode: "${-> params.publish_dir_mode}",
            overwrite: true, saveAs: { filename ->
                if (filename == 'versions.yml') return null
                return meta.single_end ? "${meta.sample_id}.report" : "reports/${meta.sample_id}/${meta.id}.report"
            }]
    }
    withName: 'FASTQC' {
        publishDir = [path: { "${params.outdir}/QC/fastqc" }, mode: "${-> params.publish_dir_mode}",
            overwrite: true, saveAs: { filename -> filename == 'versions.yml' ? null : filename }]
    }
    withName: 'MULTIQC' {
        publishDir = [path: { "${params.outdir}/QC/multiqc" }, mode: "${-> params.publish_dir_mode}",
            overwrite: true, saveAs: { filename -> filename == 'versions.yml' ? null : filename }]
    }
}
""".replace("RECIPE", salt).replace("SCATTER_HOOK", scatter_hook).replace("REPAIR_HOOK", repair_hook)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(config)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("version")
    patch = sub.add_parser("patch")
    patch.add_argument("kind", choices=("scatter", "repair"))
    patch.add_argument("script", type=Path)
    split = sub.add_parser("scatter")
    split.add_argument("-f", "--fastq", type=Path, required=True)
    split.add_argument("-n", "--num_splits", type=int, required=True)
    split.add_argument("-p", "--prefix", required=True)
    split.add_argument("-s", "--suffix", default="", nargs="?", const="")
    split.add_argument("-e", "--ext", choices=("fastq", "fq", "fastq.gz", "fq.gz"), default="fastq.gz")
    split.add_argument("-o", "--out_folder", type=Path, default=Path("chunks"))
    split.add_argument("-O", "--os", choices=("unix", "cross_platform"), default="unix")
    args = parser.parse_args()
    if args.command == "version":
        print("nfclaw-record-scatter-sha256:" + recipe_digest())
    elif args.command == "patch":
        patch_task(args.kind, args.script)
    else:
        scatter(args.fastq, args.num_splits, args.prefix, args.out_folder,
                extension=args.ext, suffix=args.suffix)


if __name__ == "__main__":
    main()
