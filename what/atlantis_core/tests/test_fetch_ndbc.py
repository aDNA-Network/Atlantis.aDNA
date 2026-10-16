"""NDBCStdmet (M-3b-ii-a, WI-19) and the calm-day grammar op `weekly_count_lt`. Offline: a fake session serves gzipped
yearly files in each of NDBC's four header forms (the 2005–06 one further down); the socket guard fails any real connection."""
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


# ── header forms, as NDBC writes them ──────────────────────────────────────────────────────────────────────────
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
    assert list(df.columns) == ["date", "station", "wspd", "n_hours", "qc_low_ratio", "qc_stuck", "qc_low_ratio_causal"]
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
    assert sa["cadence"]["1998"]["rows_per_day_median"] == 20.5 and sa["cadence"]["2006"]["minutes"] == [0, 10, 20, 30, 40, 50]
    assert set(red["raw_files"]["AAAF1"]) == {"1998", "2006"} and len(red["raw_files"]["AAAF1"]["1998"]["sha256"]) == 64
    assert sorted(sa["absent_confirmed_at"]) == [str(y) for y in range(1999, 2006)]
    assert sb["years_present"] == [1999] and sb["days_kept"] == 1
    assert s["completeness"]["dates_per_unit"] == {"min": 1, "max": 2}      # per station: the verify note can see a gap


def test_duplicate_timestamps_identical_kept_once_conflicting_dropped(tmp_path):
    """III F-2: SMKF1 2020 holds a second block that is LONF1's record. Disagreeing copies are not resolved by file order."""
    files = {"aaaf1h2006.txt.gz": y2005(2006, hours_of("2006-12-31", 24) + hours_of("2007-01-01", 2), [4.0] * 25 + [8.0]),
             "aaaf1h2007.txt.gz": y2005(2007, hours_of("2007-01-01", 24) + hours_of("2007-01-02", 3), [8.0] * 27)}
    f = ndbc(tmp_path, FakeNDBC(files))
    df = f.fetch({"stations": ["AAAF1"], "years": [2006, 2007], "variable": "WSPD", "min_hours": 18}).set_index("date")
    ps = f.reduction["per_station"]["AAAF1"]
    # 2007-01-01 00:00 is 4.0 in one file, 8.0 in the other → dropped; 01:00 is 8.0 in both → kept once
    assert ps["duplicates_conflicting"] == 1 and ps["conflicting_span"] == ["2007-01-01 00:00:00"] * 2
    assert ps["duplicates_identical"] == 1
    assert df.loc["2007-01-01", "wspd"] == pytest.approx(8.0) and df.loc["2007-01-01", "n_hours"] == 23
    within = {"aaaf1h2006.txt.gz": y2005(2006, hours_of("2006-07-01", 24) + hours_of("2006-07-01", 24, 0), [4.0] * 24 + [1.0] * 24)}
    g = ndbc(tmp_path / "w", FakeNDBC(within))
    out = g.fetch({"stations": ["AAAF1"], "years": [2006, 2006], "variable": "WSPD"})
    assert len(out) == 0                                               # a whole day of conflicts keeps nothing
    assert g.reduction["per_station"]["AAAF1"]["duplicates_conflicting"] == 24


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
    assert len(fake.calls) == 3 + 2 * 15                               # 3 files once; each of 15 absent years asked twice
    again = NDBCStdmet(tmp_path, "wind.parquet", "wind_fetch_summary.json", session=Boom()).fetch(SPEC)
    pd.testing.assert_frame_equal(first, again)                        # the artifact is the cache hit
    (tmp_path / "wind.parquet").unlink(); (tmp_path / "wind_fetch_summary.json").unlink()
    rebuilt = NDBCStdmet(tmp_path, "wind.parquet", "wind_fetch_summary.json", session=Boom()).fetch(SPEC)
    pd.testing.assert_frame_equal(first, rebuilt)                      # the raw cache (+ absence sidecars) re-reduces offline
    s = json.loads((tmp_path / "wind_fetch_summary.json").read_text())
    assert s["fetched_at_source"].startswith("offline re-reduction") and s["reduction"]["requests"] == 0   # III F-6


def test_a_cached_artifact_on_another_basis_is_refused(tmp_path):
    ndbc(tmp_path, FakeNDBC(two_station_files())).fetch(SPEC)
    f = NDBCStdmet(tmp_path, "wind.parquet", "wind_fetch_summary.json", session=Boom())
    assert f.provenance_problem(SPEC) is None
    for k, v in (("min_hours", 12), ("years", [1998, 2007]), ("stations", ["AAAF1"]), ("variable", "GST"),
                 ("qc", {"low_ratio": 0.3})):
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


