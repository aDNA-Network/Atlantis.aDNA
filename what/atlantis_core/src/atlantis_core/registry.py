"""Cross-reference checks on an instance's registries — what linkml-validate cannot see.

`linkml-validate -C AtlDocument` proves each registry FILE has the `atl_v0` shape (closed classes, enums, the lever
rule). It cannot see across files or into the transform grammar. This does:

  R1  ids unique within their kind (stream · vital · event)
  R2  every vital's stream_ref and every event's event_variable_stream names a declared stream
  R3  every transform parses under the grammar; windowed ops ⇔ a `window` slot
  R4  a lever vital names a non-blank owner (re-asserted: the schema rule's null hole was M-1c's Finding 1)
  R5  every declared stream has an engine spec in atlantis.yaml (shape · columns · artifact) and a known shape;
      a station-keyed stream maps its stations to units; `fetcher` (if set) names a known fetcher class
  R6  `label.event` names a declared event; its direction is above | below
  R7  every climatology era ends before validation starts (a training-era normal must not reach val/test weeks)

Raises RegistryError listing every failure, not just the first.
"""
from __future__ import annotations

from collections import Counter

from atlantis_core.vitals import grammar

SHAPES = {"point": ("date", "value", "lat", "lon"), "unit_daily": ("date", "value", "unit"),
          "station_daily": ("date", "value", "station")}


class RegistryError(ValueError):
    pass


def check(inst) -> None:
    from atlantis_core.fetch import FETCHERS
    errs = []
    cfg = inst.cfg
    # R1
    for kind, ids in inst.declared.items():
        errs += [f"R1 duplicate {kind} id {i}" for i, n in Counter(ids).items() if n > 1]
    # R2
    for v in inst.vitals:
        if v.get("stream_ref") not in inst.streams:
            errs.append(f"R2 {v['vital_id']}: stream_ref {v.get('stream_ref')!r} not declared")
    for e in inst.events.values():
        if e.get("event_variable_stream") not in inst.streams:
            errs.append(f"R2 {e['event_id']}: event_variable_stream {e.get('event_variable_stream')!r} not declared")
    # R3
    consts = list(cfg.get("constants", {}))
    for v in inst.vitals:
        try:
            node = grammar.parse(v["transform"], consts, v["vital_id"])
        except grammar.TransformError as ex:
            errs.append(f"R3 {ex}"); continue
        windowed = bool(grammar.functions_used(node) & grammar.WINDOWED)
        if windowed and not v.get("window"):
            errs.append(f"R3 {v['vital_id']}: windowed transform without a `window` slot")
        if v.get("window") and not windowed:
            errs.append(f"R3 {v['vital_id']}: `window` set but the transform uses no windowed op")
    # R4
    for v in inst.vitals:
        if v.get("tag") == "lever" and not (isinstance(v.get("owner"), str) and v["owner"].strip()):
            errs.append(f"R4 {v['vital_id']}: lever without a non-blank owner")
    # R5
    specs = cfg.get("streams", {})
    for sid, s in inst.streams.items():
        spec = specs.get(sid)
        if spec is None:
            errs.append(f"R5 {sid}: no engine spec under atlantis.yaml → streams"); continue
        shape = spec.get("shape")
        if shape not in SHAPES:
            errs.append(f"R5 {sid}: shape {shape!r} not in {sorted(SHAPES)}"); continue
        missing = [c for c in SHAPES[shape] if c not in spec.get("columns", {})]
        if missing:
            errs.append(f"R5 {sid}: columns missing {missing}")
        if shape == "station_daily" and not spec.get("stations"):
            errs.append(f"R5 {sid}: station_daily without a stations → units map")
        if s.get("fetcher") and s["fetcher"] not in FETCHERS:
            errs.append(f"R5 {sid}: fetcher {s['fetcher']!r} unknown (known: {sorted(FETCHERS)})")
    # R6
    ev = cfg.get("label", {}).get("event")
    if ev not in inst.events:
        errs.append(f"R6 label.event {ev!r} not declared")
    elif inst.events[ev].get("direction") not in ("above", "below"):
        errs.append(f"R6 {ev}: direction {inst.events[ev].get('direction')!r}")
    # R7
    val_start = cfg.get("split", {}).get("val_start")
    for sid, era in (cfg.get("climatology") or {}).items():
        if val_start is not None and int(era[1]) >= int(val_start):
            errs.append(f"R7 {sid}: climatology era ends {era[1]} ≥ val_start {val_start}")
    if errs:
        raise RegistryError("registry check failed:\n  " + "\n  ".join(errs))
