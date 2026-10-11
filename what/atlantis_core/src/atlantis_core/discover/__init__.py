"""discover — stream discovery: playbook §A as a skill, §B as checks (M-3a).

The skill (`how/skills/skill_stream_discovery.md`) is the search: an agent walks §A's six steps and records what it found,
and what it looked for and did not find, in `<instance>/discovery/candidates.yaml`. This package is the half that can be
checked:

    rows.pointer_rows(doc)      # candidates → AtlObservationStream pointer rows (no fetch provenance, ever)
    rows.validate_rows(rows)    # atl_v0 + fetcher names + surveillance stated
    rows.compare(rows, path)    # the declarative fields against an existing streams.yaml (a re-discovery must reproduce)
    probe.probe_stream(…)       # count-only requests, in memory (only with --probe)
    traps.run_all(inst, …)      # the six §B traps

    python -m atlantis_core.discover --instance <dir> [--probe] [--compare <dir>/streams.yaml]

It writes `<instance>/discovery/streams.discovered.yaml` and `discovery_memo.{json,md}`. It never writes `streams.yaml`
(fork and the steward own it) and never caches an artifact.
"""
from atlantis_core.discover.rows import DiscoveryError, compare, load_candidates, pointer_rows, validate_rows
from atlantis_core.discover.traps import TRAPS, run_all

__all__ = ["DiscoveryError", "compare", "load_candidates", "pointer_rows", "validate_rows", "TRAPS", "run_all"]
