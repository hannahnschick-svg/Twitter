"""The evidence ledger — the institute's memory and audit trail.

Every claim the lab makes lives here with its full provenance: the dataset
accessions it rests on, the exact query that produced it, the population/tissue
scope it holds for, its strength rating, and the checker verdicts against it. A
claim with no provenance is invalid by construction.

The ledger persists to state/ledger.json so cycles accumulate rather than reset.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import date
from pathlib import Path
from typing import Any, Literal

STATE_DIR = Path(__file__).resolve().parent.parent / "state"
LEDGER_PATH = STATE_DIR / "ledger.json"

Status = Literal["candidate", "confirmed", "ruled_out"]
Strength = Literal["strongest", "solid", "promising", "early"]


@dataclass
class Provenance:
    accessions: list[str] = field(default_factory=list)  # e.g. ["GSE40279"]
    query: str = ""                                       # exact search/analysis
    method: str = ""                                      # what was computed
    pubmed_ids: list[str] = field(default_factory=list)


@dataclass
class CheckerVerdict:
    verdict: Literal["reproduced", "needs_revision", "failed"]
    reasoning: str
    checker: str = "Checkers"


@dataclass
class Finding:
    id: str
    title: str
    summary: str
    status: Status
    provenance: Provenance
    scope: str = ""                       # "Holds for: ..."
    strength: Strength | None = None
    team: str = ""                        # which group produced it
    day: int = 0                          # institute-day it was recorded
    verdicts: list[CheckerVerdict] = field(default_factory=list)

    def confirmed(self) -> bool:
        return self.status == "confirmed"

    def traceable(self) -> bool:
        p = self.provenance
        return bool(p.accessions and p.query)


@dataclass
class Ledger:
    day: int = 0
    findings: list[Finding] = field(default_factory=list)

    # --- queries used by the console -------------------------------------
    def confirmed(self) -> list[Finding]:
        return [f for f in self.findings if f.status == "confirmed"]

    def ruled_out(self) -> list[Finding]:
        return [f for f in self.findings if f.status == "ruled_out"]

    def reproduction_rate(self) -> float:
        """Fraction of results that reproduced on first independent re-run."""
        checked = [f for f in self.findings if f.verdicts]
        if not checked:
            return 1.0
        ok = sum(1 for f in checked if f.verdicts[0].verdict == "reproduced")
        return ok / len(checked)

    def traceability_rate(self) -> float:
        if not self.findings:
            return 1.0
        return sum(1 for f in self.findings if f.traceable()) / len(self.findings)

    def strength_distribution(self) -> dict[str, int]:
        dist = {"strongest": 0, "solid": 0, "promising": 0, "early": 0}
        for f in self.confirmed():
            if f.strength in dist:
                dist[f.strength] += 1
        return dist

    def add(self, finding: Finding) -> None:
        self.findings = [f for f in self.findings if f.id != finding.id]
        self.findings.append(finding)

    # --- persistence -----------------------------------------------------
    def save(self, path: Path = LEDGER_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(_to_jsonable(self), indent=2, ensure_ascii=False))

    @classmethod
    def load(cls, path: Path = LEDGER_PATH) -> "Ledger":
        if not path.exists():
            return cls()
        raw = json.loads(path.read_text())
        findings = []
        for f in raw.get("findings", []):
            prov = Provenance(**f.get("provenance", {}))
            verdicts = [CheckerVerdict(**v) for v in f.get("verdicts", [])]
            f = {**f, "provenance": prov, "verdicts": verdicts}
            findings.append(Finding(**f))
        return cls(day=raw.get("day", 0), findings=findings)


def _to_jsonable(obj: Any) -> Any:
    if isinstance(obj, (Ledger, Finding, Provenance, CheckerVerdict)):
        return {k: _to_jsonable(v) for k, v in asdict(obj).items()}
    if isinstance(obj, list):
        return [_to_jsonable(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    return obj


def today_label() -> str:
    return date.today().strftime("%A %d %B %Y")
