#!/usr/bin/env python3
"""Run one Chronogene Institute research cycle and refresh the Board Console.

    python run_cycle.py            # one cycle (live if API key + network available)
    python run_cycle.py --offline  # force offline mode (no API calls, no network)
    python run_cycle.py --real     # drop the "SAMPLE DATA" banner

The cycle updates state/ledger.json and rewrites web/data/console.json (+ .js),
which the UI at web/index.html renders. Nothing is ever published, submitted,
or spent — outward-facing actions are queued as board decisions in the console.
"""

from __future__ import annotations

import argparse
import sys

from institute import agents, config
from institute.datasets import geo
from institute.orchestrator import run_cycle


def main() -> int:
    ap = argparse.ArgumentParser(description="Run a Chronogene Institute research cycle.")
    ap.add_argument("--offline", action="store_true", help="Force offline mode (no live research pass).")
    ap.add_argument("--real", action="store_true", help="Drop the SAMPLE DATA banner.")
    args = ap.parse_args()

    live = not args.offline
    mode = "LIVE" if (live and agents.online() and geo.available()) else "OFFLINE"
    print(f"Chronogene Institute — running one cycle [{mode}]")
    print(f"  models: PI={config.PI_MODEL}  researcher={config.RESEARCHER_MODEL}  "
          f"checker={config.CHECKER_MODEL}  literature={config.LITERATURE_MODEL}")
    if mode == "OFFLINE":
        print("  (no API key/profile or no network — using the demonstration seed)")

    state = run_cycle(sample=not args.real, live=live)

    stats = {s["label"]: s["value"] for s in state["numbers"]["stats"]}
    print("\nBoard Console refreshed → web/data/console.json")
    print(f"  Confirmed findings:  {stats.get('Confirmed findings')}")
    print(f"  Questions ruled out: {stats.get('Questions ruled out')}")
    print(f"  Reproduced first try:{stats.get('Results that reproduced first time')}%"
          if False else f"  Reproduced first try: {stats.get('Results that reproduced first time')}%")
    print(f"  Decisions for the board: {len(state['decisions'])}")
    print("\nOpen web/index.html to view the console.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
