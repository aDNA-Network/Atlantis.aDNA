"""Cross-reference checks on an instance's registries — what linkml-validate cannot see.

`linkml-validate -C AtlDocument` proves each registry FILE has the `atl_v0` shape (closed classes, enums, the lever
rule). It cannot see across files or into the transform grammar. This does:

  R1  ids unique within their kind (stream · vital · event)
  R2  every vital's stream_ref and every event's event_variable_stream names a declared stream
  R3  every transform parses under the grammar; windowed ops ⇔ a `window` slot; lag an int ≥ 0, window an int ≥ 1
      (re-asserted: load_instance does not run linkml-validate)
  R4  a lever vital names a non-blank owner (re-asserted: the schema rule's null hole was M-1c's Finding 1)
  R5  every declared stream has an engine spec in atlantis.yaml (shape · columns · artifact) and a known shape;
      a station-keyed stream maps its stations to units; `fetcher` (if set) names a known fetcher class
  R6  `label.event` names a declared event; its direction is above | below; the label signal aggregates the right way
      (`below` with weekly_max, or `above` with weekly_min, means "a week whose max ≤ thr" — rejected)
  R7  every climatology era ends before validation starts (a training-era normal must not reach val/test weeks), and
      before the first rolling-origin TEST year — unless `climatology_policy.rolling_origin: refit_per_fold` is declared,
      which is an obligation on eval (M-1b-ii) recorded in `inst.obligations`, not a waiver
  R8  the surveillance channel is declared or declared absent (contract item 5, T5; M-1d-i). Present: a stream with
      `surveillance_channel: true`, a vital in `group: surveillance` that reads one, and an `eval.ablations` entry dropping
      that group. Absent: `atlantis.yaml → surveillance: {declared: absent, reason: <non-blank>}`, and then no stream claims
      the channel, no vital sits in the group, and eval names no surveillance ablation or surveillance-only comparator

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
    for v in inst.vitals:
        for slot, lo in (("lag", 0), ("window", 1)):
            x = v.get(slot)
            if x is not None and (isinstance(x, bool) or not isinstance(x, int) or x < lo):
                errs.append(f"R3 {v['vital_id']}: {slot} must be an int ≥ {lo}, got {x!r}")
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
    else:
        d = inst.events[ev]["direction"]
        try:
            used = grammar.functions_used(grammar.parse(cfg["label"]["signal"], consts, "label.signal"))
            wrong = "weekly_max" if d == "below" else "weekly_min"
            if wrong in used:
                errs.append(f"R6 {ev}: direction {d} with a {wrong} signal — the event would be judged on the wrong tail")
        except (KeyError, grammar.TransformError) as ex:
            errs.append(f"R6 label.signal: {ex}")
    # R7
    split = cfg.get("split", {})
    val_start = split.get("val_start")
    ro = split.get("rolling_origin_years") or []
    refit = (cfg.get("climatology_policy") or {}).get("rolling_origin") == "refit_per_fold"
    inst.obligations = []
    for sid, era in (cfg.get("climatology") or {}).items():
        if val_start is not None and int(era[1]) >= int(val_start):
            errs.append(f"R7 {sid}: climatology era ends {era[1]} ≥ val_start {val_start}")
        if ro and int(era[1]) >= min(ro) + 1:
            hit = [y + 1 for y in ro if y + 1 <= int(era[1])]
            if refit:
                inst.obligations.append(f"eval must refit the {sid} climatology per rolling-origin fold "
                                        f"(era ends {era[1]}; folds testing {hit} would otherwise see their own year)")
            else:
                errs.append(f"R7 {sid}: era ends {era[1]} but rolling-origin folds test {hit} — declare "
                            f"climatology_policy.rolling_origin: refit_per_fold, or end the era earlier")
    # R8
    surv = cfg.get("surveillance") or {}
    s_streams = sorted(sid for sid, s in inst.streams.items() if s.get("surveillance_channel") is True)
    s_vitals = [v for v in inst.vitals if v.get("group") == "surveillance"]
    ev_cfg = cfg.get("eval") or {}
    s_ablation = any(a.get("drop_group") == "surveillance" for a in ev_cfg.get("ablations", []) or [])
    if surv.get("declared") not in (None, "absent", "present"):
        errs.append(f"R8 surveillance.declared {surv.get('declared')!r} is not absent | present")
    elif surv.get("declared") == "absent":
        if not (isinstance(surv.get("reason"), str) and surv["reason"].strip()):
            errs.append("R8 surveillance declared absent without a non-blank reason")
        if s_streams:
            errs.append(f"R8 surveillance declared absent, but {s_streams} declare surveillance_channel: true")
        if s_vitals:
            errs.append(f"R8 surveillance declared absent, but {[v['vital_id'] for v in s_vitals]} sit in group surveillance")
        if s_ablation or ev_cfg.get("surveillance_only"):
            errs.append("R8 surveillance declared absent, but eval names a surveillance ablation or surveillance_only comparator")
    else:
        if not s_streams:
            errs.append("R8 no stream declares surveillance_channel: true — declare one, or set "
                        "atlantis.yaml → surveillance: {declared: absent, reason: …}")
        elif not any(v.get("stream_ref") in s_streams for v in s_vitals):
            errs.append(f"R8 {s_streams} declare the surveillance channel, but no vital in group surveillance reads them")
        if s_streams and not s_ablation:
            errs.append("R8 a surveillance channel is declared, so eval.ablations must drop the surveillance group (T5)")
    if errs:
        raise RegistryError("registry check failed:\n  " + "\n  ".join(errs))
