"""The instrument contract.

Every instrument answers three questions:
  available()  — can I be used right now (credentials, network, quota)?
  describe()   — what am I, for the PI's benefit when choosing a tool?
  run(query)   — do the work, and hand back evidence WITH its provenance.

An instrument may never write to the ledger directly. It returns evidence; the
lab decides what that evidence means, and only a checker can promote it to a
confirmed finding. That separation is what keeps an external service (Claude
Science included) from being able to assert a finding into the record.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class InstrumentResult:
    """Evidence returned by an instrument, with everything needed to trace it."""

    instrument: str                       # which instrument produced this
    query: str                            # the exact request that was made
    ok: bool                              # did it actually run
    summary: str = ""                     # short human-readable result
    accessions: list[str] = field(default_factory=list)   # datasets touched
    citations: list[str] = field(default_factory=list)    # DOIs / PMIDs
    artifacts: list[str] = field(default_factory=list)    # files produced
    raw: dict[str, Any] = field(default_factory=dict)     # full payload
    error: str = ""                       # why it failed, if it did
    cost_usd: float = 0.0                 # what this call cost the budget

    def as_provenance(self) -> dict[str, Any]:
        return {
            "instrument": self.instrument,
            "query": self.query,
            "accessions": self.accessions,
            "citations": self.citations,
            "artifacts": self.artifacts,
        }


class Instrument(Protocol):
    """Structural contract every instrument satisfies."""

    key: str
    label: str

    def available(self) -> bool: ...
    def describe(self) -> str: ...
    def run(self, query: str, **kwargs: Any) -> InstrumentResult: ...


class Registry:
    """The lab's instrument bench. The PI picks from what is available."""

    def __init__(self) -> None:
        self._items: dict[str, Instrument] = {}

    def register(self, instrument: Instrument) -> Instrument:
        self._items[instrument.key] = instrument
        return instrument

    def get(self, key: str) -> Instrument | None:
        return self._items.get(key)

    def all(self) -> list[Instrument]:
        return list(self._items.values())

    def available(self) -> list[Instrument]:
        return [i for i in self._items.values() if i.available()]

    def bench_report(self) -> list[dict[str, Any]]:
        """What the board sees on the dashboard: which instruments are live."""
        return [
            {
                "key": i.key,
                "label": i.label,
                "available": i.available(),
                "describe": i.describe(),
            }
            for i in self._items.values()
        ]


REGISTRY = Registry()