# ── QC flags (III F-1; operator ruling 8): a failed anemometer reads as calm, a stuck one repeats ──────────────────────
def _three_lights(days=60, faulty=None, stuck=None, factor=0.2):
    """Three stations, hourly, 2006-07-01 on. `faulty`: (station, first day, n days) read at 0.2 ×. `stuck`: (station,
    day, n hours) read 0.0 from 00:00."""
    files = {}
    for st, level in (("AAAF1", 6.0), ("BBBF1", 5.0), ("CCCF1", 7.0)):
        t = list(pd.date_range("2006-07-01", periods=24 * days, freq="h"))
        v = [level + (i % 5) * 0.1 for i in range(len(t))]                      # never repeats for 6 h on its own
        if faulty and faulty[0] == st:
            for i, x in enumerate(t):
                if 0 <= (x.normalize() - pd.Timestamp("2006-07-01")).days - faulty[1] < faulty[2]:
                    v[i] *= factor
        if stuck and stuck[0] == st:
            i0 = (pd.Timestamp(stuck[1]) - pd.Timestamp("2006-07-01")).days * 24
            for i in range(i0, i0 + stuck[2]):
                v[i] = 0.0
        files[f"{st.lower()}h2006.txt.gz"] = y2005(2006, t, v)
    return files


QC_SPEC = {"stations": ["AAAF1", "BBBF1", "CCCF1"], "years": [2006, 2006], "variable": "WSPD", "min_hours": 18}


def test_qc_flags_a_station_reading_far_below_the_others_and_deletes_nothing(tmp_path):
    f = ndbc(tmp_path, FakeNDBC(_three_lights(faulty=("AAAF1", 20, 25))))
    df = f.fetch(QC_SPEC)
    a = df[df["station"] == "AAAF1"].set_index("date")
    fault = pd.date_range("2006-07-21", periods=25)
    assert a.loc[fault[3]:fault[-4], "qc_low_ratio"].all()                 # inside the fault (the window's edges aside)
    assert not a.loc[:"2006-07-12", "qc_low_ratio"].any() and not a.loc["2006-08-24":, "qc_low_ratio"].any()
    assert len(a) == 60 and a.loc[fault[10], "wspd"] < 2                   # flagged, never removed
    assert not df[df["station"] != "AAAF1"]["qc_low_ratio"].any()          # the others are not blamed
    assert f.reduction["per_station"]["AAAF1"]["days_flagged"]["qc_low_ratio"] >= 19
    clean = ndbc(tmp_path / "c", FakeNDBC(_three_lights())).fetch(QC_SPEC)
    assert not clean["qc_low_ratio"].any() and not clean["qc_stuck"].any()


def test_qc_ratio_is_against_the_OTHER_stations(tmp_path):
    """Two lights, one at 0.3 ×: against the other it is 0.3 (flagged); against a median that includes itself it would
    be ≈ 0.46 and pass. With two lights reporting (47% of FKNMS test days) that difference is the whole check."""
    files = {k: v for k, v in _three_lights(faulty=("AAAF1", 20, 25)).items() if not k.startswith("cccf1")}
    files["aaaf1h2006.txt.gz"] = _three_lights(faulty=("AAAF1", 20, 25), factor=0.3)["aaaf1h2006.txt.gz"]
    df = ndbc(tmp_path, FakeNDBC(files)).fetch({**QC_SPEC, "stations": ["AAAF1", "BBBF1"]})
    a = df[df["station"] == "AAAF1"].set_index("date")
    assert a.loc["2006-07-25":"2006-08-10", "qc_low_ratio"].all()


@pytest.mark.parametrize("hours,flagged", [(6, True), (5, False)])
def test_qc_flags_a_stuck_run(tmp_path, hours, flagged):
    f = ndbc(tmp_path, FakeNDBC(_three_lights(stuck=("BBBF1", "2006-07-10", hours))))
    b = f.fetch(QC_SPEC).query("station == 'BBBF1'").set_index("date")
    assert bool(b.loc["2006-07-10", "qc_stuck"]) is flagged and b["qc_stuck"].sum() == int(flagged)


# ── absence is confirmed and recorded; the raw cache is pinned (III F-3) ─────────────────────────────────────────────
class Flaky(FakeNDBC):
    """The first reply for `name` is a 404, then the real file; or an empty 200 for `empty`."""
    def __init__(self, files, once_404=(), empty=()):
        super().__init__(files); self.once, self.empty = set(once_404), set(empty)
    def get(self, url, params=None, timeout=None):
        name = url.rsplit("/", 1)[-1]
        if name in self.once:
            self.once.discard(name); self.calls.append(name); return Resp(404)
        if name in self.empty:
            self.calls.append(name); return Resp(200, b"")
        return super().get(url, params, timeout)


