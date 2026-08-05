"""Studies — a unit of commissioned work, tracked from question to verdict.

A Study is what the board actually watches: the PI commissions a question, an
instrument (Claude Science, GEO, the analysis sandbox) supplies evidence, a
checker rules on it, and it lands in the ledger. Every stage change is visible
on the dashboard, so work in flight is as visible as work finished.

Lifecycle:
    commissioned -> running -> checking -> confirmed | ruled_out | failed
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

STATE_DIR = Path(__file__).resolve().parent.parent / "state"
STUDIES_PATH = STATE_DIR / "studies.json"

Stage = Literal["commissioned", "running", "checking", "confirmed", "ruled_out", "failed"]

STAGE_ORDER: list[Stage] = ["commissioned", "running", "checking", "confirmed"]

# How each stage reads on the board.
STAGE_LABEL: dict[str, str] = {
    "commissioned": "Commissioned",
    "running": "Running",
    "checking": "Independent check",
    "confirmed": "Confirmed",
    "ruled_out": "Ruled out",
    "failed": "Stopped",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Study:
    id: str
    question: str
    group: str                      # which research group owns it
    instrument: str = ""            # which instrument is supplying evidence
    stage: Stage = "commissioned"
    commissioned_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    note: str = ""                  # one-line plain-language status
    accessions: list[str] = field(default_factory=list)
    finding_id: str | None = None   # set once it reaches the ledger
    cost_usd: float = 0.0
    history: list[dict[str, str]] = field(default_factory=list)

    def advance(self, stage: Stage, note: str = "") -> None:
        self.history.append({"stage": self.stage, "at": self.updated_at})
        self.stage = stage
        self.updated_at = _now()
        if note:
            self.note = note

    def open(self) -> bool:
        return self.stage in ("commissioned", "running", "checking")

    def as_card(self) -> dict[str, Any]:
        """Shape the dashboard renders for work in flight."""
        terminal = {"confirmed": "done", "ruled_out": "done", "failed": "stopped"}
        stages = []
        for s in STAGE_ORDER:
            if self.stage in terminal and s == "confirmed":
                name = STAGE_LABEL[self.stage]
                state = "done" if self.stage != "failed" else "pending"
            else:
                name = STAGE_LABEL[s]
                state = ("done" if STAGE_ORDER.index(s) < STAGE_ORDER.index(
                            self.stage if self.stage in STAGE_ORDER else "confirmed")
                         else "current" if s == self.stage else "pending")
            stages.append({"name": name, "state": state})
        return {
            "status": STAGE_LABEL.get(self.stage, self.stage).upper(),
            "meta": self.instrument or "",
            "title": self.question,
            "stages": stages,
            "desc": self.note or "",
        }


@dataclass
class StudyBoard:
    studies: list[Study] = field(default_factory=list)

    def add(self, study: Study) -> Study:
        self.studies = [s for s in self.studies if s.id != study.id]
        self.studies.append(study)
        return study

    def get(self, sid: str) -> Study | None:
        return next((s for s in self.studies if s.id == sid), None)

    def open_studies(self) -> list[Study]:
        return [s for s in self.studies if s.open()]

    def next_id(self) -> str:
        return f"S{len(self.studies) + 1:04d}"

    # --- persistence ---------------------------------------------------
    def save(self, path: Path = STUDIES_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(
            {"studies": [asdict(s) for s in self.studies]}, indent=2, ensure_ascii=False))

    @classmethod
    def load(cls, path: Path = STUDIES_PATH) -> "StudyBoard":
        if not path.exists():
            return cls()
        raw = json.loads(path.read_text())
        return cls(studies=[Study(**s) for s in raw.get("studies", [])])
