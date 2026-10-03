"""Patient units from coordinate rules (first match wins) — ported from the exemplar's `hab.regions` (M-1a).

Rules are tiny boolean expressions over `lat` and `lon` (e.g. "lat >= 29.6 and lon < -84.5"), parsed with `ast` and
walked against an explicit whitelist — comparisons, and/or, numeric and boolean literals, unary minus, the two names —
then evaluated vectorised over numpy arrays. Nothing from config is ever passed to `eval`/`compile`.
"""
from __future__ import annotations

import ast
import numpy as np

NAMES = {"lat", "lon"}
_CMP = {ast.Lt: np.less, ast.LtE: np.less_equal, ast.Gt: np.greater, ast.GtE: np.greater_equal,
        ast.Eq: np.equal, ast.NotEq: np.not_equal}


class RuleError(ValueError):
    """A rule used something outside the whitelist."""


def parse_rule(rule: str, rule_id="?"):
    """Parse one rule string into a validated AST (mode='eval'); raise RuleError on anything not whitelisted."""
    try:
        tree = ast.parse(rule, mode="eval")
    except SyntaxError as e:
        raise RuleError(f"unit {rule_id}: cannot parse {rule!r}: {e}") from None
    _check(tree.body, rule_id, rule)
    return tree.body


def _check(node, rid, rule):
    if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
        for v in node.values: _check(v, rid, rule)
    elif isinstance(node, ast.Compare):
        if not all(type(op) in _CMP for op in node.ops):
            raise RuleError(f"unit {rid}: unsupported comparison in {rule!r}")
        for v in [node.left, *node.comparators]: _check(v, rid, rule)
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        _check(node.operand, rid, rule)
    elif isinstance(node, ast.Name):
        if node.id not in NAMES:
            raise RuleError(f"unit {rid}: unknown name {node.id!r} in {rule!r} (only lat, lon)")
    elif isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float, bool)) or isinstance(node.value, complex):
            raise RuleError(f"unit {rid}: literal {node.value!r} not allowed in {rule!r}")
    else:
        raise RuleError(f"unit {rid}: {type(node).__name__} not allowed in {rule!r}")


def _walk(node, env):
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


class RuleGrid:
    """`rules`: [{id, name, rule}] in priority order."""

    def __init__(self, rules: list[dict]):
        self.rules = [(r["id"], r.get("name", str(r["id"])), parse_rule(r["rule"], r["id"])) for r in rules]

    def names(self) -> dict:
        return {rid: name for rid, name, _ in self.rules}

    def assign(self, lat, lon) -> np.ndarray:
        """Vectorised first-match assignment; NaN (float array) where no rule matches."""
        lat = np.asarray(lat, dtype=float); lon = np.asarray(lon, dtype=float)
        env = {"lat": lat, "lon": lon}
        out = np.full(len(lat), np.nan)
        unassigned = np.ones(len(lat), dtype=bool)
        for rid, _name, tree in self.rules:
            hit = _walk(tree, env) & unassigned
            out[hit] = rid
            unassigned &= ~hit
            if not unassigned.any(): break
        return out
