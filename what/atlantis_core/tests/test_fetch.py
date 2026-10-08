"""fetch: offline discipline, provenance pins re-hash, the declared stubs say what they are. No network, ever."""
import json
import pandas as pd
import pytest

from atlantis_core import load_instance
from atlantis_core.fetch import FETCHERS, BUILT, DeclaredFetcher, OfflineError, ERDDAPGriddap, NWISDailyValues
from atlantis_core.fetch import provenance


def test_registry_of_fetchers():
    assert set(BUILT) == {"ArcGISMapServer", "ERDDAPGriddap", "NWISDailyValues", "CoralReefWatch"}   # CRW built at M-2a-i
    declared = {n for n, c in FETCHERS.items() if issubclass(c, DeclaredFetcher)}
    assert declared == {"NDBCStdmet", "OBISOccurrence", "GBIFOccurrence"}
    assert not (declared & set(BUILT))


@pytest.mark.parametrize("name", ["NDBCStdmet", "OBISOccurrence", "GBIFOccurrence"])
def test_declared_fetchers_raise_and_name_endpoint(tmp_path, name):
    f = FETCHERS[name](tmp_path, "x.parquet", "x_fetch_summary.json")
    assert f.endpoint.startswith("https://")
    with pytest.raises(NotImplementedError, match="declared, not built"):
        f.fetch({})
    assert not (tmp_path / "x.parquet").exists()


def test_offline_never_touches_network(tmp_path):
    class Boom:
        def get(self, *a, **k): raise AssertionError("network touched")
    f = NWISDailyValues(tmp_path, "q.parquet", "q.json", offline=True, session=Boom())
    with pytest.raises(OfflineError):
        f.fetch({"sites": ["1"], "parameter": "00060", "start": "2000-01-01", "end": "2000-01-02"})


def test_cache_hit_writes_summary_and_does_not_fetch(tmp_path):
    pd.DataFrame({"date": pd.date_range("2000-01-01", periods=3), "unit": 1, "sst": [1.0, 2.0, 3.0]}).to_parquet(tmp_path / "s.parquet")
    f = ERDDAPGriddap(tmp_path, "s.parquet", "s_fetch_summary.json", offline=True)
    df = f.fetch({})
    assert len(df) == 3 and f.verify()
    s = json.loads((tmp_path / "s_fetch_summary.json").read_text())
    assert s["rows"] == 3 and s["fetched_at_source"].startswith("file mtime") and "pipeline_version" in s


def test_erddap_query_shape(tmp_path):
    from atlantis_core.fetch.erddap import chunks
    spec = {"variable": "sst", "zlev": 0.0, "years": [1982, 1986]}
    (d0, d1), = chunks(spec)                                     # the default 5-year chunk: one request, as before M-2a-ii
    q = ERDDAPGriddap(tmp_path, "a", "b").query(spec, d0, d1, [24.4, 25.9, -82.2, -80.6])
    assert q == "sst[(1982-01-01T12:00:00Z):1:(1986-12-31T12:00:00Z)][(0.0):1:(0.0)][(24.4):1:(25.9)][(-82.2):1:(-80.6)]"


def test_chunks_years_unchanged_and_months_calendar(tmp_path):
    """M-2a-ii: CRW's proxy cuts a request at ~10 s, so a month must be expressible; the year path must not move (exemplar)."""
    from atlantis_core.fetch.erddap import chunk_label, chunks
    ex = {"years": [2002, 2024], "chunk_years": 5}
    assert chunks(ex)[0] == ("2002-01-01", "2006-12-31") and chunks(ex)[-1] == ("2022-01-01", "2024-12-31")
    assert chunk_label(ex, *chunks(ex)[0]) == "2002_2006"                          # pre-M-2a-ii cache names still hit
    m = chunks({"years": [1985, 1986], "start": "1985-03-25", "chunk_months": 1})
    assert m[0] == ("1985-03-25", "1985-03-31") and m[1] == ("1985-04-01", "1985-04-30")    # Jan–Feb dropped, March clamped
    assert ("1986-02-01", "1986-02-28") in m and m[-1] == ("1986-12-01", "1986-12-31") and len(m) == 10 + 12
    assert all(a <= b for a, b in m) and all(str(m[i][1]) < m[i + 1][0] for i in range(len(m) - 1))   # contiguous, ordered
    q = chunks({"years": [2023, 2024], "chunk_months": 5})                          # spans a year boundary; last one cut at 31 Dec
    assert q == [("2023-01-01", "2023-05-31"), ("2023-06-01", "2023-10-31"), ("2023-11-01", "2024-03-31"),
                 ("2024-04-01", "2024-08-31"), ("2024-09-01", "2024-12-31")]
    assert chunk_label({"chunk_months": 1}, "1985-03-25", "1985-03-31") == "1985-03-25_1985-03-31"
    dd = chunks({"years": [1985, 1986], "start": "1985-03-25", "chunk_days": 15})    # N-day spans, across the year end
    assert dd[0] == ("1985-03-25", "1985-04-08") and dd[1] == ("1985-04-09", "1985-04-23") and dd[-1][1] == "1986-12-31"
    assert all((pd.Timestamp(b) - pd.Timestamp(a)).days == 14 for a, b in dd[:-1]) and any(a[:4] == "1985" and b[:4] == "1986" for a, b in dd)
    assert all(pd.Timestamp(dd[i][1]) + pd.Timedelta(days=1) == pd.Timestamp(dd[i + 1][0]) for i in range(len(dd) - 1))
    longer = chunks({"years": [1985, 1990], "start": "1985-03-25", "chunk_days": 15})   # extending years renames nothing cached
    assert longer[:len(dd) - 1] == dd[:-1]
    assert chunk_label({"chunk_days": 15}, *dd[0]) == "1985-03-25_1985-04-08"
    for bad, why in (({"chunk_years": 5, "chunk_months": 1}, "exclusive"), ({"chunk_months": 1, "chunk_days": 15}, "exclusive"),
                     ({"chunk_months": 0}, "≥ 1"), ({"chunk_days": 0}, "≥ 1"),
                     ({"chunk_months": True}, "≥ 1"), ({"chunk_years": "5"}, "≥ 1")):
        with pytest.raises(ValueError, match=why):
            chunks({"years": [2020, 2020], **bad})


def test_exemplar_pins_rehash(exemplar_dir):
    """The three committed parquets re-hash to their *_fetch_summary.json sha256 and to streams.yaml's sha256."""
    inst = load_instance(exemplar_dir)
    for sid, spec in inst.cfg["streams"].items():
        ok, actual, recorded = provenance.verify(inst.path(spec["artifact"]), inst.path(spec["summary"]))
        assert ok, f"{sid}: {actual} != {recorded}"
        assert inst.streams[sid]["sha256"] == actual
