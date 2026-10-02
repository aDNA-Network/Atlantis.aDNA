"""Region-rule parser: whitelist holds, and the safe parser reproduces the S329 `eval` assignment exactly.
Frozen counts were captured at M-1a (2026-10-02) under the original compile/eval implementation on the committed
FWC parquet (sha256 2bde1410…); total 196,024 samples, none unassigned."""
import numpy as np, pandas as pd, pytest
from hab import DATA_RAW
from hab.regions import RuleError, assign_region, assign_region_array, assign_regions, parse_rule, rules

FROZEN = {1: 15992, 2: 6341, 3: 2686, 4: 32893, 5: 56108, 6: 20190, 7: 30563, 8: 12833, 9: 18418}
PARQUET = DATA_RAW / "fwc_hab_karenia_1970_2023.parquet"


@pytest.mark.parametrize("bad", ["__import__('os').system('true')", "lat.real >= 1", "open('x')", "lat + 1 >= 2",
                                 "depth >= 1", "'a' == 'a'", "lat >= 1 if lon else 0", "[lat] == [1]"])
def test_rejects_non_whitelisted(bad):
    with pytest.raises(RuleError):
        parse_rule(bad, "test")


def test_accepts_the_configured_grammar():
    for rid, _n, tree in rules():
        assert tree is not None
    parse_rule("lon >= -80.6 or (lat >= 28.0 and lon >= -81.7)")
    parse_rule("True")


def test_scalar_matches_vector():
    lat = np.array([30.0, 29.2, 28.5, 27.8, 27.2, 26.8, 26.0, 25.0, 27.0, 26.0])
    lon = np.array([-86.0, -83.5, -82.8, -82.6, -82.5, -82.2, -81.9, -81.0, -80.2, -81.5])
    vec = assign_region_array(lat, lon)
    assert [assign_region(a, b) for a, b in zip(lat, lon)] == [int(v) for v in vec]
    assert list(vec) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 7]   # (26.0, -81.5): lon < -81.7 fails the Atlantic rule → Lee-Collier


@pytest.mark.skipif(not PARQUET.exists(), reason="committed FWC parquet not present")
def test_region_counts_unchanged():
    s = pd.read_parquet(PARQUET)
    counts = {int(k): int(v) for k, v in assign_regions(s).value_counts().sort_index().items()}
    assert counts == FROZEN
    assert sum(counts.values()) == len(s) == 196024
