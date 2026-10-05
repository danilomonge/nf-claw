from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_agents_md_matches_claude_md():
    # Two entry points to the same agent guide: CLAUDE.md (Claude Code) and AGENTS.md (other agents).
    # AGENTS.md had silently fallen five sections behind (replay, --limit-*, `nfclaw verify`, remote
    # reference defaults, warnings that are not faults), so agents reading it never learned them.
    assert (ROOT / "AGENTS.md").read_text(encoding="utf-8") == \
        (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
