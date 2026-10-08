"""atlantis_core — the Atlantis reference implementation (P1, extracted from the Gulf K. brevis exemplar).

An instance is a directory holding `atlantis.yaml` (engine config) and the `AtlDocument` registries it names
(`streams.yaml` · `features.yaml` · `events.yaml`). Behaviour is declared there, not in code:

    inst = load_instance(path)            # config + registries, cross-reference checked
    table = vitals.build(inst, frames)    # patient × week vitals, registry order
    table = label.make(inst, table, ...)  # direction-aware onset label + drop flags
    python -m atlantis_core.selftest --instance <path>   # SO-7: perturbs every registered stream

Nothing here fetches on import, holds data, or is an operational forecast (SO-3, SO-4).
"""
from atlantis_core.config import Instance, load_instance, semantic_hash

__version__ = "0.6.0"
__all__ = ["Instance", "load_instance", "semantic_hash", "__version__"]
