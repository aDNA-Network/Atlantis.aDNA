"""Playbook §B as checks: each trap the S329 discovery arc hit, run against an instance (M-3a).

Every function returns one result, `{"trap", "status", "evidence", "note"}`, with status:
  pass · warn (look at it; nothing is known to be wrong) · fail (a steward must rule: fix it, or accept it in
  candidates.yaml → rulings) · na (does not apply here — `note` always says why).

The traps read the instance's declarations, its cached artifacts (read-only; never written) and, for 1 · 3 · 5, the
answers of a count-only probe (`discover.probe`). Every number they emit is a summary: counts, fractions, ranges.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ORDER = {"pass": 0, "na": 0, "warn": 1, "fail": 2}
TRAPS = ("server_count", "longitude_by_unit", "probe_zero", "samples_per_year", "negative_flow", "surveillance_declared")
DEFAULTS = {"lon_tolerance_deg": 0.5, "lon_gross_deg": 1.0, "lon_max_out_frac": 0.01, "sparse_year_frac": 0.25}


def _result(trap, status, evidence=None, note=""):
    return {"trap": trap, "status": status, "evidence": evidence or {}, "note": note}


def _worst(statuses) -> str:
    s = [x for x in statuses if x]
    if not s:
        return "na"
    if all(x == "na" for x in s):
        return "na"
    return max((x for x in s if x != "na"), key=ORDER.get)


def _summary(inst, sid) -> dict:
    p = inst.stream_spec(sid).get("summary")
    return json.loads(inst.path(p).read_text()) if p and inst.path(p).exists() else {}


def _frame(inst, sid) -> pd.DataFrame | None:
    a = inst.stream_spec(sid).get("artifact")
    return pd.read_parquet(inst.path(a)) if a and inst.path(a).exists() else None


# ── 1. server count ────────────────────────────────────────────────────────────────────────────────────────────────
def server_count(inst, probes: dict | None) -> dict:
    """§B/§A1: the server's own count, asserted against what the instance fetched (and stored, so a re-fetch sees drift)."""
    if probes is None:
        return _result("server_count", "na", note="not probed — re-run with --probe (count-only requests)")
    ev, st = {}, []
    for sid, p in probes.items():
        if p.get("skipped"):
            ev[sid] = {"skipped": p["skipped"]}; st.append("na"); continue
        summ, spec = _summary(inst, sid), inst.stream_spec(sid)
        rows = []
        for a in p["answers"]:
            row = {"what": a["what"], "server": a["n"]}
            if a["broken"]:
                row.update(status="fail", why=f"no count: {a['broken']}")
            elif p["fetcher"] == "ArcGISMapServer":
                name = a["what"].removeprefix("layer ")
                have = (summ.get("per_layer") or {}).get(name, a.get("expected"))
                row.update(fetched=have, status="pass" if have == a["n"] else "fail",
                           why="" if have == a["n"] else "server count ≠ fetched: a re-fetch would differ")
            elif p["fetcher"] in ("ERDDAPGriddap", "CoralReefWatch"):
                rng, lo, hi = a.get("time_range"), summ.get("min_date"), summ.get("max_date")
                ok = bool(rng and lo and hi and rng[0] <= lo[:10] and hi[:10] <= rng[1])
                row.update(server_range=rng, fetched_range=[lo, hi], status="pass" if ok else "fail",
                           why="" if ok else "the server's time axis no longer covers what was fetched")
            elif p["fetcher"] == "NWISDailyValues":
                df, col = _frame(inst, sid), (spec.get("columns") or {}).get("station", "site")
                have = None if df is None else int((df[col].astype(str) == a["what"].removeprefix("site ")).sum())
                row.update(fetched=have, status="pass" if have == a["n"] else ("na" if have is None else "fail"),
                           why="" if have == a["n"] else ("not fetched" if have is None else
                                                          "server day count ≠ fetched: a re-fetch would differ"))
            rows.append(row); st.append(row["status"])
        ev[sid] = rows
    return _result("server_count", _worst(st), ev,
                   "ArcGIS: returnCountOnly per layer vs the fetch summary · ERDDAP: the time axis vs the fetched range · "
                   "NWIS: days served vs days cached, per site")


