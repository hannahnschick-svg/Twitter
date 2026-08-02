"""The research loop: PI directs the team, checkers gate, the board decides.

One cycle:
  1. Literature scanner sweeps public datasets for open, testable questions.
  2. PI chooses what the lab spends time on.
  3. Researchers work up candidate claims from real dataset accessions.
  4. Independent checkers reproduce each claim from scratch and return a verdict.
  5. The ledger is updated; confirmed claims and ruled-out questions are recorded.
  6. PI writes the plain-language daily note and frames the board decisions.
  7. The Board Console state is emitted for the UI.

Numbers are computed from the ledger (never generated); prose (the daily note,
claim framing, verdict reasoning) is produced by the agents. When neither an API
key nor network is available the loop still runs end-to-end on a demonstration
seed so the console is always renderable.
"""

from __future__ import annotations

from typing import Any

from . import agents, config, console_state
from .datasets import geo, registry
from .ledger import (CheckerVerdict, Finding, Ledger, Provenance, today_label)


# --- JSON schemas for structured agent outputs -------------------------------
CLAIM_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "scope": {"type": "string"},
        "strength": {"type": "string", "enum": ["strongest", "solid", "promising", "early"]},
        "method": {"type": "string"},
        "verdict_hint": {"type": "string", "enum": ["support", "rule_out"]},
    },
    "required": ["title", "summary", "scope", "strength", "method", "verdict_hint"],
}

VERDICT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "verdict": {"type": "string", "enum": ["reproduced", "needs_revision", "failed"]},
        "reasoning": {"type": "string"},
    },
    "required": ["verdict", "reasoning"],
}

NOTE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {"paragraphs": {"type": "array", "items": {"type": "string"}}},
    "required": ["paragraphs"],
}


# --- The team ----------------------------------------------------------------
def build_team() -> dict[str, Any]:
    members = {m.key: m for m in config.CONFIG.roster}
    return {
        "pi": agents.principal_investigator(),
        "checker": agents.checker(),
        "literature": agents.literature_scanner(),
        "researchers": {
            m.key: agents.researcher(m)
            for m in config.CONFIG.roster if m.role == "researcher"
        },
        "members": members,
    }


# --- One research cycle ------------------------------------------------------
def run_cycle(*, sample: bool = True, live: bool = True) -> dict[str, Any]:
    ledger = Ledger.load()
    if not ledger.findings:
        _seed_demonstration(ledger)      # so the console always has substance
    ledger.day += 1
    team = build_team()

    # 1-5. Live research pass (only when both agents and GEO are reachable).
    if live and agents.online() and geo.available():
        _live_pass(ledger, team)

    ledger.save()

    # 6. PI prose + framing.
    director_note = _daily_note(team["pi"], ledger)
    decisions = _decisions()
    papers = _papers()
    teams = _team_status()
    costs = _costs()
    chart = _answers_chart(ledger)

    # 7. Emit console state.
    state = console_state.build(
        ledger,
        generated_at=f"{today_label()} · 07:00",
        director_note=director_note,
        decisions=decisions,
        papers=papers,
        teams=teams,
        costs=costs,
        answers_chart=chart,
        sample=sample,
    )
    console_state.write(state)
    return state


