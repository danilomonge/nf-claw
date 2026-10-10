"""Known-input read conservation and mate orientation for pinned fastqrepair 1.1.1.

The official bundled test filters its paired sample before BBMAP_REPAIR. This
independent fixture contains reordered mates and one orphan on each side.
It checks exact sequence/quality retention, pairing and singleton inventory;
it does not establish repair accuracy for arbitrary damaged sequencing data.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
from pathlib import Path

# Distinct sequences and qualities expose mate swaps even if a tool rewrites headers.
READS = {
    "pairA/1": ("ACGT" * 19, "I" * 76),
    "pairA/2": ("TGCA" * 19, "H" * 76),
    "pairB/1": ("GATTACA" * 11, "G" * 77),
    "pairB/2": ("CCTAGGT" * 11, "F" * 77),
    "orphanLeft/1": ("AACCGGTT" * 9, "E" * 72),
    "orphanRight/2": ("TTGGCCAA" * 9, "D" * 72),
}
EXPECTED = {
    "paired_probe_1_repaired.fastq.gz": {"pairA/1", "pairB/1"},
    "paired_probe_2_repaired.fastq.gz": {"pairA/2", "pairB/2"},
    "paired_probe_singleton.fastq.gz": {"orphanLeft/1", "orphanRight/2"},
}


def write_fixture(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=False)
    for name, ids in (("left", ("pairA/1", "orphanLeft/1", "pairB/1")),
                      ("right", ("pairB/2", "pairA/2", "orphanRight/2"))):
        text = "".join(f"@{key}\n{READS[key][0]}\n+\n{READS[key][1]}\n" for key in ids)
        (directory / f"{name}.fastq").write_text(text, encoding="ascii")
    with (directory / "samples.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sample", "fastq_1", "fastq_2"])
        writer.writerow(["paired_probe", str((directory / "left.fastq").resolve()),
                         str((directory / "right.fastq").resolve())])
    # Deliberately perturb task arrival order: completion order must not determine mate identity.
    (directory / "arrival.config").write_text(
        "process {\n    withName: '.*:WIPERTOOLS_FASTQGATHER' {\n"
        "        beforeScript = { meta.id == 'left' ? 'sleep 3' : '' }\n    }\n}\n")


def read_fastq(path: Path) -> dict[str, tuple[str, str]]:
    records = {}
    with gzip.open(path, "rt", encoding="ascii") as handle:
        while header := handle.readline():
            sequence = handle.readline().rstrip("\r\n")
            plus = handle.readline()
            quality = handle.readline().rstrip("\r\n")
            if not header.startswith("@") or not plus.startswith("+") or not sequence:
                raise ValueError(f"invalid FASTQ record in {path}")
            if len(sequence) != len(quality) or any(not 33 <= ord(c) <= 126 for c in quality):
                raise ValueError(f"invalid sequence/quality in {path}")
            key = header[1:].split()[0]
            if key in records:
                raise ValueError(f"duplicate read {key!r} in {path}")
            records[key] = (sequence, quality)
    return records


def check_run(run: Path) -> dict[str, int]:
    manifest = json.loads((run / "provenance/run_manifest.json").read_text())
    expected_identity = {"pipeline": "fastqrepair", "version": "1.1.1",
                         "nextflow": "nextflow version 25.10.4", "outcome": "success"}
    if any(manifest.get(key) != value for key, value in expected_identity.items()):
        raise ValueError("unvalidated pipeline, engine or run outcome")
    outputs = run / "repaired"
    inventory = {path.name for path in outputs.glob("*.fastq.gz")}
    if inventory != set(EXPECTED):
        raise ValueError(f"unexpected repaired inventory: {sorted(inventory)}")
    counts = {}
    for filename, ids in EXPECTED.items():
        records = read_fastq(outputs / filename)
        expected = {key: READS[key] for key in ids}
        if records != expected:
            raise ValueError(f"read identities, mate orientation, sequences or qualities changed: {filename}")
        counts[filename] = len(records)
    traces = list((run / "pipeline_info").glob("execution_trace*.txt"))
    if len(traces) != 1:
        raise ValueError("expected one fresh execution trace")
    with traces[0].open() as handle:
        tasks = list(csv.DictReader(handle, delimiter="\t"))
    repair = [row for row in tasks if ":BBMAP_REPAIR " in row.get("name", "")]
    if len(repair) != 1 or repair[0].get("status") != "COMPLETED" or repair[0].get("exit") != "0":
        raise ValueError("BBMAP_REPAIR must execute successfully; stubs or skipped pairing are insufficient")
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("fixture").add_argument("directory", type=Path)
    sub.add_parser("check").add_argument("run", type=Path)
    args = parser.parse_args()
    if args.command == "fixture":
        write_fixture(args.directory)
    else:
        print(check_run(args.run))
        print("Two pairs and both orphans retain their exact sequences, qualities and mate identity.")


if __name__ == "__main__":
    main()