# ── 2. longitude distribution per unit ─────────────────────────────────────────────────────────────────────────────
def _polygon_bounds(inst) -> dict:
    g = inst.cfg["grid"]
    gj = json.loads(inst.path(g["path"]).read_bytes())
    out = {}
    for f in gj["features"] if gj.get("type") == "FeatureCollection" else [gj]:
        xy = np.array(list(_coords(f["geometry"]["coordinates"])))
        out[str(f["properties"][g["id_property"]])] = [xy[:, 1].min(), xy[:, 1].max(), xy[:, 0].min(), xy[:, 0].max()]
    return out


def _coords(c):
    if isinstance(c[0], (int, float)):
        yield c[:2]
    else:
        for x in c:
            yield from _coords(x)


def _declared_boxes(inst):
    """A rule grid declares no geometry. The only per-unit space it declares is a gridded stream's `boxes`
    ([lat0, lat1, lon0, lon1] per unit). A box is a proxy for the unit, not its boundary — the note says so."""
    for sid in inst.streams:
        b = (inst.stream_spec(sid).get("fetch") or {}).get("boxes")
        if b:
            return {str(k): [float(x) for x in v] for k, v in b.items()}, f"{sid} fetch.boxes"
    return None, None


def _unit_key(u) -> str:
    return str(int(u)) if isinstance(u, float) and u.is_integer() else str(u)


def longitude_by_unit(inst, checks: dict) -> dict:
    """§B: space is assigned by coordinates; then the coordinates are checked per unit. S329's first rule put 11,379
    Atlantic-coast samples into Gulf units. Point streams only: a gridded stream was reduced to its units upstream."""
    from atlantis_core.grid import make_grid
    tol, gross, mx = checks["lon_tolerance_deg"], checks["lon_gross_deg"], checks["lon_max_out_frac"]
    kind = inst.cfg["grid"]["kind"]
    if kind == "polygons":
        bounds, source = _polygon_bounds(inst), "the pinned zone polygons' bounding boxes"
    else:
        bounds, source = _declared_boxes(inst)
    ev, st = {}, []
    for sid in inst.streams:
        spec = inst.stream_spec(sid)
        if spec.get("shape") != "point":
            red = _summary(inst, sid).get("reduction") or {}
            fb = sorted(k for k, z in (red.get("zones") or {}).items() if z.get("fallback"))
            ev[sid] = ({"shape": spec.get("shape"), "reduction_rule": _summary(inst, sid).get("reduction_rule"),
                        "fallback_zones": len(fb), "zones": len(red.get("zones") or {})} if red else
                       {"shape": spec.get("shape"), "assigned_by": "the declared station → unit map" if spec.get("stations")
                        else "the fetch spec's per-unit request"})
            st.append("na"); continue
        df = _frame(inst, sid)
        if df is None:
            ev[sid] = {"skipped": "not fetched"}; st.append("na"); continue
        c = spec["columns"]
        lat, lon = df[c["lat"]].to_numpy(float), df[c["lon"]].to_numpy(float)
        unit = pd.Series(make_grid(inst).assign(lat, lon))
        key = unit.dropna().map(_unit_key)   # a rule grid answers 4.0 where the boxes (and atlantis.yaml) say 4
        per, s_st = {}, []
        for u, idx in key.groupby(key).groups.items():
            la, lo = lat[list(idx)], lon[list(idx)]
            row = {"n": int(len(lo)), "lon_min": round(float(lo.min()), 2), "lon_median": round(float(np.median(lo)), 2),
                   "lon_max": round(float(lo.max()), 2)}
            b = (bounds or {}).get(str(u))
            if b:
                def outside(t):
                    return (lo < b[2] - t) | (lo > b[3] + t) | (la < b[0] - t) | (la > b[1] + t)
                o, og = outside(tol), outside(gross)
                row.update(box=[round(x, 2) for x in b], out_tol=int(o.sum()), out_gross=int(og.sum()),
                           out_gross_frac=round(float(og.mean()), 4))
                s_st.append("fail" if og.mean() > mx else ("warn" if o.any() else "pass"))
            else:
                s_st.append("warn")
            per[str(u)] = row
        n_un = int(unit.isna().sum())
        ev[sid] = {"units": per, "unassigned": n_un, "bounds": source or "none declared",
                   "failing_units": [u for u, s in zip(per, s_st) if s == "fail"]}
        st.append(_worst(s_st + (["warn"] if n_un else [])))
    note = (f"bounds: {source or 'none declared — read the per-unit ranges by eye'}; a point counts as outside beyond "
            f"±{tol}° (warn) and ±{gross}° (fail if > {mx:.0%} of a unit's points). Unassigned points are dropped by "
            f"vitals.build without a count; the count is here.")
    if kind == "rules" and bounds:
        note += " A rule grid's box is a proxy for the unit, not its boundary: a fail asks for a ruling, not a re-grid."
    return _result("longitude_by_unit", _worst(st), ev, note)


