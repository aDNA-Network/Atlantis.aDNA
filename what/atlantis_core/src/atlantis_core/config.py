"""Instance loading and the semantic config hash.

`atlantis.yaml` is the engine config: grid, stream shapes, climatology eras, label parameters, split, and the paths
of the three registries. The registries are `AtlDocument`s (validated by linkml-validate; cross-referenced here).
"""
from __future__ import annotations

import hashlib, json
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from atlantis_core import registry as _registry

# Sections of atlantis.yaml whose values change a trained model. `semantic_hash` covers these and the registries'
# machine-relevant fields — never comments, ordering, prose, or SHAP/site settings (WI-7: the exemplar's bytes-md5
# changed on a SHAP-only edit and stopped matching its metrics).
TRAINING_SECTIONS = ("grid", "streams", "climatology", "climatology_policy", "constants", "vitals", "label", "split", "learner")
STREAM_NON_TRAINING = ("fetch", "summary", "artifact", "lever_stations")   # fetch details are pinned by sha256; lever_stations is what-if only
EVAL_TRAINING_KEYS = ("ablations", "sensitivity_threshold", "surveillance_only")   # they choose WHICH models are trained (M-1b-ii-a III F-2)
VITAL_MACHINE_FIELDS = ("vital_id", "stream_ref", "transform", "lag", "window", "monotone", "group")   # group drives the ablations
EVENT_MACHINE_FIELDS = ("event_id", "event_variable_stream", "threshold", "direction", "horizon")
EVENT_MACHINE_OPTIONAL = ("refractory_weeks",)   # M-2a-i: hashed only when set and non-zero, so every config written before it
                                                 # (absent ≡ 0, the same label) keeps its hash — board v1/v2's acfa22c6e4


@dataclass
class Instance:
    root: Path
    cfg: dict
    streams: dict = field(default_factory=dict)   # stream_id → AtlObservationStream dict
    vitals: list = field(default_factory=list)    # AtlVital dicts, registry order
    events: dict = field(default_factory=dict)    # event_id → AtlEventDefinition dict
    declared: dict = field(default_factory=dict)  # kind → every id as written (duplicates kept, for registry R1)
    obligations: list = field(default_factory=list)  # what downstream stages MUST do for this config to be honest (R7)

    @property
    def event(self) -> dict:
        return self.events[self.cfg["label"]["event"]]

    @property
    def vital_ids(self) -> list[str]:
        return [v["vital_id"] for v in self.vitals]

    @property
    def feature_names(self) -> list[str]:
        """Column names of the vitals table: the vital id without its `atl_vital_` prefix."""
        return [feature_name(v) for v in self.vitals]

    def path(self, rel: str) -> Path:
        return (self.root / rel).resolve()

    def stream_spec(self, stream_id: str) -> dict:
        return self.cfg["streams"][stream_id]

    def climatology(self, stream_id: str) -> tuple[int, int] | None:
        era = self.cfg.get("climatology", {}).get(stream_id)
        return (int(era[0]), int(era[1])) if era else None

    def constant(self, name: str) -> float:
        return float(self.cfg["constants"][name])


def feature_name(vital: dict) -> str:
    vid = vital["vital_id"]
    return vid[len("atl_vital_"):] if vid.startswith("atl_vital_") else vid


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def load_instance(root, config_name: str = "atlantis.yaml", check: bool = True) -> Instance:
    root = Path(root).resolve()
    cfg = load_yaml(root / config_name)
    inst = Instance(root=root, cfg=cfg)
    reg = cfg["registries"]
    docs = [load_yaml(root / reg[k]) for k in ("streams", "features", "events")]
    inst.declared = {"stream": [], "vital": [], "event": []}
    for d in docs:
        for s in d.get("observation_streams", []) or []:
            inst.streams.setdefault(s["stream_id"], s); inst.declared["stream"].append(s["stream_id"])
        for v in d.get("vitals", []) or []:
            inst.vitals.append(v); inst.declared["vital"].append(v["vital_id"])
        for e in d.get("event_definitions", []) or []:
            inst.events.setdefault(e["event_id"], e); inst.declared["event"].append(e["event_id"])
    if check:
        _registry.check(inst)
    return inst


def _strip_streams(streams: dict) -> dict:
    return {sid: {k: v for k, v in spec.items() if k not in STREAM_NON_TRAINING} for sid, spec in streams.items()}


def semantic_hash(inst: Instance, learner: dict | None = None) -> str:
    """md5 (first 10 hex, same width as the exemplar's bytes hash) of a canonical JSON of the training-relevant
    config sections + the machine fields of every vital and event. Key order, comments and prose do not move it.
    `learner` overrides `cfg.learner` — a learner swap's results carry the hash of the learner that produced them."""
    cfg = dict(inst.cfg)
    if learner is not None:
        cfg["learner"] = learner
    if "split" in cfg:   # M-1f: the embargo as RESOLVED — absent means the event horizon, so absent must move the hash;
        from atlantis_core.eval import embargo_weeks   # `none` (off) is hashed as v2's split was, so acfa22c6e4 re-derives
        E = embargo_weeks(cfg["split"], inst.event["horizon"])
        cfg["split"] = {**{k: v for k, v in cfg["split"].items() if k != "embargo_weeks"}, **({"embargo_weeks": E} if E else {})}
    payload = {
        "config": {k: (_strip_streams(cfg[k]) if k == "streams" else cfg[k]) for k in TRAINING_SECTIONS if k in cfg},
        "eval": {k: (cfg.get("eval") or {}).get(k) for k in EVAL_TRAINING_KEYS},
        "vitals": [{k: v.get(k) for k in VITAL_MACHINE_FIELDS} for v in inst.vitals],
        "events": [{**{k: inst.events[e].get(k) for k in EVENT_MACHINE_FIELDS},
                    **{k: inst.events[e][k] for k in EVENT_MACHINE_OPTIONAL if inst.events[e].get(k)}}
                   for e in sorted(inst.events)],
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.md5(blob.encode()).hexdigest()[:10]
