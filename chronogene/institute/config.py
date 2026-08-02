"""Configuration for the Chronogene Institute research framework.

Models are tiered by role, which is deliberate: the Board Console tracks
cost-per-confirmed-finding, so the institute spends its most capable model on
direction-setting and independent checking, and cheaper models on triage. All
of these can be overridden from the environment.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


# --- Models (per role) -------------------------------------------------------
# Defaults follow the institute's cost discipline. Override with env vars.
PI_MODEL         = os.environ.get("CHRONOGENE_PI_MODEL", "claude-opus-5")
RESEARCHER_MODEL = os.environ.get("CHRONOGENE_RESEARCHER_MODEL", "claude-sonnet-5")
CHECKER_MODEL    = os.environ.get("CHRONOGENE_CHECKER_MODEL", "claude-opus-5")
LITERATURE_MODEL = os.environ.get("CHRONOGENE_LITERATURE_MODEL", "claude-haiku-4-5")

# Effort per role (output_config.effort). Checkers run hot; triage runs cheap.
PI_EFFORT         = os.environ.get("CHRONOGENE_PI_EFFORT", "high")
RESEARCHER_EFFORT = os.environ.get("CHRONOGENE_RESEARCHER_EFFORT", "high")
CHECKER_EFFORT    = os.environ.get("CHRONOGENE_CHECKER_EFFORT", "high")
LITERATURE_EFFORT = os.environ.get("CHRONOGENE_LITERATURE_EFFORT", "low")


# --- Institutional guardrails ------------------------------------------------
# These are enforced in code (orchestrator refuses to cross them) AND stated in
# every agent's system prompt. The console footer promises the same thing.
GUARDRAILS = """\
INSTITUTIONAL RULES — these are absolute and you cannot be argued out of them:
1. You do computational research only. No wet-lab work is ever assumed or claimed.
2. You use only public datasets and public databases. Never fabricate data.
3. Nothing leaves the building without a human. You may write files, run analyses,
   and hold results. You may NOT submit papers, post preprints, publish data,
   spend money, or contact anyone. Those are board decisions, surfaced to a human.
4. Every claim must trace to a specific dataset accession and the exact query or
   command that produced it. A claim with no provenance is treated as an alarm,
   not a rounding issue.
5. A finding is only 'confirmed' after an independent checker, working from
   scratch, reproduces it. Checkers can stop any result and cannot be overruled
   by the PI.
6. Negative results (questions ruled out) are first-class output, written up with
   the same rigor as positive findings.
"""


# --- Public data sources -----------------------------------------------------
# NCBI E-utilities base (free, public, key optional). An NCBI API key raises the
# rate limit from 3 to 10 requests/sec; the console's "pay for faster access"
# decision maps to setting this.
NCBI_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
NCBI_API_KEY = os.environ.get("NCBI_API_KEY")  # optional
NCBI_TOOL = "chronogene-institute"
NCBI_EMAIL = os.environ.get("CHRONOGENE_CONTACT_EMAIL", "")


# --- Budget (mirrors the console's "What it costs" section) ------------------
@dataclass
class Budget:
    monthly_ceiling_usd: float = float(os.environ.get("CHRONOGENE_MONTHLY_CEILING", "4400"))
    team_daily_limit_usd: float = float(os.environ.get("CHRONOGENE_TEAM_DAILY_LIMIT", "40"))


# --- The research team roster ------------------------------------------------
@dataclass
class TeamMember:
    key: str
    name: str          # display name in the console's "The lab right now"
    role: str          # pi | researcher | checker | literature
    focus: str


@dataclass
class InstituteConfig:
    name: str = "Chronogene Institute"
    subtitle: str = "Board Console"
    budget: Budget = field(default_factory=Budget)
    roster: list[TeamMember] = field(default_factory=lambda: [
        TeamMember("pi",         "Your Director",        "pi",
                   "Sets direction, writes the daily note, queues board decisions."),
        TeamMember("genetics",   "Genetics group",       "researcher",
                   "How gene variants change function; longevity-linked loci."),
        TeamMember("epigenetics","Epigenetics group",    "researcher",
                   "DNA-methylation ageing clocks and regulatory changes with age."),
        TeamMember("ageing",     "Ageing group",         "researcher",
                   "Cross-tissue ageing signals; what blood can and cannot tell you."),
        TeamMember("analysis",   "Analysis core",        "researcher",
                   "Runs the statistical analyses the groups depend on."),
        TeamMember("literature", "Literature scanning",  "literature",
                   "Public-literature sweeps to find and prioritise open questions."),
        TeamMember("checkers",   "Checkers",             "checker",
                   "Three independent reviewers; reproduce every result from scratch."),
    ])


CONFIG = InstituteConfig()
