"""The lab's instrument bench — what the team can actually reach today.

Registering an instrument here makes it available to the Principal Investigator
when commissioning studies, and puts its live/offline status on the dashboard so
the board can see what the lab currently has hands on.
"""

from __future__ import annotations

from typing import Any

from .base import REGISTRY, InstrumentResult
from . import claude_science


class GeoRepository:
    """NCBI GEO — public gene-expression and methylation datasets."""

    key = "geo"
    label = "NCBI GEO (public datasets)"

    def available(self) -> bool:
        from ..datasets import geo
        return geo.available()

    def describe(self) -> str:
        return "Search and summarise public GEO series. Free; rate-limited without a key."

    def run(self, query: str, **kwargs: Any) -> InstrumentResult:
        from ..datasets import geo
        series = geo.find_series(query, retmax=kwargs.get("retmax", 5))
        if not series:
            return InstrumentResult(instrument=self.key, query=query, ok=False,
                                    error="no results or GEO unreachable")
        return InstrumentResult(
            instrument=self.key, query=query, ok=True,
            summary=f"{len(series)} public series matched",
            accessions=[s.accession for s in series if s.accession],
            citations=[p for s in series for p in s.pubmed_ids][:10],
            raw={"series": [s.as_dict() for s in series]},
        )


class LiteratureIndex:
    """Public literature via NCBI E-utilities (PubMed)."""

    key = "literature"
    label = "PubMed (public literature)"

    def available(self) -> bool:
        from ..datasets import geo
        return geo.available()

    def describe(self) -> str:
        return "Sweep the public literature for open, testable questions."

    def run(self, query: str, **kwargs: Any) -> InstrumentResult:
        # Uses the same public E-utilities host, PubMed database.
        import requests
        from .. import config
        try:
            r = requests.get(
                f"{config.NCBI_EUTILS}/esearch.fcgi",
                params={"db": "pubmed", "term": query, "retmax": kwargs.get("retmax", 10),
                        "retmode": "json", "tool": config.NCBI_TOOL},
                timeout=20,
            )
            r.raise_for_status()
            ids = r.json().get("esearchresult", {}).get("idlist", [])
        except Exception as exc:
            return InstrumentResult(instrument=self.key, query=query, ok=False,
                                    error=str(exc)[:200])
        return InstrumentResult(
            instrument=self.key, query=query, ok=bool(ids),
            summary=f"{len(ids)} papers matched", citations=ids,
        )


def install() -> None:
    """Register every instrument the lab knows about."""
    REGISTRY.register(GeoRepository())
    REGISTRY.register(LiteratureIndex())
    REGISTRY.register(claude_science.INSTRUMENT)


def bench_status() -> list[dict[str, Any]]:
    """Dashboard-shaped view of the bench."""
    if not REGISTRY.all():
        install()
    out = []
    for row in REGISTRY.bench_report():
        out.append({
            "name": row["label"],
            "desc": row["describe"],
            "status": "CONNECTED" if row["available"] else "NOT CONNECTED",
            "dot": "green" if row["available"] else "amber",
        })
    return out