def test_a_transient_404_is_not_absence_and_an_empty_200_fails(tmp_path):
    f = ndbc(tmp_path, Flaky(two_station_files(), once_404={"aaaf1h2006.txt.gz"}))
    f.fetch(SPEC)
    assert 2006 in f.reduction["per_station"]["AAAF1"]["years_present"]   # confirmed on the second ask
    g = ndbc(tmp_path / "e", Flaky(two_station_files(), empty={"aaaf1h2006.txt.gz"}))
    with pytest.raises(ValueError, match="empty body"):
        g.fetch(SPEC)


def test_absence_sidecar_legacy_zero_byte_and_current_year(tmp_path):
    fake = FakeNDBC(two_station_files())
    ndbc(tmp_path, fake).fetch(SPEC)
    side = tmp_path / "wind" / "AAAF1" / "aaaf1h1999.txt.gz.absent.json"
    assert json.loads(side.read_text())["confirmed_by"] == 2
    # a 0.10.0 zero-byte cache file is never read as absence: it is asked again
    (tmp_path / "wind.parquet").unlink(); (tmp_path / "wind_fetch_summary.json").unlink(); side.unlink()
    (tmp_path / "wind" / "AAAF1" / "aaaf1h1999.txt.gz").write_bytes(b"")
    fake2 = FakeNDBC(two_station_files())
    ndbc(tmp_path, fake2).fetch(SPEC)
    assert fake2.calls == ["aaaf1h1999.txt.gz"] * 2
    this = pd.Timestamp.now(tz="UTC").year
    with pytest.raises(ValueError, match="only after the year ends"):
        ndbc(tmp_path / "y", FakeNDBC({})).fetch({**SPEC, "years": [this - 1, this]})


def test_verify_sees_a_raw_cache_changed_under_its_reduction(tmp_path):
    ndbc(tmp_path, FakeNDBC(two_station_files())).fetch(SPEC)
    f = NDBCStdmet(tmp_path, "wind.parquet", "wind_fetch_summary.json", session=Boom())
    assert f.provenance_problem(SPEC) is None
    raw = tmp_path / "wind" / "BBBF1" / "bbbf1h1999.txt.gz"
    raw.write_bytes(gzip.compress(y1999(1999, hours_of("1999-07-01", 24), [1.0] * 24).encode()))
    assert "raw cache" in f.provenance_problem(SPEC) and "BBBF1 1999" in f.provenance_problem(SPEC)


# ── the record's other forms (III F-7, F-12) ─────────────────────────────────────────────────────────────────────────
def y2005_no_hash(year, times, wspd):
    """2005–2006: YYYY … mm, no '#', no units line."""
    head = "YYYY MM DD hh mm WD   WSPD GST  WVHT  DPD   APD  MWD  BAR    ATMP  WTMP  DEWP  VIS  TIDE"
    rows = [f"{t.year} {t.month:02d} {t.day:02d} {t.hour:02d} {t.minute:02d} 159 {w:4.1f} 05.4 99.00 99.00 99.00 999 1018.9  24.4  23.2 999.0 99.0 99.00"
            for t, w in zip(times, wspd)]
    return "\n".join([head, *rows]) + "\n"


def test_parse_the_2005_form_repeated_headers_garbled_minutes_and_50_stamps():
    t = [pd.Timestamp("2005-07-01 00:50"), pd.Timestamp("2005-07-01 01:50")]
    df = parse_stdmet(y2005_no_hash(2005, t, [3.0, 4.0]).encode(), "WSPD")
    assert list(df["time"]) == t and df.attrs == {"malformed": 0, "header_lines": 0}
    txt = y2005(2020, hours_of("2020-11-30", 2), [3.0, 4.0])
    head, units = txt.splitlines()[:2]
    txt += "\n".join([head, units]) + "\n" + "\n".join(y2005(2020, hours_of("2020-12-01", 1), [5.0]).splitlines()[2:]) + "\n"
    txt += "2020 12 01 01 xx  31  6.0  4.5 99.00 99.00 99.00 999 1023.4  18.9 999.0  12.1 99.0 99.00\n"   # garbled minute
    df = parse_stdmet(txt.encode(), "WSPD")
    assert list(df["v"]) == [3.0, 4.0, 5.0]                                # not filled with minute 0
    assert df.attrs == {"malformed": 1, "header_lines": 2}                 # a repeated header + units line, counted apart
    t2 = y1999(1999, hours_of("1999-07-01", 2), [3.0, 4.0])
    t2 += t2.splitlines()[0] + "\n" + "\n".join(y1999(1999, hours_of("1999-07-02", 1), [5.0]).splitlines()[1:]) + "\n"
    df = parse_stdmet(t2.encode(), "WSPD")
    assert list(df["v"]) == [3.0, 4.0, 5.0] and df.attrs == {"malformed": 0, "header_lines": 1}   # a YYYY header repeated