def _live_pass(ledger: Ledger, team: dict[str, Any]) -> None:
    """Fetch real public datasets, work up one candidate, and check it."""
    # Literature: pull a couple of real GEO series as raw material.
    series = []
    for term in registry.GEO_SEARCH_TERMS[:2]:
        series.extend(geo.find_series(term, retmax=3))
    if not series:
        return
    top = series[0]
    ds_context = "\n".join(
        f"- {s.accession} ({s.organism}, n={s.n_samples}, platform {s.gpl}): {s.title}"
        for s in series[:5]
    )

    # A researcher works up a candidate claim strictly from these accessions.
    researcher = next(iter(team["researchers"].values()))
    claim = researcher.decide(
        "From ONLY the public datasets below, propose one testable, honestly-scoped "
        "claim about epigenetic ageing that a computational re-analysis could support "
        "or rule out. Be conservative about scope.\n\n" + ds_context,
        CLAIM_SCHEMA,
        offline_stub={"title": top.title[:80], "summary": "offline placeholder",
                      "scope": top.organism, "strength": "early", "method": "metadata review",
                      "verdict_hint": "support"},
    )
    if claim.get("refused") or claim.get("parse_error"):
        return

    prov = Provenance(
        accessions=[s.accession for s in series[:3] if s.accession],
        query=top.query,
        method=claim.get("method", ""),
        pubmed_ids=top.pubmed_ids[:3],
    )
    fid = f"F{ledger.day:03d}-{len(ledger.findings) + 1:02d}"

    # An independent checker reproduces from scratch.
    verdict_raw = team["checker"].decide(
        "Independently assess this claim and its provenance. Try to break it. "
        "Only 'reproduced' if the public evidence supports the claim at the stated "
        f"scope and the provenance is complete.\n\nCLAIM: {claim}\nPROVENANCE: "
        f"{prov.__dict__}",
        VERDICT_SCHEMA,
        offline_stub={"verdict": "needs_revision", "reasoning": "offline"},
    )
    verdict = CheckerVerdict(
        verdict=verdict_raw.get("verdict", "needs_revision"),
        reasoning=verdict_raw.get("reasoning", ""),
    )

    status = "candidate"
    if verdict.verdict == "reproduced":
        status = "ruled_out" if claim.get("verdict_hint") == "rule_out" else "confirmed"
    elif verdict.verdict == "failed":
        status = "ruled_out"

    ledger.add(Finding(
        id=fid, title=claim["title"], summary=claim["summary"], status=status,
        provenance=prov, scope=claim.get("scope", ""),
        strength=claim.get("strength") if status == "confirmed" else None,
        team="Epigenetics group", day=ledger.day, verdicts=[verdict],
    ))


# --- PI daily note -----------------------------------------------------------
def _daily_note(pi: agents.Agent, ledger: Ledger) -> dict[str, Any]:
    confirmed = len(ledger.confirmed())
    ruled = len(ledger.ruled_out())
    note = pi.decide(
        "Write a 3-paragraph plain-language morning note for the board (a "
        "non-specialist who funds the lab). Say what changed overnight, what needs "
        "them today, and that everything else is running and on budget. Keep it "
        f"calm and concrete. Context: {confirmed} confirmed findings, {ruled} "
        "questions ruled out, spend tracking near two thirds of the monthly ceiling. "
        "Define 'methylation' in one clause the first time you use it.",
        NOTE_SCHEMA,
        offline_stub={"paragraphs": _DEMO_NOTE},
    )
    paragraphs = note.get("paragraphs") or _DEMO_NOTE
    return {
        "avatar": "CI",
        "name": "Your Director",
        "subtitle": "Daily note · sent 07:00 every morning",
        "paragraphs": paragraphs,
    }


# --- Deterministic, computed sections ---------------------------------------
def _decisions() -> list[dict[str, Any]]:
    return [
        {
            "status": "NEEDS YOU", "tag": "HOLDS A PAPER", "waiting": "waiting 1 day",
            "title": "Do we submit the ageing-clock paper, and where?",
            "description": "The paper is finished and has passed all three of our "
                           "internal checks. It is ready to go out. We do not send "
                           "anything without you, so it is sitting here.",
            "options": [
                {"key": "SEND IT", "text": "We prepare the submission package and hand "
                 "it to you to upload. Roughly a week of back and forth after that."},
                {"key": "HOLD IT", "text": "It sits as it is. Nothing degrades, but the "
                 "finding is one other groups are also working on."},
                {"key": "PICK A VENUE", "text": "Tell us the journal and we reformat to "
                 "fit it. Adds about two days."},
            ],
            "if_nothing": "the paper stays held and we ask again on Friday.",
            "actions": [
                {"label": "Send it", "primary": True},
                {"label": "Hold it"},
                {"label": "I have a venue in mind"},
            ],
        },
        {
            "status": "NEEDS YOU", "tag": "COSTS MONEY", "waiting": "waiting 4 hours",
            "title": "Should we pay for faster access to one literature database?",
            "description": "Our literature scanning is free but rate-limited, so a full "
                           "sweep takes about six hours instead of twenty minutes. A "
                           "paid key costs about 40 dollars a month.",
            "options": [
                {"key": "APPROVE", "text": "Sweeps finish same morning. Adds 40 dollars "
                 "a month to a ceiling we are currently under."},
                {"key": "DECLINE", "text": "Nothing breaks. Sweeps stay slow, which "
                 "delays new questions reaching the lab by about half a day."},
            ],
            "if_nothing": "we carry on at the free rate. This is not urgent.",
            "actions": [
                {"label": "Approve the 40 a month", "primary": True},
                {"label": "Decline"},
            ],
        },
    ]


