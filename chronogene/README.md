# Chronogene Institute

A research institute for **epigenetic ageing**, run as a multi-agent computational
research team with a board-facing oversight console.

- A **Principal Investigator** directs a team of researcher agents (grad students
  and postdocs), independent checkers, and a literature scanner.
- The team does **computational research only**, on **public datasets and
  databases** (NCBI GEO and the public literature) — no wet lab.
- Every claim traces back to a dataset accession and the exact query that produced
  it. A finding is "confirmed" only after an independent checker reproduces it from
  scratch. Checkers can stop any result and the PI cannot overrule them.
- **Nothing leaves the building without a human.** The lab writes files, checks
  them, and holds them. Submitting a paper, posting a preprint, publishing data, or
  spending money are **board decisions**, surfaced to a human in the console — never
  taken by the agents.

The intended output is publishable, institutional-grade computational work: confirmed
findings with full provenance, and rigorously written-up negative results.

```
chronogene/
├── web/                     # Board Console UI (static, no build step)
│   ├── index.html
│   ├── styles.css
│   ├── app.js               # renders entirely from the console state
│   └── data/
│       ├── console.json     # the console state (the backend↔frontend contract)
│       └── console.js        # same state as a window global (file:// fallback)
├── institute/               # the multi-agent research framework
│   ├── config.py            # models per role, guardrails, budget, team roster
│   ├── agents.py            # PI / researcher / checker / literature (Anthropic SDK)
│   ├── datasets/
│   │   ├── geo.py           # NCBI GEO connector (public E-utilities)
│   │   └── registry.py      # public epigenetic-ageing clocks + search terms
│   ├── ledger.py            # evidence ledger with full provenance + audit trail
│   ├── console_state.py     # builds console.json from ledger + cycle state
│   └── orchestrator.py      # the research loop
├── run_cycle.py             # entry point: run one cycle, refresh the console
└── requirements.txt
```

## The console

Open `web/index.html` in a browser. It renders the Board Console: the PI's morning
note, the decisions waiting on the board, the numbers (all computed from the evidence
ledger), the findings feed, the paper pipeline, spend, and live team status.

The UI is a static page driven entirely by `web/data/console.json`. It loads that
state from `console.js` (so it works when opened directly from disk) and falls back
to fetching `console.json` when served over HTTP. To serve it:

```bash
cd chronogene/web && python3 -m http.server 8000   # then open http://localhost:8000
```

The committed `console.json` is a **sample** (banner: *"SAMPLE DATA. NOTHING HERE IS A
REAL RESULT."*) that mirrors the reference design. Running a research cycle overwrites
it with live, self-consistent state computed from the ledger.

## The research team (backend)

```bash
pip install -r requirements.txt

python run_cycle.py            # one cycle; live if credentials + network are available
python run_cycle.py --offline  # force offline mode (no API calls, no network)
python run_cycle.py --real     # drop the SAMPLE DATA banner once results are real
```

A cycle:

1. **Literature scan** — sweeps public datasets (NCBI GEO) for open, testable questions.
2. **PI direction** — chooses what the lab spends time on.
3. **Researchers** — work up candidate claims from real dataset accessions, with scope
   and a strength rating.
4. **Checkers** — independently reproduce each claim from scratch and return a verdict
   (`reproduced` / `needs_revision` / `failed`).
5. **Ledger** — records confirmed findings and ruled-out questions with full provenance.
6. **PI** — writes the plain-language daily note and frames the board decisions.
7. **Console** — `web/data/console.json` (+ `.js`) is regenerated.

**Numbers are computed from the ledger, never generated.** The console cannot show a
figure the ledger can't back — which is the promise in the console's own footer.

### Credentials and modes

The agent layer uses the Anthropic Messages API. Provide credentials via
`ANTHROPIC_API_KEY` or an `ant auth login` profile. If neither is present, or there is
no network, the cycle runs **offline** on a demonstration seed so the console is always
renderable — nothing silently breaks.

Models are tiered by role (overridable via environment variables in `config.py`),
because the institute tracks cost-per-confirmed-finding: the most capable model does
direction-setting and independent checking, cheaper models do triage.

| Role        | Default model      | Env override                    |
|-------------|--------------------|---------------------------------|
| PI          | `claude-opus-5`    | `CHRONOGENE_PI_MODEL`           |
| Researcher  | `claude-sonnet-5`  | `CHRONOGENE_RESEARCHER_MODEL`   |
| Checker     | `claude-opus-5`    | `CHRONOGENE_CHECKER_MODEL`      |
| Literature  | `claude-haiku-4-5` | `CHRONOGENE_LITERATURE_MODEL`   |

An optional `NCBI_API_KEY` raises the GEO rate limit from 3 to 10 requests/sec — this is
exactly the "pay for faster access to one literature database" board decision in the
console.

## Guardrails

The institutional rules in `institute/config.py` are stated in every agent's system
prompt **and** enforced in code: computational-only, public data only, full provenance
on every claim, independent checkers that can't be overruled, negative results as
first-class output, and no outward-facing action without a human. They are the same
promises the console footer makes to the board.
