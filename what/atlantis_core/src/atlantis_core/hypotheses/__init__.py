"""atlantis_core.hypotheses — the hypothesis ledger (M-3b-i): literature → testable feature hypotheses with provenance.

    python -m atlantis_core.hypotheses corpus --ecosystem <type> [--refresh] [--max-per-query N] [--no-europepmc]
    python -m atlantis_core.hypotheses --index [--check]

Three parts, one directory (`what/hypotheses/`):
- `corpus`   (`corpus.py`) — the standalone intake (Ingest.aDNA has no literature class yet; the card's documented
  fallback). Reads `corpus/<ecosystem>/queries.yaml`, asks OpenAlex, and writes `corpus/<ecosystem>/manifest.yaml` — the
  committed record: queries · DOIs · OpenAlex ids · titles · years · retrieval time · each abstract's word count and
  sha256 · a result-set sha256. Abstract TEXT goes to `corpus/<ecosystem>/unreviewed/` — gitignored, a path, not a flag
  (README rule 6; operator ruling 3, 2026-10-12: a manifest only, no new snapshots in Atlantis, SO-3).
- `check`    (`check.py`) — every row: the closed `AtlHypothesis` (committed JSON Schema) plus what the schema cannot see
  (README known limit 18), each a failure key.
- `index`    (`index.py`) — `LEDGER.md`, generated, never hand-edited; `--check` writes nothing.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[4] / "hypotheses"   # Atlantis what/hypotheses/
SCHEMA = Path(__file__).resolve().parents[4] / "schema" / "atl_v0" / "atl_ontology_v0.schema.json"
QUOTE_MAX_WORDS = 25    # README rule 1 / operator ruling 3: rows quote ≤ 25 words
POINTER_MAX_WORDS = 40  # a pointer is a locator or a short quotation, never a paragraph


class LedgerError(ValueError):
    pass