def test_a_stray_row_from_outside_the_span_is_dropped_and_counted(tmp_path):
    files = {"aaaf1h2006.txt.gz": y2005(2006, hours_of("2005-12-31", 24) + hours_of("2006-07-01", 24), [9.0] * 24 + [3.0] * 24)}
    f = ndbc(tmp_path, FakeNDBC(files))
    df = f.fetch({"stations": ["AAAF1"], "years": [2006, 2006], "variable": "WSPD"})
    assert f.reduction["per_station"]["AAAF1"]["rows_stray_year"] == 24   # a full stray day: min_hours would keep it
    assert list(df["date"]) == [pd.Timestamp("2006-07-01")]


def test_a_station_listed_twice_is_refused(tmp_path):
    with pytest.raises(ValueError, match="listed twice"):
        ndbc(tmp_path, FakeNDBC(two_station_files())).fetch({**SPEC, "stations": ["AAAF1", "BBBF1", "AAAF1"]})


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


def test_weekly_count_lt_on_a_point_stream():
    """III F-7: the Obs branch — per unit × week, observations below the threshold; an unobserved week is NaN."""
    mon = pd.Timestamp("2024-07-01")
    d = pd.DataFrame({"unit": [1, 1, 1, 2, 2], "date": [mon, mon + pd.Timedelta(days=1), mon + pd.Timedelta(days=8), mon,
                                                       mon + pd.Timedelta(days=9)],
                      "value": [3.0, 5.0, 6.0, 1.0, np.nan]})                  # unit 2's week 2: one row, its value missing
    ev = ops.Evaluator("s", d, "point", pd.date_range(mon, periods=3, freq="7D"), [1, 2], {"c": 4.0})
    out = ev.weekly(grammar.parse("weekly_count_lt(value, c)", constants=["c"], where="t"))
    nxt = mon + pd.Timedelta(weeks=1)
    assert out.loc[mon, 1] == 1.0 and out.loc[mon, 2] == 1.0 and out.loc[nxt, 1] == 0.0
    assert np.isnan(out.loc[nxt, 2]) and np.isnan(out.loc[mon + pd.Timedelta(weeks=2), 1])


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
    # III F-4: a plant that leaves (primary, t) non-NaN, so the LEAK check (C1) is what must see it, not C4's NaN check
    monkeypatch.setattr(ops.Evaluator, "f_weekly_count_lt",
                        lambda self, x, thr, window=None: ops.Weekly((lambda d: d.add(d.shift(-1), fill_value=0))(orig(self, x, thr).df)))
    with pytest.raises(st.LeakError, match="C1"):
        st.run(inst, verbose=False)


# ── III M-3b-ii-b-1 F-5 (operator ruling 7): the maskable flag reads no day after its own ─────────────────────────────
def test_causal_flag_reads_no_later_day_and_catches_the_fault(tmp_path):
    f = ndbc(tmp_path, FakeNDBC(_three_lights(faulty=("AAAF1", 20, 25))))
    df = f.fetch(QC_SPEC)
    a = df[df["station"] == "AAAF1"].set_index("date")
    fault = pd.date_range("2006-07-21", periods=25)
    assert a.loc[fault[8]:fault[-1], "qc_low_ratio_causal"].all()          # caught once the trailing window fills
    assert not a.loc[:"2006-07-20", "qc_low_ratio_causal"].any()           # never before the fault
    assert f.reduction["per_station"]["AAAF1"]["days_flagged"]["qc_low_ratio_causal"] >= 17
    # no hindsight: the same fault cut off after 3 days. Up to the 3rd fault day the days are identical, so a flag that
    # reads no later day must agree on them; the centred flag reads the days after, and does not (the control)
    short = ndbc(tmp_path / "s", FakeNDBC(_three_lights(faulty=("AAAF1", 20, 3)))).fetch(QC_SPEC)
    b = short[short["station"] == "AAAF1"].set_index("date")
    upto = slice(None, "2006-07-23")
    assert a.loc[upto, "wspd"].equals(b.loc[upto, "wspd"])
    assert a.loc[upto, "qc_low_ratio_causal"].equals(b.loc[upto, "qc_low_ratio_causal"])
    assert not a.loc[upto, "qc_low_ratio"].equals(b.loc[upto, "qc_low_ratio"])


def test_maskable_flags_exclude_the_ones_that_read_ahead():
    from atlantis_core.fetch.ndbc import NDBCStdmet
    assert NDBCStdmet.FLAG_COLUMNS == ("qc_low_ratio_causal",)
    assert set(NDBCStdmet.LOOKAHEAD_FLAGS) == {"qc_low_ratio", "qc_stuck"}