# ── 3. probe before believing a zero ───────────────────────────────────────────────────────────────────────────────
def probe_zero(inst, probes: dict | None) -> dict:
    """§B: 'a zero measures your question first.' Every empty or keyless answer was re-asked with a control the
    server must answer; a zero whose control also fails is a broken question, not a zero."""
    if probes is None:
        zeros = {sid: s.get("rows") for sid in inst.streams if (s := _summary(inst, sid)) and s.get("rows") == 0}
        layer0 = {sid: [k for k, v in (s.get("per_layer") or {}).items() if v == 0] for sid in inst.streams
                  if (s := _summary(inst, sid))}
        layer0 = {k: v for k, v in layer0.items() if v}
        if zeros or layer0:
            return _result("probe_zero", "warn", {"zero_rows": zeros, "zero_layers": layer0},
                           "a zero on record, never probed — re-run with --probe")
        return _result("probe_zero", "na", note="not probed — re-run with --probe; no zero on record in the summaries")
    ev, st, n = {}, [], 0
    for sid, p in probes.items():
        for a in p.get("answers", []):
            n += 1
            if a["broken"]:
                ok = bool(a["control"]) and "did not answer" not in a["control"]
                ev.setdefault(sid, []).append({"what": a["what"], "kind": "broken question", "error": a["broken"],
                                               "control": a["control"],
                                               "reading": "the server is up; the question is wrong" if ok else
                                               "the server did not answer the control either"})
                st.append("fail")
            elif a["zero"]:
                real = bool(a["control"]) and "did not answer" not in a["control"]
                ev.setdefault(sid, []).append({"what": a["what"], "kind": "zero", "control": a["control"],
                                               "reading": "a true zero (the control answered)" if real else "a broken question"})
                st.append("warn" if real else "fail")
    if not n:
        return _result("probe_zero", "na", note="no stream had a probe")
    return _result("probe_zero", _worst(st) if st else "pass", ev or {"answers": n, "zero_or_broken": 0},
                   f"{n} probe answers; each zero or failed answer re-asked with a control")


# ── 4. samples per year before min_train_year ──────────────────────────────────────────────────────────────────────
def samples_per_year(inst, checks: dict) -> dict:
    """§B: early decades are sparse. Rows per year (point: samples · unit_daily: unit-days · station_daily: station-days)
    over min_train_year…test_end, against the median year. The event stream decides the status; the others inform."""
    sp, frac = inst.cfg["split"], checks["sparse_year_frac"]
    y0, y1 = int(sp["min_train_year"]), int(sp.get("test_end", sp.get("val_end")))
    ev_sid = inst.event["event_variable_stream"]
    ev, status = {}, "na"
    for sid in inst.streams:
        df = _frame(inst, sid)
        if df is None:
            ev[sid] = {"skipped": "not fetched"}; continue
        years = pd.to_datetime(df[inst.stream_spec(sid)["columns"]["date"]]).dt.year
        counts = years.value_counts().reindex(range(y0, y1 + 1), fill_value=0)
        med = float(counts.median())
        sparse = [int(y) for y, n in counts.items() if n < frac * med]
        ok_from = next((y for y in range(y0, y1 + 1) if all(counts[z] >= frac * med for z in range(y, y1 + 1))), None)
        first = int(years.min())
        ev[sid] = {"years": {int(y): int(n) for y, n in counts.items()}, "median_year": med,
                   "sparse_years": sparse, "first_year_on_record": first,
                   "earliest_min_train_year_with_no_sparse_year": ok_from}
        if sid == ev_sid:
            status = "warn" if sparse else "pass"
    note = (f"a year is sparse below {frac:.0%} of the median year in {y0}–{y1}; min_train_year is {y0}. A warn asks "
            f"whether the sparse years should train — it does not move min_train_year (that is a vitals change, SO-7).")
    if ev_sid not in ev or "skipped" in ev[ev_sid]:
        note = "the event stream is not fetched. " + note
    return _result("samples_per_year", status, ev, note)


