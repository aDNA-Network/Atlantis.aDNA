"""NDBCStdmet (M-3b-ii-a, WI-19) and the calm-day grammar op `weekly_count_lt`. Offline: a fake session serves gzipped
yearly files in each of NDBC's three header forms; the socket guard fails any real connection."""
import gzip, json, shutil, socket

import numpy as np
import pandas as pd
import pytest
import yaml

from atlantis_core import load_instance
from atlantis_core.fetch import FETCHERS, BUILT, OfflineError
from atlantis_core.fetch.ndbc import NDBCStdmet, parse_stdmet
from atlantis_core.grid import week_start
from atlantis_core.vitals import grammar, ops


@pytest.fixture(autouse=True)
def no_sockets(monkeypatch):
    def refuse(*a, **k): raise AssertionError("a test opened a socket")
    monkeypatch.setattr(socket.socket, "connect", refuse)


# ── three header forms, as NDBC writes them ──────────────────────────────────────────────────────────────────────────
def pre1999(year, hours, wspd):
    """YY MM DD hh — two-digit year, no minute, hourly."""
    head = "YY MM DD hh WD   WSPD GST  WVHT  DPD   APD  MWD  BAR    ATMP  WTMP  DEWP  VIS"
    rows = [f"{t.year % 100:02d} {t.month:02d} {t.day:02d} {t.hour:02d} 159 {w:04.1f} 05.4 99.00 99.00 99.00 999 1018.9  24.4  23.2 999.0 99.0"
            for t, w in zip(hours, wspd)]
    return "\n".join([head, *rows]) + "\n"


def y1999(year, hours, wspd):
    """YYYY MM DD hh — four-digit year, no minute."""
    head = "YYYY MM DD hh WD  WSPD GST  WVHT  DPD   APD  MWD  BAR    ATMP  WTMP  DEWP  VIS"
    rows = [f"{t.year} {t.month:02d} {t.day:02d} {t.hour:02d} 159 {w:4.1f} 05.4 99.00 99.00 99.00 999 1018.9  24.4  23.2 999.0 99.0"
            for t, w in zip(hours, wspd)]
    return "\n".join([head, *rows]) + "\n"


def y2005(year, times, wspd):
    """#YY … mm + a units line — the 2005-on form, any sampling (10-minute rows here)."""
    head = "#YY  MM DD hh mm WDIR WSPD GST  WVHT   DPD   APD MWD   PRES  ATMP  WTMP  DEWP  VIS  TIDE"
    units = "#yr  mo dy hr mn degT m/s  m/s     m   sec   sec degT   hPa  degC  degC  degC   mi    ft"
    rows = [f"{t.year} {t.month:02d} {t.day:02d} {t.hour:02d} {t.minute:02d}  31 {w:4.1f}  4.5 99.00 99.00 99.00 999 1023.4  18.9 999.0  12.1 99.0 99.00"
            for t, w in zip(times, wspd)]
    return "\n".join([head, units, *rows]) + "\n"


def hours_of(day, n, start=0):
    return list(pd.date_range(pd.Timestamp(day) + pd.Timedelta(hours=start), periods=n, freq="h"))


class Resp:
    def __init__(self, status, content=b""):
        self.status_code, self.content = status, content
    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeNDBC:
    """name → text (served gzipped); anything else is a 404. `fail` names files that answer 500."""
    def __init__(self, files, fail=()):
        self.files, self.fail, self.calls = files, set(fail), []
    def get(self, url, params=None, timeout=None):
        name = url.rsplit("/", 1)[-1]
        self.calls.append(name)
        if name in self.fail:
            return Resp(500)
        if name not in self.files:
            return Resp(404)
        return Resp(200, gzip.compress(self.files[name].encode()))


class Boom:
    def get(self, *a, **k): raise AssertionError("network touched")


def ndbc(tmp_path, session, **kw):
    return NDBCStdmet(tmp_path, "wind.parquet", "wind_fetch_summary.json", session=session, retries=1, backoff=0.0, **kw)


SPEC = {"stations": ["AAAF1", "BBBF1"], "years": [1998, 2006], "variable": "WSPD", "min_hours": 18}


