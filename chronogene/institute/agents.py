"""The agentic research team, built on the Anthropic SDK.

Every agent is a thin, auditable wrapper over the Messages API:
  - `Agent.think(prompt)`          -> free text (adaptive thinking, per-role effort)
  - `Agent.decide(prompt, schema)` -> a validated JSON object (structured outputs)

Roles:
  PrincipalInvestigator  sets direction, writes the daily note, frames decisions
  Researcher             proposes and works up claims from public data
  Checker                independently reproduces a claim and returns a verdict
  LiteratureScanner      triages open questions from the public literature

If ANTHROPIC_API_KEY (or an `ant auth login` profile) is unavailable, agents run
in OFFLINE mode: they return deterministic, clearly-labelled placeholders so a
research cycle and the console can still be produced end-to-end without spend.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from . import config

try:  # SDK is optional at import time so offline mode always works.
    import anthropic
except Exception:  # pragma: no cover
    anthropic = None


def _make_client():
    """Return an Anthropic client, or None if unavailable (offline mode)."""
    if anthropic is None:
        return None
    try:
        return anthropic.Anthropic()
    except Exception:
        return None


# One shared client for the whole team.
_CLIENT = _make_client()


def online() -> bool:
    return _CLIENT is not None


@dataclass
class Agent:
    """A single research-team member backed by one Claude model."""

    name: str
    role: str
    model: str
    effort: str
    system: str

    # --- free-text reasoning -------------------------------------------------
    def think(self, prompt: str, *, max_tokens: int = 4000) -> str:
        if _CLIENT is None:
            return f"[offline:{self.role}] {prompt[:120].strip()}…"
        # Stream so large max_tokens never trips the SDK HTTP-timeout guard.
        with _CLIENT.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system,
            thinking={"type": "adaptive"},
            output_config={"effort": self.effort},
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            msg = stream.get_final_message()
        return _text_or_refusal(msg)

    # --- structured decisions ------------------------------------------------
    def decide(self, prompt: str, schema: dict[str, Any], *, offline_stub: dict | None = None,
               max_tokens: int = 4000) -> dict[str, Any]:
        """Return a JSON object validated against `schema` (a JSON Schema object)."""
        if _CLIENT is None:
            return offline_stub or {"offline": True, "role": self.role}
        with _CLIENT.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system,
            output_config={
                "effort": self.effort,
                "format": {"type": "json_schema", "schema": schema},
            },
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            msg = stream.get_final_message()
        if msg.stop_reason == "refusal":
            return {"refused": True, "role": self.role}
        text = next((b.text for b in msg.content if b.type == "text"), "{}")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"parse_error": True, "raw": text[:500]}


def _text_or_refusal(msg) -> str:
    if getattr(msg, "stop_reason", None) == "refusal":
        return "[refused by safety classifier]"
    return "".join(b.text for b in msg.content if b.type == "text").strip()


# --- Role factories ----------------------------------------------------------

def _system(role_desc: str) -> str:
    return (
        f"You are part of the {config.CONFIG.name}, a computational research "
        f"institute studying epigenetic ageing.\n\n{role_desc}\n\n{config.GUARDRAILS}"
    )


def principal_investigator() -> Agent:
    return Agent(
        name="Your Director", role="pi",
        model=config.PI_MODEL, effort=config.PI_EFFORT,
        system=_system(
            "You are the Principal Investigator. You set the research agenda, "
            "decide which open questions the lab spends time on, and write a short "
            "plain-language daily note for the board — a non-specialist reader who "
            "funds the lab. You frame decisions that only a human should make "
            "(submitting a paper, spending money) as clear either/or choices with "
            "an explicit 'if you do nothing' default. You never overrule a checker."
        ),
    )


def researcher(member: config.TeamMember) -> Agent:
    return Agent(
        name=member.name, role="researcher",
        model=config.RESEARCHER_MODEL, effort=config.RESEARCHER_EFFORT,
        system=_system(
            f"You are the {member.name}: {member.focus} You work up candidate "
            "findings from public datasets. For each claim you must state the exact "
            "dataset accession(s) and the query/analysis that produced it, the "
            "population and tissue it holds for, and how strong you think the "
            "evidence is. You are rewarded as much for ruling a question out as for "
            "confirming one. You never overstate scope."
        ),
    )


def checker() -> Agent:
    return Agent(
        name="Checkers", role="checker",
        model=config.CHECKER_MODEL, effort=config.CHECKER_EFFORT,
        system=_system(
            "You are an independent Checker. You receive a claim and its stated "
            "provenance and you try to break it, working from scratch. You assess "
            "whether the evidence supports the claim at the stated scope, whether "
            "the provenance is complete and traceable, and whether the strength "
            "rating is honest. You can stop any result. You are not swayed by how "
            "much work went into it or by the PI's preferences. Report a verdict of "
            "reproduced, needs_revision, or failed, with your reasoning."
        ),
    )


def literature_scanner() -> Agent:
    return Agent(
        name="Literature scanning", role="literature",
        model=config.LITERATURE_MODEL, effort=config.LITERATURE_EFFORT,
        system=_system(
            "You are the Literature Scanner. Given public dataset and literature "
            "metadata, you surface and prioritise open, testable questions in "
            "epigenetic ageing that the lab could answer computationally. You favour "
            "questions that are under-tested, replicable, and cheap to check."
        ),
    )