# ── 5. negative flow at tidal gauges ───────────────────────────────────────────────────────────────────────────────
def negative_flow(inst, probes: dict | None) -> dict:
    """§B: reverse flow at a tidal gauge is negative. Clip it and say so. The cache is post-clip, so the count of what
    was clipped is known only to a probe; offline this checks that nothing negative survived undeclared."""
    ev, st = {}, []
    for sid, s in inst.streams.items():
        if s.get("fetcher") != "NWISDailyValues":
            continue
        spec = inst.stream_spec(sid)
        clip, val = bool((spec.get("fetch") or {}).get("clip_negative")), spec["columns"]["value"]
        df = _frame(inst, sid)
        cached_neg = None if df is None else int((df[val] < 0).sum())
        row = {"clip_negative": clip, "negatives_in_cache": cached_neg}
        p = (probes or {}).get(sid)
        if p and p.get("answers"):
            row["server_negatives"] = {a["what"]: a.get("negatives") for a in p["answers"]}
            row["server_nodata_sentinels"] = {a["what"]: a.get("nodata_sentinels") for a in p["answers"]}
            neg = sum(v or 0 for v in row["server_negatives"].values())
            sen = sum(v or 0 for v in row["server_nodata_sentinels"].values())
            if sen:
                row["why"] = f"{sen} no-data sentinel value(s) parse as numbers; a clip would read them as zero flow"
                st.append("fail")
            elif neg and not clip:
                row["why"] = f"{neg} negative day(s) served and clip_negative is not declared"; st.append("fail")
            else:
                row["why"] = f"{neg} negative day(s) served; clipped by declaration" if neg else "no negative day served"
                st.append("pass")
        elif cached_neg:
            row["why"] = ("negative values in the cache: declare clip_negative, or keep reverse flow by a ruling "
                          "(candidates.yaml → rulings.negative_flow)")
            st.append("fail")
        else:
            row["why"] = ("clipped by declaration; how many were clipped is not knowable from the clipped cache — --probe"
                          if clip else "no negative value in the cache")
            st.append("na" if clip else "pass")
        ev[sid] = row
    if not ev:
        return _result("negative_flow", "na", note="no gauge stream (NWIS) declared")
    return _result("negative_flow", _worst(st), ev)


# ── 6. surveillance channel declared ───────────────────────────────────────────────────────────────────────────────
def surveillance_declared(inst) -> dict:
    """§B: surveillance is endogenous. Registry R8 is the check (contract item 5); this reports it."""
    from atlantis_core.registry import RegistryError, check
    try:
        check(inst)
        r8 = []
    except RegistryError as e:
        r8 = [l.strip() for l in str(e).splitlines() if l.strip().startswith("R8")]
    surv = inst.cfg.get("surveillance") or {}
    ev = {"declared": surv.get("declared") or "present",
          "streams": sorted(sid for sid, s in inst.streams.items() if s.get("surveillance_channel") is True)}
    if surv.get("reason"):
        ev["reason"] = surv["reason"]
    if r8:
        ev["r8"] = r8
    return _result("surveillance_declared", "fail" if r8 else "pass", ev, "registry R8 (contract item 5)")


def run_all(inst, checks: dict | None = None, probes: dict | None = None) -> list[dict]:
    c = {**DEFAULTS, **(checks or {})}
    return [server_count(inst, probes), longitude_by_unit(inst, c), probe_zero(inst, probes),
            samples_per_year(inst, c), negative_flow(inst, probes), surveillance_declared(inst)]
