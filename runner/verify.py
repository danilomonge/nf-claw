from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from runner.errors import ErrorCode, NfclawError


@dataclass(frozen=True)
class Comparison:
    """How a replay's outputs compare to the run they reproduce."""

    identical: list[str] = field(default_factory=list)   # same path, same bytes
    changed: list[str] = field(default_factory=list)     # same path, different bytes
    missing: list[str] = field(default_factory=list)     # in the original, absent from the replay
    extra: list[str] = field(default_factory=list)       # in the replay, absent from the original

    @property
    def structurally_equal(self) -> bool:
        """The replay produced exactly the same set of files — the property that is achievable.

        Byte-equality is not: nf-core outputs embed timestamps (HTML reports, gzip headers, zip
        entries), so re-running the same pipeline on the same inputs legitimately yields different
        bytes for the same file. A *missing* or *extra* file is a different matter — that means the
        replay did not do the same work."""
        return not self.missing and not self.extra


def _read(bundle: Path) -> dict[str, str]:
    """`provenance/outputs.sha256` as {relative path: hash}."""
    checksums = bundle / "provenance" / "outputs.sha256"
    if not checksums.is_file():
        raise NfclawError(
            ErrorCode.ENVIRONMENT,
            f"no provenance bundle found in {bundle} (expected provenance/outputs.sha256).",
            fix="Pass an --outdir from a run made with provenance enabled.")
    out: dict[str, str] = {}
    for line in checksums.read_text(encoding="utf-8").splitlines():
        digest, _, path = line.partition("  ")
        if digest and path:
            out[path] = digest
    return out


def compare(original: Path, replay: Path) -> Comparison:
    """Compare a replay's outputs against the run it reproduces, by path.

    Comparing the raw `outputs.sha256` lines instead — the obvious thing to do — is misleading: a
    file whose *content* differs has a different `hash  path` line, so it shows up as both "missing"
    from the replay and "extra" in it, and one changed file is counted twice. Keying on the path
    separates the two questions that matter: did the replay produce the same *files* (structural),
    and did any of them come out different (content).
    """
    before, after = _read(original), _read(replay)
    identical, changed = [], []
    for path, digest in sorted(before.items()):
        if path not in after:
            continue
        (identical if after[path] == digest else changed).append(path)
    return Comparison(
        identical=identical,
        changed=changed,
        missing=sorted(set(before) - set(after)),
        extra=sorted(set(after) - set(before)),
    )


def report(cmp: Comparison) -> str:
    lines = [
        f"identical : {len(cmp.identical)}",
        f"changed   : {len(cmp.changed)}   (same file, different bytes)",
        f"missing   : {len(cmp.missing)}   (in the original, not in the replay)",
        f"extra     : {len(cmp.extra)}   (in the replay, not in the original)",
        "",
    ]
    if cmp.structurally_equal:
        lines.append("The replay produced the same set of files as the original run.")
        if cmp.changed:
            lines.append(
                "Differing bytes are expected: nf-core outputs embed timestamps (the execution "
                "report and timeline, gzip headers, zip entries, MultiQC's HTML), so the same file "
                "re-made from the same inputs is not byte-identical. Inspect the list below if a "
                "specific result matters.")
    else:
        lines.append("The replay did NOT produce the same set of files — it did different work.")
    for label, paths in (("missing", cmp.missing), ("extra", cmp.extra), ("changed", cmp.changed)):
        if paths:
            lines.append("")
            lines.append(f"{label}:")
            lines += [f"  {p}" for p in paths]
    return "\n".join(lines) + "\n"
