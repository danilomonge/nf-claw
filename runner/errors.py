from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    SUBMODULE_INCOMPLETE = "submodule_incomplete"
    PIPELINE_NOT_FOUND = "pipeline_not_found"
    ENVIRONMENT = "environment"
    SAMPLESHEET_INVALID = "samplesheet_invalid"
    EXECUTION_FAILED = "execution_failed"


@dataclass
class NfclawError(Exception):
    code: ErrorCode
    message: str
    fix: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        base = f"[{self.code.value}] {self.message}"
        return f"{base}\n  fix: {self.fix}" if self.fix else base