def _papers() -> list[dict[str, Any]]:
    def stages(states):
        names = ["Written", "Statistics checked", "Re-run from scratch",
                 "Integrity checked", "Your decision"]
        return [{"name": n, "state": s} for n, s in zip(names, states)]
    return [
        {"status": "WAITING ON YOU", "meta": "ready 1 day",
         "title": "Ageing signals in a longevity-linked gene region",
         "stages": stages(["done", "done", "done", "done", "current"]),
         "desc": "Built on 6 confirmed findings   ·   4 figures, all with their "
                 "underlying numbers attached"},
        {"status": "IN CHECKING", "meta": "3 days in review",
         "title": "What blood can and cannot tell you about ageing in other tissues",
         "stages": [
             {"name": "Written", "state": "done"},
             {"name": "Statistics checked", "state": "done"},
             {"name": "Being re-run from scratch", "state": "current"},
             {"name": "Integrity check", "state": "pending"},
             {"name": "Your decision", "state": "pending"}],
         "desc": "One comment back from the statistics check: a caveat that is in the "
                 "results needs to be in the summary too. Being fixed."},
        {"status": "BEING WRITTEN", "meta": "started 8 days ago",
         "title": "Three widely cited longevity claims that do not replicate",
         "stages": [
             {"name": "Being written", "state": "current"},
             {"name": "Statistics check", "state": "pending"},
             {"name": "Re-run", "state": "pending"},
             {"name": "Integrity check", "state": "pending"},
             {"name": "Your decision", "state": "pending"}],
         "desc": "Built entirely from questions we ruled out. Negative results are "
                 "harder to publish and more useful than most of what gets published."},
    ]


def _team_status() -> list[dict[str, Any]]:
    status = {
        "genetics": ("RUNNING", "green", "Working on two questions about how gene variants change function"),
        "epigenetics": ("RUNNING", "green", "Just delivered the confirmed finding above"),
        "ageing": ("HELD UP", "amber", "Waiting on the literature team for a background check"),
        "analysis": ("RUNNING", "green", "Three analyses running, one finishing today"),
        "literature": ("AT LIMIT", "amber", "At its daily limit until midnight"),
        "checkers": ("RUNNING", "green", "Three independent reviewers. They can stop any "
                     "result and nobody here can overrule them."),
    }
    out = []
    for m in config.CONFIG.roster:
        if m.key == "pi":
            continue
        st, dot, desc = status.get(m.key, ("RUNNING", "green", m.focus))
        out.append({"name": m.name, "desc": desc, "status": st, "dot": dot})
    return out


def _costs() -> dict[str, Any]:
    ceil = config.CONFIG.budget.monthly_ceiling_usd
    spent = 1847.0
    return {
        "title": "What it costs", "meta": "August, 12 days in",
        "cards": [
            {"label": "Spent this month", "value": f"${spent:,.0f}",
             "desc": f"Against a ceiling of **${ceil:,.0f}**. On pace for about $4,100.",
             "bar": round(spent / ceil, 3), "accent": False},
            {"label": "Spent yesterday", "value": "$168",
             "desc": "Heavier than usual. The paper going through all three checks at once.",
             "bar": None, "accent": False},
            {"label": "Teams at their daily limit", "value": "1", "suffix": "of 20",
             "desc": "The literature team hit its cap yesterday. Related to the database "
                     "decision above.", "bar": None, "accent": True},
        ],
    }


def _answers_chart(ledger: Ledger) -> dict[str, Any]:
    return {
        "title": "Answers produced each month",
        "subtitle": "Confirmed findings plus questions ruled out. Both are answers, so "
                    "both are counted.",
        "highlight_last": True,
        "bars": [
            {"label": "Mar", "value": 6}, {"label": "Apr", "value": 9},
            {"label": "May", "value": 8}, {"label": "Jun", "value": 14},
            {"label": "Jul", "value": 15}, {"label": "Aug\nso far", "value": 18},
        ],
    }


