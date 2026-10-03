"""fetch: offline discipline, provenance pins re-hash, the declared stubs say what they are. No network, ever."""
import json
import pandas as pd
import pytest

from atlantis_core import load_instance
from atlantis_core.fetch import FETCHERS, BUILT, DeclaredFetcher, OfflineError, ERDDAPGriddap, NWISDailyValues
from atlantis_core.fetch import provenance


def test_registry_of_fetchers():
    assert set(BUILT) == {"ArcGISMapServer", "ERDDAPGriddap", "NWISDailyValues"}
    declared = {n for n, c in FETCHERS.items() if issubclass(c, DeclaredFetcher)}
    assert declared == {"NDBCStdmet", "OBISOccurrence", "GBIFOccurrence", "CoralReefWatch"}
    assert not (declared & set(BUILT))


@pytest.mark.parametrize("name", ["NDBCStdmet", "OBISOccurrence", "GBIFOccurrence", "CoralReefWatch"])
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
    q = ERDDAPGriddap(tmp_path, "a", "b").query({"variable": "sst", "zlev": 0.0}, 1982, 1986, [24.4, 25.9, -82.2, -80.6])
    assert q == "sst[(1982-01-01T12:00:00Z):1:(1986-12-31T12:00:00Z)][(0.0):1:(0.0)][(24.4):1:(25.9)][(-82.2):1:(-80.6)]"


def test_exemplar_pins_rehash(exemplar_dir):
    """The three committed parquets re-hash to their *_fetch_summary.json sha256 and to streams.yaml's sha256."""
    inst = load_instance(exemplar_dir)
    for sid, spec in inst.cfg["streams"].items():
        ok, actual, recorded = provenance.verify(inst.path(spec["artifact"]), inst.path(spec["summary"]))
        assert ok, f"{sid}: {actual} != {recorded}"
        assert inst.streams[sid]["sha256"] == actual
