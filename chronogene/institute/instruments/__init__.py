"""Instruments — the external capabilities the research team can use.

An "instrument" is anything the lab can point at a question: a public data
repository, a literature index, a compute sandbox, or an external research
service such as Claude Science. Every instrument exposes the same shape, so the
Principal Investigator can commission work without knowing which tool will serve
it, and so **every use is recorded in provenance the same way**.

This is the core of the native-lab design: the lab owns the question, the ledger,
and the checking. Instruments are interchangeable suppliers of evidence.
"""

from .base import Instrument, InstrumentResult, Registry, REGISTRY

__all__ = ["Instrument", "InstrumentResult", "Registry", "REGISTRY"]