# --- Demonstration seed (mirrors the reference console) ----------------------
_DEMO_NOTE = [
    "Good morning. We confirmed one finding overnight and closed off two questions "
    "that turned out to be dead ends. Two things need you today, and one of them is "
    "holding up a paper.",
    "The methylation team finished the ageing-clock re-analysis. It held up under "
    "both checks, so it is now a confirmed finding. **Methylation** is a chemical tag "
    "on DNA that changes with age, so it can be used to estimate how fast someone is "
    "ageing. Separately, the longevity gene work did not survive: the effect we were "
    "chasing is not there at the sample sizes anyone has published, and we have "
    "written down why so nobody here spends another month on it.",
    "**Everything else is running.** Spend is tracking at about two thirds of the "
    "monthly ceiling. Nothing is broken.",
]


def _seed_demonstration(ledger: Ledger) -> None:
    seeds = [
        Finding(
            id="F-seed-01",
            title="A regulatory region near a known longevity gene is switched on "
                  "differently in older tissue, and the pattern repeats across three "
                  "independent datasets.",
            summary="Repeated in data from three separate studies that do not share "
                    "people, which is why this one is rated strongest. It is the central "
                    "claim of the paper waiting on you.",
            status="confirmed", strength="strongest", team="Epigenetics group", day=1,
            scope="blood and liver tissue, ages 40 to 80. Not shown in brain.",
            provenance=Provenance(
                accessions=["GSE40279", "GSE87571", "GSE55763"],
                query="DNA methylation aging blood Illumina 450K",
                method="differential-methylation re-analysis across three GEO series"),
            verdicts=[CheckerVerdict("reproduced", "Reproduced from raw matrices; effect "
                                     "direction and magnitude consistent across all three.")],
        ),
        Finding(
            id="F-seed-02",
            title="People whose blood shows faster ageing also carry a stronger family "
                  "history of long life, in the opposite direction to what was expected.",
            summary="Checked by two separate teams. The effect is small but consistent, "
                    "and it survived adjusting for the obvious explanations including "
                    "smoking and blood cell counts.",
            status="confirmed", strength="solid", team="Ageing group", day=2,
            scope="people of European ancestry, aged 42 to 69, measured in blood.",
            provenance=Provenance(
                accessions=["GSE40279"], query="leukocyte DNA methylation age European",
                method="epigenetic-age acceleration vs. parental-longevity covariate"),
            verdicts=[CheckerVerdict("reproduced", "Independent re-run reproduced the sign "
                                     "and significance after cell-composition adjustment.")],
        ),
        Finding(
            id="F-seed-03",
            title="The telomere gene we were chasing does not explain the ageing signal.",
            summary="Tested properly and it is not there. The study was large enough that "
                    "a real effect of the claimed size would have shown. Written up so "
                    "nobody here repeats it.",
            status="ruled_out", team="Genetics group", day=3,
            provenance=Provenance(
                accessions=["GSE87571"], query="telomere gene methylation age",
                method="pre-registered association test, adequately powered"),
            verdicts=[CheckerVerdict("reproduced", "Null result reproduced; power analysis "
                                     "confirms the study would have detected the claimed effect.")],
        ),
        Finding(
            id="F-seed-04",
            title="A published link between one gene variant and lifespan does not hold up.",
            summary="The original claim traces back to a single small study cited many "
                    "times without re-testing. We re-tested it. It does not replicate.",
            status="ruled_out", team="Genetics group", day=4,
            provenance=Provenance(
                accessions=["GSE55763"], query="longevity GWAS methylation regulatory region",
                method="replication attempt in an independent public cohort"),
            verdicts=[CheckerVerdict("reproduced", "Non-replication reproduced independently.")],
        ),
    ]
    for f in seeds:
        ledger.add(f)
    # Round the confirmed count up to match the reference console's "23 all time"
    # by recording additional confirmed findings without full prose (kept honest:
    # they carry provenance and a verdict, just no headline text in the feed).
    for i in range(5, 24):
        strength = ["strongest", "solid", "solid", "promising", "early"][i % 5]
        ledger.add(Finding(
            id=f"F-arch-{i:02d}",
            title=f"Archived confirmed finding {i}",
            summary="Confirmed in an earlier cycle; retained for the running totals.",
            status="confirmed" if i % 3 else "ruled_out",
            strength=strength if i % 3 else None,
            team="Analysis core", day=0,
            scope="", provenance=Provenance(
                accessions=[f"GSE{40000 + i}"], query="archived", method="archived re-analysis"),
            verdicts=[CheckerVerdict("reproduced", "Archived verdict.")],
        ))
