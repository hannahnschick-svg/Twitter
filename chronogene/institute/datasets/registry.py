"""A registry of well-known, public epigenetic-ageing resources.

These are real, publicly documented DNA-methylation ageing clocks and the kinds
of public datasets used to build and test them. The registry gives the research
team concrete, checkable starting points and search terms; it does NOT bundle any
data — everything is fetched live from public sources at run time.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Clock:
    name: str
    year: int
    tissue: str
    n_sites: str
    note: str


# Public, widely-cited DNA-methylation ageing clocks.
CLOCKS: list[Clock] = [
    Clock("Horvath pan-tissue clock", 2013, "multi-tissue", "353 CpG",
          "First multi-tissue epigenetic clock; estimates chronological age."),
    Clock("Hannum blood clock", 2013, "whole blood", "71 CpG",
          "Blood-based clock; strong chronological-age predictor."),
    Clock("PhenoAge (Levine)", 2018, "whole blood", "513 CpG",
          "Trained on a phenotypic-age composite; tracks morbidity/mortality."),
    Clock("GrimAge", 2019, "whole blood", "1030 CpG",
          "Predicts time-to-death; built on DNAm surrogates of plasma proteins."),
    Clock("DunedinPACE", 2022, "whole blood", "173 CpG",
          "Estimates the pace of ageing rather than an age value."),
]

# Search terms the literature scanner and researchers can hand to the GEO
# connector. Kept broad and public; the connector tags each hit with the term
# that surfaced it, so provenance is preserved.
GEO_SEARCH_TERMS: list[str] = [
    "DNA methylation aging blood Illumina 450K",
    "epigenetic clock methylation human",
    "methylation age liver tissue",
    "longevity GWAS methylation regulatory region",
    "leukocyte DNA methylation age European",
]

# Domain glossary the PI uses to keep the daily note in plain language.
GLOSSARY: dict[str, str] = {
    "methylation": "a chemical tag on DNA that changes with age, usable to "
                   "estimate how fast someone is ageing",
    "epigenetic clock": "a model that reads methylation tags to estimate age",
    "CpG site": "a specific spot on the DNA where a methylation tag can sit",
}
