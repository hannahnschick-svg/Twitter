"""NCBI GEO connector via the public E-utilities API.

GEO (Gene Expression Omnibus) is a free public repository. This connector is
read-only and hits only public endpoints. It is the institute's window onto real
DNA-methylation and expression datasets — the raw material every claim must
trace back to.

Rate limit: 3 requests/sec without a key, 10/sec with NCBI_API_KEY set. The
console's "pay for faster access to one literature database" decision maps
directly onto obtaining that key.
"""

from __future__ import annotations

import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from typing import Any

try:
    import requests
except Exception:  # pragma: no cover
    requests = None

from .. import config

_LAST_CALL = 0.0
_MIN_INTERVAL = 0.11 if config.NCBI_API_KEY else 0.34  # be a good API citizen


@dataclass
class GeoSeries:
    accession: str          # e.g. GSE40279
    uid: str
    title: str
    summary: str
    organism: str
    n_samples: int | None
    gpl: str                # platform (e.g. GPL13534 = Illumina 450K methylation)
    pubmed_ids: list[str]
    query: str              # the exact search that surfaced this series (provenance)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _throttle() -> None:
    global _LAST_CALL
    dt = time.time() - _LAST_CALL
    if dt < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - dt)
    _LAST_CALL = time.time()


def _params(extra: dict) -> dict:
    p = {"tool": config.NCBI_TOOL, **extra}
    if config.NCBI_API_KEY:
        p["api_key"] = config.NCBI_API_KEY
    if config.NCBI_EMAIL:
        p["email"] = config.NCBI_EMAIL
    return p


def available() -> bool:
    return requests is not None


def search(term: str, *, retmax: int = 10) -> list[str]:
    """Return GEO DataSet UIDs matching `term`. Empty list if offline/unreachable."""
    if requests is None:
        return []
    _throttle()
    try:
        r = requests.get(
            f"{config.NCBI_EUTILS}/esearch.fcgi",
            params=_params({"db": "gds", "term": term, "retmax": retmax, "retmode": "json"}),
            timeout=20,
        )
        r.raise_for_status()
        return r.json().get("esearchresult", {}).get("idlist", [])
    except Exception:
        return []


def summarize(uids: list[str], *, query: str = "") -> list[GeoSeries]:
    """Fetch document summaries for a list of GEO UIDs."""
    if requests is None or not uids:
        return []
    _throttle()
    out: list[GeoSeries] = []
    try:
        r = requests.get(
            f"{config.NCBI_EUTILS}/esummary.fcgi",
            params=_params({"db": "gds", "id": ",".join(uids), "retmode": "json"}),
            timeout=25,
        )
        r.raise_for_status()
        result = r.json().get("result", {})
        for uid in result.get("uids", []):
            d = result.get(uid, {})
            out.append(GeoSeries(
                accession=d.get("accession", ""),
                uid=uid,
                title=d.get("title", ""),
                summary=(d.get("summary", "") or "")[:1200],
                organism=d.get("taxon", ""),
                n_samples=_safe_int(d.get("n_samples")),
                gpl=d.get("gpl", ""),
                pubmed_ids=[str(p) for p in d.get("pubmedids", [])],
                query=query,
            ))
    except Exception:
        return out
    return out


def find_series(term: str, *, retmax: int = 8) -> list[GeoSeries]:
    """Search + summarize in one call, tagging each hit with its provenance query."""
    return summarize(search(term, retmax=retmax), query=term)


def _safe_int(v) -> int | None:
    try:
        return int(v)
    except (TypeError, ValueError):
        return None
