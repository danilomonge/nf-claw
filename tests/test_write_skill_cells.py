from pathlib import Path

from runner.schema import Param, ParamSchema
from runner.submodule import SubmoduleStatus
from librarian import write_skill


def test_cell_collapses_whitespace_and_escapes_pipes():
    assert write_skill._cell("a\n\nb") == "a b"
    assert write_skill._cell("x  |  y") == "x \\| y"
    assert write_skill._cell("p\tq\nr") == "p q r"


def _ps(desc):
    return ParamSchema(title="t", description="d", params={
        "weird": Param(name="weird", type="string", default=None, enum=None,
                       description=desc, fmt=None, required=False, group="g"),
    })


def _st():
    return SubmoduleStatus("t", Path("/x"), True, True, "1.0.0", "abc", ())


def test_reference_row_is_single_line_and_pipe_safe():
    desc = "First sentence.\n\nSecond with a | pipe."
    out = write_skill._render_reference("t", _st(), _ps(desc), None)
    rows = [ln for ln in out.splitlines() if ln.startswith("| `--weird`")]
    assert len(rows) == 1
    assert "First sentence. Second with a \\| pipe." in rows[0]