def two_station_files():
    return {
        # AAAF1: 1998 (pre-1999 form) and 2006 (10-minute form); 1999–2005 absent (404)
        "aaaf1h1998.txt.gz": pre1999(1998, hours_of("1998-07-01", 24), [3.0] * 23 + [99.0])          # a sentinel hour
                             + "\n".join(pre1999(1998, hours_of("1998-07-02", 17), [5.0] * 17).splitlines()[1:]) + "\n",
        "aaaf1h2006.txt.gz": y2005(2006, list(pd.date_range("2006-07-01", periods=24 * 6, freq="10min")),
                                   [2.0, 4.0] * 72),
        # BBBF1: 1999 (four-digit form) only
        "bbbf1h1999.txt.gz": y1999(1999, hours_of("1999-07-01", 24), [6.0] * 24),
    }


# ── the registry of fetchers ─────────────────────────────────────────────────────────────────────────────────────────
def test_ndbc_is_built():
    assert "NDBCStdmet" in BUILT and FETCHERS["NDBCStdmet"] is NDBCStdmet
    assert NDBCStdmet.daily and set(NDBCStdmet.spec_required) == {"stations", "years", "variable"}


# ── parsing ──────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("form", [pre1999, y1999, y2005])
def test_parse_each_header_form(form):
    t = hours_of("1998-07-01" if form is pre1999 else "2006-07-01", 3)
    txt = form(t[0].year, t, [4.2, 99.0, 0.0])
    df = parse_stdmet(gzip.compress(txt.encode()), "WSPD", where="x")
    assert list(df["time"]) == t                                     # two-digit year → 19xx; no minute column → :00
    assert df["v"].iloc[0] == pytest.approx(4.2) and np.isnan(df["v"].iloc[1]) and df["v"].iloc[2] == 0.0   # 99 → NaN; 0 stays


def test_parse_takes_rows_shorter_than_their_header_and_counts_the_malformed():
    """LONF1 2000 (found live at the M-3b-ii-a fetch): a 17-column header naming TIDE, rows of 16 and 17 fields."""
    txt = ("YYYY MM DD hh WD   WSPD GST  WVHT  DPD   APD  MWD  BAR    ATMP  WTMP  DEWP  VIS  TIDE\n"
           "2000 01 01 14  37  2.3  2.6 99.00 99.00 99.00 999 1022.5  21.0  20.4 999.0 99.0\n"
           "2000 01 01 15  70  2.6  2.9 99.00 99.00 99.00 999 1023.2  21.2  20.4 999.0 99.0 99.00\n"
           "2000 01 01 16  70\n"                                                   # too short to hold WSPD
           "2000 13 01 17  70  2.6  2.9 99.00 99.00 99.00 999 1023.2  21.2  20.4 999.0 99.0\n")   # month 13
    df = parse_stdmet(txt.encode(), "WSPD", where="x")
    assert list(df["v"]) == [2.3, 2.6] and df.attrs["malformed"] == 2


def test_parse_refuses_a_header_without_the_variable():
    with pytest.raises(ValueError, match="lacks"):
        parse_stdmet(b"YY MM DD hh WD GST\n90 01 01 00 159 05.4\n", "WSPD", where="x")
    with pytest.raises(ValueError, match="not a readable"):
        parse_stdmet(b"\x1f\x8bnot gzip", "WSPD", where="x")


# ── the download and its reduction ───────────────────────────────────────────────────────────────────────────────────
def test_download_reduces_to_daily_and_records_absent_years(tmp_path):
    f = ndbc(tmp_path, FakeNDBC(two_station_files()))
    df = f.fetch(SPEC)
    assert list(df.columns) == ["date", "station", "wspd", "n_hours"]
    a = df[df["station"] == "AAAF1"].set_index("date")
    # 1998-07-01: 23 valid hours of 3.0 (the sentinel hour dropped) → kept; 1998-07-02: 17 hours < 18 → dropped
    assert a.loc["1998-07-01", "wspd"] == pytest.approx(3.0) and a.loc["1998-07-01", "n_hours"] == 23
    assert pd.Timestamp("1998-07-02") not in a.index
    # 2006-07-01: 144 ten-minute rows alternating 2 and 4 → the day's mean over every observation, 24 distinct hours
    assert a.loc["2006-07-01", "wspd"] == pytest.approx(3.0) and a.loc["2006-07-01", "n_hours"] == 24
    s = json.loads((tmp_path / "wind_fetch_summary.json").read_text())
    red = s["reduction"]
    assert red["day_boundary"] == "UTC" and red["min_hours"] == 18 and red["stations"] == ["AAAF1", "BBBF1"]
    sa, sb = red["per_station"]["AAAF1"], red["per_station"]["BBBF1"]
    assert sa["years_present"] == [1998, 2006] and sa["years_absent"] == list(range(1999, 2006))
    assert sa["days_short"] == 1 and sa["days_kept"] == 2 and sa["n_obs_missing"] == 1 and sa["rows_malformed"] == 0
    assert sb["years_present"] == [1999] and sb["days_kept"] == 1
    assert s["completeness"]["dates_per_unit"] == {"min": 1, "max": 2}      # per station: the verify note can see a gap


