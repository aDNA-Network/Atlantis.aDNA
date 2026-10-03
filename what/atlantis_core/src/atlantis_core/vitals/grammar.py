"""The transform grammar — what `AtlVital.transform` may say.

A transform is a tiny call expression over one stream, parsed with `ast` against a whitelist (the same discipline as
the region rules): known function names with fixed arity, the terminal `value`, named constants, numeric literals and
unary minus. Nothing is evaluated by Python; `ops.Evaluator` walks the validated tree.

Value kinds: obs (per observation, point streams) → daily (date × entity) → weekly (week × unit) → scalar.

    log10p1(x)                    log10(1 + max(x, 0))                         obs|daily|scalar → same
    roll_mean_days(x, days, min)  trailing rolling mean over calendar days     daily → daily
    anomaly(x)                    minus the stream's climatology (atlantis.yaml → climatology[stream]);
                                  day-of-year on daily, ISO-week-of-year on weekly; era years inclusive
    weekly_max|min|mean|median|p90(x)   aggregate per unit × ISO week          obs|daily → weekly
    weekly_count(x)               non-null count per unit × week, 0-filled     obs|daily → weekly
    at_week_end(x)                sample on the Sunday closing each week       daily → weekly
    rolling_max(x) · rolling_sum(x)   trailing window = the vital's `window`   weekly → weekly
    diff(x)                       x − x shifted by the vital's `window`        weekly → weekly
    weeks_since_ge(x, thr) · weeks_since_gt(x, thr)   steps since x ≥ / > thr (capped)   weekly → weekly
    harmonic_sin(period) · harmonic_cos(period)       of the ISO week number   → weekly

The vital's `lag` slot shifts the finished weekly signal; it is never written inside the transform.
Station-keyed daily streams are averaged onto units (atlantis.yaml → streams[...].stations) when they become weekly.
"""
from __future__ import annotations

import ast

# name → (arity, needs_window)
FUNCS = {
    "log10p1": (1, False), "roll_mean_days": (3, False), "anomaly": (1, False),
    "weekly_max": (1, False), "weekly_min": (1, False), "weekly_mean": (1, False), "weekly_median": (1, False),
    "weekly_p90": (1, False), "weekly_count": (1, False), "at_week_end": (1, False),
    "rolling_max": (1, True), "rolling_sum": (1, True), "diff": (1, True),
    "weeks_since_ge": (2, False), "weeks_since_gt": (2, False),
    "harmonic_sin": (1, False), "harmonic_cos": (1, False),
}
WINDOWED = {f for f, (_, w) in FUNCS.items() if w}
TERMINALS = {"value"}
EVENT_CONSTANT = "event_threshold"


class TransformError(ValueError):
    """A transform used something outside the grammar."""


def parse(expr: str, constants=(), where="?"):
    """Validate and return the expression AST body. `constants`: names allowed besides `value` / `event_threshold`."""
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise TransformError(f"{where}: cannot parse {expr!r}: {e}") from None
    names = TERMINALS | {EVENT_CONSTANT} | set(constants)
    _check(tree.body, names, where, expr)
    return tree.body


def _check(node, names, where, expr):
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in FUNCS:
            fn = getattr(node.func, "id", type(node.func).__name__)
            raise TransformError(f"{where}: unknown function {fn!r} in {expr!r}")
        if node.keywords:
            raise TransformError(f"{where}: keyword arguments not allowed in {expr!r}")
        arity = FUNCS[node.func.id][0]
        if len(node.args) != arity:
            raise TransformError(f"{where}: {node.func.id} takes {arity} argument(s), got {len(node.args)} in {expr!r}")
        for a in node.args: _check(a, names, where, expr)
    elif isinstance(node, ast.Name):
        if node.id not in names:
            raise TransformError(f"{where}: unknown name {node.id!r} in {expr!r}")
    elif isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise TransformError(f"{where}: literal {node.value!r} not allowed in {expr!r}")
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        _check(node.operand, names, where, expr)
    else:
        raise TransformError(f"{where}: {type(node).__name__} not allowed in {expr!r}")


def functions_used(node) -> set[str]:
    return {n.func.id for n in ast.walk(node) if isinstance(n, ast.Call)}


def uses_value(node) -> bool:
    return any(isinstance(n, ast.Name) and n.id == "value" for n in ast.walk(node))
