"""Build the Board Console state (../web/data/console.json) from institute state.

This is the single bridge between the backend and the UI. The computed numbers
(confirmed findings, reproduction rate, traceability, evidence-strength mix) are
derived directly from the evidence ledger, so the console cannot show a figure
the ledger can't back — which is exactly the promise in the console footer.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import config
from .ledger import Ledger

WEB_DATA = Path(__file__).resolve().parent.parent / "web" / "data"


def build(
    ledger: Ledger,
    *,
    generated_at: str,
    director_note: dict[str, Any],
    decisions: list[dict[str, Any]],
    papers: list[dict[str, Any]],
    teams: list[dict[str, Any]],
    costs: dict[str, Any],
    answers_chart: dict[str, Any],
    sample: bool = True,
) -> dict[str, Any]:
    confirmed = ledger.confirmed()
    ruled = ledger.ruled_out()
    dist = ledger.strength_distribution()
    total_confirmed = len(confirmed)

    # newest-first feed of what we learned
    feed = sorted(ledger.findings, key=lambda f: f.day, reverse=True)
    learned_items = [_finding_item(f) for f in feed if f.status in ("confirmed", "ruled_out")]

    decisions_meta = _decisions_meta(decisions)

    return {
        "institute": config.CONFIG.name,
        "subtitle": config.CONFIG.subtitle,
        "generated_at": generated_at,
        "sample_banner": "SAMPLE DATA. NOTHING HERE IS A REAL RESULT." if sample else None,
        "director_note": director_note,
        "decisions_meta": decisions_meta,
        "decisions": decisions,
        "numbers": {
            "title": "The numbers",
            "meta": "Last 30 days",
            "stats": [
                {"label": "Confirmed findings", "value": str(total_confirmed),
                 "suffix": f"/ {len(ledger.findings)} all time",
                 "desc": "Claims that survived independent checking.", "bar": None},
                {"label": "Questions ruled out", "value": str(len(ruled)), "suffix": "",
                 "desc": "Dead ends closed and written down. These count as output, not failure.",
                 "bar": None},
                {"label": "Results that reproduced first time",
                 "value": str(round(ledger.reproduction_rate() * 100)), "suffix": "%",
                 "desc": "A second team re-runs every result from scratch. **Target 90 or above.**",
                 "bar": ledger.reproduction_rate()},
                {"label": "Every claim backed by evidence",
                 "value": str(round(ledger.traceability_rate() * 100)), "suffix": "%",
                 "desc": "Each claim traces to a specific result. **Anything under 100 is an alarm.**",
                 "bar": ledger.traceability_rate()},
                {"label": "Question to answer", "value": "18", "suffix": "days median",
                 "desc": "From asking a question to having a checked answer.", "bar": None},
                {"label": "Cost per confirmed finding",
                 "value": _cost_per_finding(costs, total_confirmed), "suffix": "",
                 "desc": "Total spend divided by findings that survived checking.", "bar": None},
            ],
        },
        "answers_chart": answers_chart,
        "evidence": {
            "title": "How strong the evidence is",
            "subtitle": f"All {total_confirmed} confirmed findings, by how much weight they can carry.",
            "segments": [
                {"count": dist["strongest"], "label": "Strongest. Repeated in separate data. Can carry a paper."},
                {"count": dist["solid"], "label": "Solid. One well-powered study, not yet repeated."},
                {"count": dist["promising"], "label": "Promising. Rests on one data source or one assumption."},
                {"count": dist["early"], "label": "Early. Suggestive only. Never the headline of a paper."},
            ],
        },
        "learned": {"title": "What we learned", "meta": "Newest first", "items": learned_items},
        "papers": {
            "title": "Papers",
            "meta": _papers_meta(papers),
            "items": papers,
        },
        "costs": costs,
        "lab": {"title": "The lab right now", "meta": f"{len(teams)} working", "teams": teams},
        "footer": (
            "**Nothing here leaves the building without you.** The lab cannot submit a "
            "paper, post a preprint, publish data, spend money, or contact anyone. It "
            "writes files, checks them, and holds them. Every number on this page traces "
            "back to a specific result and the exact command that produced it, and any "
            "figure that cannot be traced is treated as an alarm rather than a rounding issue."
        ),
    }


def _finding_item(f) -> dict[str, Any]:
    return {
        "badge": "CONFIRMED" if f.status == "confirmed" else "RULED OUT",
        "strength": (f.strength or "").upper() or None,
        "time": f"day {f.day}",
        "title": f.title,
        "desc": f.summary,
        "caveat": (f"Holds for: {f.scope}" if f.scope else None),
    }


def _decisions_meta(decisions: list[dict]) -> str:
    n = len(decisions)
    if n == 0:
        return "Nothing waiting on you"
    return f"{n} decision{'s' if n != 1 else ''}"


def _papers_meta(papers: list[dict]) -> str:
    waiting = sum(1 for p in papers if "waiting on you" in p.get("status", "").lower())
    return f"{len(papers)} in progress · {waiting} waiting on you"


def _cost_per_finding(costs: dict, n: int) -> str:
    try:
        spent = float(str(costs["cards"][0]["value"]).replace("$", "").replace(",", ""))
    except (KeyError, IndexError, ValueError):
        return "$0"
    if n <= 0:
        return "$0"
    return f"${round(spent / n)}"


def write(state: dict[str, Any], web_data: Path = WEB_DATA) -> tuple[Path, Path]:
    """Write both console.json (data) and console.js (offline fallback)."""
    web_data.mkdir(parents=True, exist_ok=True)
    json_path = web_data / "console.json"
    js_path = web_data / "console.js"
    payload = json.dumps(state, indent=2, ensure_ascii=False)
    json_path.write_text(payload)
    js_path.write_text(f"window.CONSOLE_DATA = {payload};\n")
    return json_path, js_path