def test_duplicate_timestamps_across_year_files_count_once(tmp_path):
    files = {"aaaf1h2006.txt.gz": y2005(2006, hours_of("2006-12-31", 24) + hours_of("2007-01-01", 1), [4.0] * 25),
             "aaaf1h2007.txt.gz": y2005(2007, hours_of("2007-01-01", 24), [8.0] * 24)}
    f = ndbc(tmp_path, FakeNDBC(files))
    df = f.fetch({"stations": ["AAAF1"], "years": [2006, 2007], "variable": "WSPD", "min_hours": 18}).set_index("date")
    assert f.reduction["per_station"]["AAAF1"]["duplicates"] == 1
    assert df.loc["2007-01-01", "wspd"] == pytest.approx(4.0 / 24 + 8.0 * 23 / 24)   # the first file's row kept, once


def test_a_station_with_no_year_present_is_refused(tmp_path):
    f = ndbc(tmp_path, FakeNDBC(two_station_files()))
    with pytest.raises(ValueError, match="no stdmet year file"):
        f.fetch({**SPEC, "stations": ["AAAF1", "ZZZF1"]})
    assert not (tmp_path / "wind.parquet").exists()


def test_a_non_404_failure_fails_closed(tmp_path):
    f = ndbc(tmp_path, FakeNDBC(two_station_files(), fail={"aaaf1h2006.txt.gz"}))
    with pytest.raises(RuntimeError, match="gave up"):
        f.fetch(SPEC)
    assert not (tmp_path / "wind.parquet").exists()


def test_offline_and_cache(tmp_path):
    with pytest.raises(OfflineError):
        NDBCStdmet(tmp_path, "wind.parquet", "wind_fetch_summary.json", offline=True, session=Boom()).fetch(SPEC)
    fake = FakeNDBC(two_station_files())
    first = ndbc(tmp_path, fake).fetch(SPEC)
    n_calls = len(fake.calls)
    assert n_calls == 2 * 9                                            # every station-year asked once, 404s included
    again = NDBCStdmet(tmp_path, "wind.parquet", "wind_fetch_summary.json", session=Boom()).fetch(SPEC)
    pd.testing.assert_frame_equal(first, again)                        # the artifact is the cache hit
    (tmp_path / "wind.parquet").unlink(); (tmp_path / "wind_fetch_summary.json").unlink()
    rebuilt = NDBCStdmet(tmp_path, "wind.parquet", "wind_fetch_summary.json", session=Boom()).fetch(SPEC)
    pd.testing.assert_frame_equal(first, rebuilt)                      # the raw cache (404s as zero-byte files) re-reduces offline


def test_a_cached_artifact_on_another_basis_is_refused(tmp_path):
    ndbc(tmp_path, FakeNDBC(two_station_files())).fetch(SPEC)
    f = NDBCStdmet(tmp_path, "wind.parquet", "wind_fetch_summary.json", session=Boom())
    assert f.provenance_problem(SPEC) is None
    for k, v in (("min_hours", 12), ("years", [1998, 2007]), ("stations", ["AAAF1"]), ("variable", "GST")):
        with pytest.raises(ValueError, match=f"different basis.*{k}"):
            f.fetch({**SPEC, k: v})


def test_bind_refuses_a_mapped_station_the_spec_does_not_fetch(tmp_path):
    class Inst:
        def stream_spec(self, sid):
            return {"columns": {"date": "date", "value": "wspd", "station": "station"},
                    "stations": {"AAAF1": [1], "BBBF1": [1], "CCCF1": [2]}}
    f = ndbc(tmp_path, FakeNDBC(two_station_files()))
    f.bind(Inst(), "s")
    with pytest.raises(ValueError, match=r"\['CCCF1'\] are mapped"):
        f.fetch(SPEC)


