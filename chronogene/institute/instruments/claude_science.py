"""Claude Science — an instrument on the lab's bench.

Claude Science is treated as ONE supplier of evidence, not the system of record.
The lab commissions a sub-study from it, receives the result, and then puts that
result through the same independent checking as anything else. Claude Science
cannot mark its own work "confirmed" — only a checker can, and the checker
reproduces the claim by other means where possible.

CONNECTING IT
-------------
This connector supports two modes. Which one you use depends on how your Claude
Science access is exposed:

  A. MCP connector mode (preferred, and how Anthropic's life-sciences
     connectors are generally surfaced). Set:
         CLAUDE_SCIENCE_MCP_URL     the connector's URL
         CLAUDE_SCIENCE_MCP_TOKEN   the auth token for it
     The lab then reaches it as a tool through the Messages API's MCP support,
     so the research agents can call it mid-analysis.

  B. HTTP mode. If your access is a plain REST endpoint, set:
         CLAUDE_SCIENCE_API_URL     the base URL
         CLAUDE_SCIENCE_API_KEY     the key

Until one of those is configured, `available()` is False and the PI simply will
not commission work from this instrument — the lab keeps running on its other
instruments. Nothing silently pretends to have consulted it.
"""

from __future__ import annotations

import json
import os
from typing import Any

from .base import InstrumentResult

try:
    import requests
except Exception:  # pragma: no cover
    requests = None


MCP_URL = os.environ.get("CLAUDE_SCIENCE_MCP_URL", "")
MCP_TOKEN = os.environ.get("CLAUDE_SCIENCE_MCP_TOKEN", "")
API_URL = os.environ.get("CLAUDE_SCIENCE_API_URL", "")
API_KEY = os.environ.get("CLAUDE_SCIENCE_API_KEY", "")


class ClaudeScience:
    key = "claude_science"
    label = "Claude Science"

    def mode(self) -> str:
        if MCP_URL and MCP_TOKEN:
            return "mcp"
        if API_URL and API_KEY:
            return "http"
        return "unconfigured"

    def available(self) -> bool:
        return self.mode() != "unconfigured"

    def describe(self) -> str:
        m = self.mode()
        if m == "mcp":
            return "Claude Science, reachable as an MCP tool. Commission a sub-study."
        if m == "http":
            return "Claude Science, reachable over HTTP. Commission a sub-study."
        return ("Claude Science is not connected. Set CLAUDE_SCIENCE_MCP_URL + "
                "CLAUDE_SCIENCE_MCP_TOKEN (preferred) or CLAUDE_SCIENCE_API_URL + "
                "CLAUDE_SCIENCE_API_KEY.")

    # --- the MCP tool definition the research agents can call ---------------
    def mcp_server_config(self) -> dict[str, Any] | None:
        """Returned to the agent layer so Claude can call Claude Science directly
        as a tool during an analysis (Messages API MCP connector shape)."""
        if self.mode() != "mcp":
            return None
        return {"type": "url", "name": "claude_science", "url": MCP_URL,
                "authorization_token": MCP_TOKEN}

    # --- direct commission ---------------------------------------------------
    def run(self, query: str, **kwargs: Any) -> InstrumentResult:
        """Commission a sub-study and return its evidence."""
        mode = self.mode()
        if mode == "unconfigured":
            return InstrumentResult(
                instrument=self.key, query=query, ok=False,
                error="Claude Science is not connected; see instrument docstring.")

        if mode == "http":
            return self._run_http(query, **kwargs)

        # MCP mode: the call is made by the agent layer as a tool call, because
        # MCP tools are invoked through the Messages API rather than directly.
        return InstrumentResult(
            instrument=self.key, query=query, ok=False,
            error="MCP mode: commission this through the agent layer "
                  "(orchestrator passes mcp_server_config() to the researcher).")

    def _run_http(self, query: str, **kwargs: Any) -> InstrumentResult:
        if requests is None:
            return InstrumentResult(instrument=self.key, query=query, ok=False,
                                    error="requests not installed")
        try:
            r = requests.post(
                f"{API_URL.rstrip('/')}/studies",
                headers={"Authorization": f"Bearer {API_KEY}",
                         "content-type": "application/json"},
                data=json.dumps({"question": query, **kwargs}),
                timeout=120,
            )
            r.raise_for_status()
            payload = r.json()
        except Exception as exc:
            return InstrumentResult(instrument=self.key, query=query, ok=False,
                                    error=str(exc)[:300])

        return InstrumentResult(
            instrument=self.key,
            query=query,
            ok=True,
            summary=payload.get("summary", ""),
            accessions=payload.get("accessions", []) or payload.get("datasets", []),
            citations=payload.get("citations", []) or payload.get("references", []),
            artifacts=payload.get("artifacts", []),
            raw=payload,
            cost_usd=float(payload.get("cost_usd", 0.0) or 0.0),
        )


INSTRUMENT = ClaudeScience()
