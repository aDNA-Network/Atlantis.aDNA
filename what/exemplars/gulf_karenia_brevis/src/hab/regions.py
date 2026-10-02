"""Region assignment from lat/lon rules in config.yaml (first match wins).

Rules are tiny boolean expressions over `lat` and `lon` (e.g. "lat >= 29.6 and lon < -84.5"). They are parsed with
`ast` and walked against an explicit whitelist — comparisons, and/or, numeric and boolean literals, unary minus,
the two names — then evaluated vectorised over numpy arrays. Nothing from config is ever passed to `eval`/`compile`
(M-1a, 2026-10-02; the S329 version did exactly that).
"""
import ast
import numpy as np
import pandas as pd
from hab import load_config

_RULES = None
_NAMES = {"lat", "lon"}
_CMP = {ast.Lt: np.less, ast.LtE: np.less_equal, ast.Gt: np.greater, ast.GtE: np.greater_equal,
        ast.Eq: np.equal, ast.NotEq: np.not_equal}


class RuleError(ValueError):
    """A region rule used something outside the whitelist."""


def parse_rule(rule, rule_id="?"):
    """Parse one rule string into a validated AST (mode='eval'); raise RuleError on anything not whitelisted."""
    try:
        tree = ast.parse(rule, mode="eval")
    except SyntaxError as e:
        raise RuleError(f"region {rule_id}: cannot parse {rule!r}: {e}") from None
    _check(tree.body, rule_id, rule)
    return tree.body


def _check(node, rid, rule):
    if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
        for v in node.values: _check(v, rid, rule)
    elif isinstance(node, ast.Compare):
        if not all(type(op) in _CMP for op in node.ops):
            raise RuleError(f"region {rid}: unsupported comparison in {rule!r}")
        for v in [node.left, *node.comparators]: _check(v, rid, rule)
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        _check(node.operand, rid, rule)
    elif isinstance(node, ast.Name):
        if node.id not in _NAMES:
            raise RuleError(f"region {rid}: unknown name {node.id!r} in {rule!r} (only lat, lon)")
    elif isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float, bool)) or isinstance(node.value, complex):
            raise RuleError(f"region {rid}: literal {node.value!r} not allowed in {rule!r}")
    else:
        raise RuleError(f"region {rid}: {type(node).__name__} not allowed in {rule!r}")


def _walk(node, env):
    """Evaluate a validated AST against env = {'lat': ndarray, 'lon': ndarray}; returns a boolean ndarray."""
    n = len(env["lat"])
    if isinstance(node, ast.BoolOp):
        parts = [_walk(v, env) for v in node.values]
        return np.logical_and.reduce(parts) if isinstance(node.op, ast.And) else np.logical_or.reduce(parts)
    if isinstance(node, ast.Compare):
        out = np.ones(n, dtype=bool); left = _walk(node.left, env)
        for op, comp in zip(node.ops, node.comparators):
            right = _walk(comp, env)
            out &= _CMP[type(op)](left, right)
            left = right
        return out
    if isinstance(node, ast.UnaryOp):
        return -_walk(node.operand, env)
    if isinstance(node, ast.Name):
        return env[node.id]
    if isinstance(node, ast.Constant):
        return np.full(n, node.value)
    raise RuleError(f"unexpected node {type(node).__name__}")  # unreachable after _check


def rules():
    global _RULES
    if _RULES is None:
        cfg = load_config()
        _RULES = [(r["id"], r["name"], parse_rule(r["rule"], r["id"])) for r in cfg["regions"]]
    return _RULES


def assign_region_array(lat, lon):
    """Vectorised first-match assignment; NaN (float array) where no rule matches."""
    lat = np.asarray(lat, dtype=float); lon = np.asarray(lon, dtype=float)
    env = {"lat": lat, "lon": lon}
    out = np.full(len(lat), np.nan)
    unassigned = np.ones(len(lat), dtype=bool)
    for rid, _name, tree in rules():
        hit = _walk(tree, env) & unassigned
        out[hit] = rid
        unassigned &= ~hit
        if not unassigned.any(): break
    return out


def assign_region(lat, lon):
    """Scalar convenience: region id (int) or NaN."""
    v = assign_region_array([lat], [lon])[0]
    return int(v) if not np.isnan(v) else np.nan


def assign_regions(df, lat="lat", lon="lon"):
    return pd.Series(assign_region_array(df[lat].values, df[lon].values), index=df.index).astype("int64")


def region_names():
    return {r["id"]: r["name"] for r in load_config()["regions"]}


if __name__ == "__main__":  # python -m hab.regions → counts per region on the committed FWC parquet
    import json
    from hab import DATA_RAW
    s = pd.read_parquet(DATA_RAW / "fwc_hab_karenia_1970_2023.parquet")
    print(json.dumps({int(k): int(v) for k, v in assign_regions(s).value_counts().sort_index().items()}))
