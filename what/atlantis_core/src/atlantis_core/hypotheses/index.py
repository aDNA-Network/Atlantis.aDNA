"""`what/hypotheses/LEDGER.md`, generated from `ledger/` (M-3b-i; the board index's pattern). Never hand-edited.

    python -m atlantis_core.hypotheses --index [--check] [--root <…/what/hypotheses>]

Byte-stable: rows sorted by hyp_id, no timestamps, written and compared as bytes. Nothing renders unless every row passes
`check` — the ledger never displays an unchecked row. A rendered string with a line break or a control character is
refused, and `|` is escaped, so no row can write markdown.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from atlantis_core.hypotheses import LedgerError
from atlantis_core.hypotheses.check import check_ledger, quotes

HEADER = """# The hypothesis ledger

> **GENERATED — never hand-edit.** Regenerate with `python -m atlantis_core.hypotheses --index` (from
> `what/atlantis_core/`); `--index --check` fails if this file is stale or any row fails its check. The YAML in `ledger/`
> is authoritative; the spec is `README.md`.

> **A row is a hypothesis, not a fact** (README rule 2). `reviewed` means a second reader found the extraction faithful
> to the cited text — never that the mechanism is true. Truth is an instance's SHAP and its write-up, either way (T8).
"""
_BAD = re.compile(r"[\x00-\x1f\x7f]")


def _cell(x) -> str:
    s = "" if x is None else str(x)
    if _BAD.search(s):
        raise LedgerError(f"a rendered value carries a line break or control character: {s[:60]!r}")
    return s.replace("|", "\\|")


def _lag(d: dict) -> str:
    l = d.get("driver_lag") or {}
    v = l.get("lag_value")
    v = int(v) if isinstance(v, float) and v.is_integer() else v
    return f"{v} {l.get('lag_unit', '')}".strip()


def render(root: Path) -> str:
    loaded, fails, _ = check_ledger(root)
    if fails:
        raise LedgerError(f"{len(fails)} row failure(s) — the ledger renders only checked rows:\n" +
                          "\n".join(f"  {k} · {f} · {w}" for k, f, w in fails))
    rs = sorted(loaded, key=lambda r: r["hyp_id"])
    out = [HEADER]
    eco = Counter(r["ecosystem_type"] for r in rs)
    out.append(f"**{len(rs)} rows** · " + " · ".join(f"{k} {v}" for k, v in sorted(eco.items())) + " · tiers " +
               " · ".join(f"{k} {v}" for k, v in sorted(Counter(r.get("tier", "draft") for r in rs).items())) +
               " · results " + " · ".join(f"{k} {v}" for k, v in sorted(Counter(r["realisation"]["result"] for r in rs).items())) +
               f" · pointers quoting text {sum(1 for r in rs if quotes(r['sentence_pointer']))}\n")
    out.append("| hyp_id | ecosystem | event | driver → lag | direction | evidence | year | tier | realisable as | realised in | result |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rs:
        d, z = r["driver"], r["realisation"]
        out.append("| " + " | ".join(_cell(x) for x in (
            f"`{r['hyp_id']}`", r["ecosystem_type"], r["event_variable"], f"{d['variable']} → {_lag(d)}",
            d["driver_direction"], r["evidence_class"], r["citation"]["year"], r.get("tier", "draft"),
            r["realisable_as"], z.get("realised_in") or "—", z["result"])) + " |")
    return "\n".join(out) + "\n"


def ledger_path(root: Path) -> Path:
    return root / "LEDGER.md"


def write_or_check(root: Path, check: bool) -> int:
    try:
        out = render(root)
    except LedgerError as e:
        print(f"✗ {e}"); return 1
    _, _, warns = check_ledger(root)
    for k, f, w in warns:
        print(f"  ⚠ {k} · {f} · {w}")
    b = ledger_path(root)
    if check:
        if not b.exists() or b.read_bytes() != out.encode():
            print(f"✗ {b.name} {'missing' if not b.exists() else 'stale'} — regenerate with `python -m atlantis_core.hypotheses --index`")
            return 1
        print(f"✅ {b.name} up to date · every row checked ({len(warns)} warning(s))"); return 0
    b.write_bytes(out.encode())
    print(f"→ {b}  ({out.count(chr(10) + '| `')} rows; {len(warns)} warning(s))")
    return 0
