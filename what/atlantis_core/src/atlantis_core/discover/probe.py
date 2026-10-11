"""Count-only probes of a stream's source (operator ruling, M-3a 2026-10-10): metadata and counts, read in memory.

Nothing is cached and nothing but summary numbers leaves this module: no artifact, no observation, no reply body. A probe
answers three questions per source:
  · what does the server count? (§B trap 1 — the count a fetch must assert)
  · is a zero a zero? (§B trap 3 — an empty answer is re-asked with a control the server must answer)
  · how much reverse flow is there before the clip? (§B trap 5 — NWIS only; the cached artifact is already clipped)

`Probe(session=…)` takes any object with `.get(url, params=None, timeout=None)`, as the fetchers do; tests pass fakes.
"""
from __future__ import annotations

import sys
from collections import Counter
from urllib.parse import urlsplit

import pandas as pd

NWIS_DV = "https://waterservices.usgs.gov/nwis/dv/"
NWIS_SITE = "https://waterservices.usgs.gov/nwis/site/"


class Probe:
    def __init__(self, session=None, timeout: int = 60, retries: int = 2):
        self._session, self.timeout, self.retries = session, timeout, retries
        self.hosts: Counter = Counter()   # host → requests made; the memo's record of what was touched

    def _http(self):
        if self._session is None:
            import requests
            self._session = requests.Session()
        return self._session

    def get(self, url, params=None):
        """→ (status_code, response) or (None, error string). Never raises: an unreachable source is an answer."""
        self.hosts[urlsplit(url).netloc] += 1
        err = None
        for _ in range(self.retries):
            try:
                r = self._http().get(url, params=params, timeout=self.timeout)
                return r.status_code, r
            except Exception as e:  # noqa: BLE001
                err = f"{type(e).__name__}: {str(e)[:160]}"
                print(f"  probe retry {url[:80]}: {err}", file=sys.stderr)
        return None, err

    def json(self, url, params=None):
        code, r = self.get(url, params)
        if code is None:
            return None, r
        if code >= 400:
            return None, f"HTTP {code}"
        try:
            return r.json(), None
        except Exception as e:  # noqa: BLE001
            return None, f"not JSON: {type(e).__name__}"


def _answer(what, n, *, broken=None, control=None, **kw):
    """One probe answer. `n` None = no count obtained. `zero` = the server said 0/empty. `broken` = the question failed
    (no such key, an error, unreachable) — never read as a zero. `control` = what the control query said, when one ran."""
    return {"what": what, "n": n, "zero": n == 0, "broken": broken, "control": control, **kw}


# ── ArcGIS MapServer ────────────────────────────────────────────────────────────────────────────────────────────────
def arcgis(spec: dict, P: Probe) -> list[dict]:
    out = []
    for l in spec["layers"]:
        url = spec["url_template"].format(name=l["name"], layer=l["layer"])
        j, err = P.json(url, {"where": "1=1", "returnCountOnly": "true", "f": "json"})
        if j is not None and "error" in j:
            j, err = None, f"server error {str(j['error'])[:120]}"
        if j is not None and "count" not in j:   # the S329 trap: a reply without the key you asked for is not a zero
            j, err = None, f"reply has no `count` key (keys: {sorted(j)[:6]})"
        n = None if j is None else int(j["count"])
        a = _answer(f"layer {l['name']}", n, broken=err, expected=l.get("expected"))
        if n == 0 or n is None:
            meta, merr = P.json(url.rsplit("/query", 1)[0], {"f": "json"})
            a["control"] = (f"layer metadata answered (name {meta.get('name')!r})" if meta and "name" in meta
                            else f"layer metadata did not answer ({merr or 'no name'})")
        out.append(a)
    return out


# ── ERDDAP griddap (and Coral Reef Watch, which is one) ────────────────────────────────────────────────────────────
def _erddap_root_and_id(base: str) -> tuple[str, str]:
    head, tail = base.split("/griddap/", 1)
    return head, tail.rsplit(".", 1)[0]


def erddap(spec: dict, P: Probe) -> list[dict]:
    root, dsid = _erddap_root_and_id(spec["base"])
    j, err = P.json(f"{root}/info/{dsid}/index.json")
    n, rng = None, None
    if j is not None:
        try:
            cols = j["table"]["columnNames"]
            rows = [dict(zip(cols, r)) for r in j["table"]["rows"]]
            for r in rows:
                if r.get("Row Type") == "dimension" and r.get("Variable Name") == "time":
                    n = int(str(r.get("Value", "")).split("nValues=")[1].split(",")[0])
                if r.get("Variable Name") == "time" and r.get("Attribute Name") == "actual_range":
                    lo, hi = (float(x) for x in str(r["Value"]).split(","))
                    rng = [str(pd.to_datetime(lo, unit="s").date()), str(pd.to_datetime(hi, unit="s").date())]
        except (KeyError, IndexError, ValueError) as e:
            err = f"info table unreadable: {type(e).__name__}"
        if n is None and err is None:
            err = "info has no time dimension nValues"
    a = _answer(f"dataset {dsid} time steps", n, broken=err, time_range=rng)
    if n == 0 or n is None:
        code, r = P.get(f"{root}/version")
        a["control"] = (f"server answered /version ({r.text.strip()[:40]})" if code == 200
                        else f"server did not answer /version ({code or r})")
    return [a]


# ── USGS NWIS daily values ──────────────────────────────────────────────────────────────────────────────────────────
def nwis(spec: dict, P: Probe) -> list[dict]:
    out = []
    for site in spec["sites"]:
        j, err = P.json(NWIS_DV, {"format": "json", "sites": site, "parameterCd": spec["parameter"],
                                  "startDT": spec["start"], "endDT": spec["end"], "siteStatus": "all"})
        n = neg = sentinel = None
        if j is not None:
            try:
                ts = j["value"]["timeSeries"]
                if not ts:
                    n = 0
                else:
                    nodata = ts[0].get("variable", {}).get("noDataValue")
                    v = pd.to_numeric(pd.Series([x["value"] for x in ts[0]["values"][0]["value"]]), errors="coerce").dropna()
                    sentinel = int((v == nodata).sum()) if nodata is not None else 0
                    real = v[v != nodata] if nodata is not None else v
                    n, neg = int(len(v)), int((real < 0).sum())
            except (KeyError, IndexError, TypeError) as e:
                err = f"reply shape unexpected: {type(e).__name__}"
        a = _answer(f"site {site}", n, broken=err, negatives=neg, nodata_sentinels=sentinel)
        if n == 0 or n is None:
            code, r = P.get(NWIS_SITE, {"format": "rdb", "sites": site})
            a["control"] = (f"site service knows {site}" if code == 200 and str(site) in r.text
                            else f"site service did not answer for {site} ({code or r})")
        out.append(a)
    return out


PROBES = {"ArcGISMapServer": arcgis, "ERDDAPGriddap": erddap, "CoralReefWatch": erddap, "NWISDailyValues": nwis}


def probe_stream(inst, sid: str, P: Probe) -> dict:
    """Probe one declared stream from its own fetch spec. A fetcher with no probe, or a stream with no spec, says so."""
    s, spec = inst.streams[sid], (inst.stream_spec(sid).get("fetch") or {})
    fn = PROBES.get(s.get("fetcher"))
    if fn is None or not spec:
        return {"stream_id": sid, "fetcher": s.get("fetcher"), "answers": [],
                "skipped": "no fetch spec yet" if not spec else f"no probe for fetcher {s.get('fetcher')!r}"}
    return {"stream_id": sid, "fetcher": s.get("fetcher"), "answers": fn(spec, P)}