# ── the calm-day op ──────────────────────────────────────────────────────────────────────────────────────────────────
def test_grammar_takes_weekly_count_lt_with_a_constant():
    node = grammar.parse("weekly_count_lt(value, calm_threshold)", constants=["calm_threshold"], where="t")
    assert grammar.functions_used(node) == {"weekly_count_lt"}
    with pytest.raises(grammar.TransformError, match="takes 2"):
        grammar.parse("weekly_count_lt(value)", where="t")


def _ev(data, stations=None, shape="station_daily"):
    days = pd.to_datetime(data["date"])
    wk = week_start(days)
    weekly = pd.date_range(wk.min(), wk.max() + pd.Timedelta(weeks=1), freq="7D")
    return ops.Evaluator("s", data, shape, weekly, [1, 2], {"c": 4.0}, stations=stations)


def test_weekly_count_lt_counts_on_the_unit_value_and_an_empty_week_is_nan():
    mon = pd.Timestamp("2024-07-01")                                   # a Monday
    d = [(mon + pd.Timedelta(days=i), st, v) for i, (a, b) in enumerate([(3, 5), (3, 3), (1, 9), (5, 5)]) for st, v in (("A", a), ("B", b))]
    d += [(mon + pd.Timedelta(days=4), "C", 2.0)]                       # unit 2's only station, one day in week 1
    nxt = mon + pd.Timedelta(weeks=1)
    d += [(nxt + pd.Timedelta(days=2), "A", 6.0)]                       # week 2: unit 1 observed once (not calm); unit 2 never
    data = pd.DataFrame(d, columns=["date", "station", "value"])
    ev = _ev(data, stations={"A": [1], "B": [1], "C": [2]})
    out = ev.weekly(grammar.parse("weekly_count_lt(value, c)", constants=["c"], where="t"))
    # unit 1, week 1: daily unit means 4, 3, 5, 5 → one day < 4 (per station it would have counted 3 + 1 = 4 rows)
    assert out.loc[mon, 1] == 1.0
    # unit 2, week 1: one observed day, 2 < 4 → 1
    assert out.loc[mon, 2] == 1.0
    # week 2 lies inside the data's span: unit 1 observed, no calm day → 0; unit 2 has no observation → NaN, not 0
    assert out.loc[nxt, 1] == 0.0 and np.isnan(out.loc[nxt, 2])
    assert np.isnan(out.loc[nxt + pd.Timedelta(weeks=1), 1])             # past the data: NaN


def test_weekly_count_lt_refuses_a_series_threshold():
    mon = pd.Timestamp("2024-07-01")
    data = pd.DataFrame({"date": [mon], "station": ["A"], "value": [1.0]})
    ev = _ev(data, stations={"A": [1, 2]})
    with pytest.raises(TypeError, match="constant or a literal"):
        ev.weekly(grammar.parse("weekly_count_lt(value, value)", where="t"))


# ── the self-test sees a calm-day vital that reads the future ────────────────────────────────────────────────────────
def _with_calm_vital(src, dst):
    shutil.copytree(src, dst)
    inst = load_instance(dst)
    sid = next(s for s in inst.streams if inst.stream_spec(s)["shape"] == "station_daily")
    feats = yaml.safe_load((dst / "features.yaml").read_text())
    feats["vitals"].append({"vital_id": "atl_vital_calm_count_t0", "name": "calm days", "description": "test",
                            "stream_ref": sid, "transform": "weekly_count_lt(value, 1000)", "lag": 0,
                            "group": "test", "tag": "proxy"})
    (dst / "features.yaml").write_text(yaml.safe_dump(feats, sort_keys=False))
    return load_instance(dst)


def test_selftest_passes_with_a_calm_vital_and_catches_a_future_read(variant_master, tmp_path, monkeypatch):
    from atlantis_core import selftest as st
    inst = _with_calm_vital(variant_master, tmp_path / "inst")
    st.run(inst, verbose=False)                                       # synthetic station values straddle 1000
    orig = ops.Evaluator.f_weekly_count_lt
    monkeypatch.setattr(ops.Evaluator, "f_weekly_count_lt",
                        lambda self, x, thr, window=None: ops.Weekly(orig(self, x, thr).df.shift(-1)))   # next week's count
    with pytest.raises(st.LeakError):
        st.run(inst, verbose=False)
