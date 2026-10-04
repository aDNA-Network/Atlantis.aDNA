"""atlantis_core.board.index — `BOARD.md`, generated from `entries/` (M-1d-ii; closes WI-8; RareArchive `board_index.py`
precedent). Never hand-edited.

    python -m atlantis_core.board --index [--entries <…/what/board/entries>] [--check]

Byte-stable: entries sorted by `entry_id`, no timestamps, numbers printed as recorded. `--check` writes nothing and
exits 1 if `BOARD.md` is missing or differs from a fresh render.

Every entry must pass before anything renders — the board never displays an unchecked entry:
- **closed** (from v1 on): the `evaluation` validates as the closed `AtlEvaluation` against the committed schema;
- **open** — ONLY an `entry_id` in `GRANDFATHERED_OPEN` (today: v0, written by the M-0 sitting script before the closed
  shape existed), and only **as the exact bytes pinned there**: an open `evaluation` has no closed key set to stop a
  smuggled field, so the pin is the closure (and SO-2 already says those bytes never change). It must still carry the
  README's required minimum, and the table labels it. There is no other fallback:
  any other entry that fails the closed schema refuses the whole render (C-015 — a fallback that silences a failure must
  name what it disables; this one names one entry, by id).
Both kinds pass `assert_green` and the top-level checks (GREEN tier · the NONE accuracy line · file name = `entry_id` ·
an operational claim cites its owner ruling)."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from atlantis_core.board import BoardError, assert_green, validate

GRANDFATHERED_OPEN = {   # entry_id → (sha256 of the file's bytes, the label the table shows)
    "2026-09-23_gulf_karenia_brevis_v0": ("4a0b1fe6fcdd2cf5a972a1f3ab907b535edd0a173ce3ee5fe782afcd9dede9ef",
                                          "open shape — pre-atlantis_core (M-0 sitting script); not a closed AtlEvaluation"),
}
SHA = re.compile(r"^[0-9a-f]{64}$")
HEADER = """# The Atlantis evidence board

> **GENERATED — never hand-edit.** Regenerate with `python -m atlantis_core.board --index` (from `what/atlantis_core/`);
> `--index --check` fails if this file is stale. A merge conflict here is resolved by regenerating, never by hand.
> Rules and lifecycle: `README.md`. The JSON in `entries/` is authoritative.

> ⛔ **THIS BOARD MAKES NO ACCURACY CLAIM.** Every entry is a *method demonstration* unless its claim cites an instance
> owner's written ruling. Read every score against **its own base rate** and at **its stated alert budgets** — a bare
> AUROC is not a result here.
"""


def _minimum(ev: dict) -> list[str]:
    """README §What an entry is — the fields every entry carries, whatever its shape."""
    errs = []
    if not isinstance(ev.get("base_rate"), (int, float)):
        errs.append("evaluation.base_rate missing (a score without its base rate is rejected)")
    if not (isinstance(ev.get("alert_budgets"), list) and ev["alert_budgets"]):
        errs.append("evaluation.alert_budgets: ≥ 1 required")
    for k in ("claim", "limitations_ref", "config_hash"):
        if not ev.get(k):
            errs.append(f"evaluation.{k} missing")
    pins = ev.get("data_pins")
    if not (isinstance(pins, list) and pins and all(isinstance(p, dict) and SHA.match(str(p.get("sha256", ""))) for p in pins)):
        errs.append("evaluation.data_pins: every pin carries a sha256")
    return errs


def check_entry(path: Path, entry: dict, raw: bytes = b"") -> tuple[str, list[str]]:
    """→ (shape, problems). shape ∈ {'closed', 'open'}."""
    errs = []
    eid = entry.get("entry_id")
    if path.name != f"{eid}.json":
        errs.append(f"file name {path.name} ≠ entry_id {eid!r}")
    if entry.get("board_entry_schema") != "atl_board_entry_v1":
        errs.append(f"board_entry_schema {entry.get('board_entry_schema')!r} ≠ 'atl_board_entry_v1'")
    if entry.get("tier") != "GREEN":
        errs.append(f"tier {entry.get('tier')!r} — the board is GREEN only")
    if not str(entry.get("accuracy_claim", "")).startswith("NONE"):
        errs.append("accuracy_claim: the literal 'NONE — …' line is required")
    if entry.get("source") not in ("exemplar", "instance"):
        errs.append(f"source {entry.get('source')!r} ∉ exemplar | instance")
    ev = entry.get("evaluation")
    if not isinstance(ev, dict):
        return "open", errs + ["evaluation missing"]
    try:
        assert_green(entry)
    except BoardError as e:
        errs.append(str(e))
    if ev.get("claim") != "method_demonstration" and not ev.get("owner_ruling_ref"):
        errs.append(f"claim {ev.get('claim')!r} without owner_ruling_ref (SO-4)")
    try:
        validate(ev)
        shape = "closed"
    except BoardError as e:
        shape = "open"
        if eid not in GRANDFATHERED_OPEN:
            errs.append(f"not a closed AtlEvaluation and not grandfathered — {str(e)[:300]}")
        elif hashlib.sha256(raw).hexdigest() != GRANDFATHERED_OPEN[eid][0]:
            errs.append("grandfathered open-shape entry is not the pinned bytes (an open evaluation is closed only by its pin; "
                        "SO-2: entries are never edited — publish a new version)")
    errs += _minimum(ev)
    return shape, errs


def load(entries: Path) -> list[tuple[Path, dict, str]]:
    entries = Path(entries)
    if not entries.is_dir():
        raise BoardError(f"no entries directory at {entries}")
    out, bad = [], []
    for p in sorted(entries.glob("*.json")):
        try:
            raw = p.read_bytes(); e = json.loads(raw)
        except json.JSONDecodeError as x:
            bad.append(f"{p.name}: not JSON ({x})"); continue
        shape, errs = check_entry(p, e, raw)
        bad += [f"{p.name}: {x}" for x in errs]
        out.append((p, e, shape))
    if bad:
        raise BoardError("REFUSING to render — the board never displays an unchecked entry:\n  " + "\n  ".join(bad))
    return sorted(out, key=lambda t: t[1]["entry_id"])


def _num(x) -> str:
    return "—" if x is None else str(x)


def _event(ev: dict, extras: dict) -> str:
    e = ev.get("event") or extras.get("event") or {}
    if not e:
        return f"`{ev.get('event_ref', '—')}`"
    name = e.get("event_id") or ev.get("event_ref") or e.get("variable", "—")
    op = {"above": "≥", "below": "≤"}.get(e.get("direction"), "?")
    return f"`{name}` {op} {e.get('threshold')} {e.get('unit', '')} within {e.get('horizon')} wk".replace("  ", " ")


def _patients(ev: dict, extras: dict) -> str:
    p = ev.get("patient") or extras.get("patient") or {}
    return f"{p.get('n_units', '—')} × {p.get('unit_kind', '—')}" if p else f"`{ev.get('unit_ref', '—')}`"


def render(entries: Path) -> str:
    docs = load(entries)
    n_sup = sum(1 for _, e, _ in docs if e.get("superseded_by"))
    parts = [HEADER, f"**{len(docs)} entries** ({n_sup} superseded; "
                     f"{sum(1 for *_, s in docs if s == 'open')} open-shape, grandfathered by id).", "",
             "## Entries", "",
             "| Entry | Source | Event | Patients | Base rate | AUROC / AUPRC | Climatology AUROC / AUPRC | Lead (budget) | Claim | Shape | Status |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for p, e, shape in docs:
        ev, ex = e["evaluation"], e.get("evaluation_extras") or {}
        lt = ev.get("lead_time") or {}
        lead = (f"{lt.get('flagged_fraction')} of {lt.get('n_onsets')} onsets flagged, median {lt.get('median_lead')} wk "
                f"(@ {lt.get('budget_rate')})") if lt else "—"
        claim = ev["claim"] + (f" ({ev['owner_ruling_ref']})" if ev.get("owner_ruling_ref") else "")
        sh = "closed `AtlEvaluation`" if shape == "closed" else GRANDFATHERED_OPEN[e["entry_id"]][1]
        status = f"superseded → `{e['superseded_by']}`" if e.get("superseded_by") else "live"
        parts.append(f"| [`{e['entry_id']}`](entries/{p.name}) | {e['source']} | {_event(ev, ex)} | {_patients(ev, ex)} | "
                     f"{_num(ev.get('base_rate'))} | {_num(ev.get('auroc'))} / {_num(ev.get('auprc'))} | "
                     f"{_num(ev.get('climatology_auroc'))} / {_num(ev.get('climatology_auprc'))} | {lead} | {claim} | {sh} | {status} |")
    parts += ["", "## Alert budgets", "",
              "*Precision and recall when the steward can staff alerts on this fraction of patient-weeks.*", "",
              "| Entry | Budget | Precision | Recall | Alerts |", "|---|---|---|---|---|"]
    for _, e, _ in docs:
        for b in e["evaluation"]["alert_budgets"]:
            parts.append(f"| `{e['entry_id']}` | {_num(b.get('rate'))} | {_num(b.get('precision'))} | "
                         f"{_num(b.get('recall'))} | {_num(b.get('n_alerts'))} |")
    parts += ["", "## Limits and ablations", ""]
    for _, e, _ in docs:
        ev = e["evaluation"]
        abl = "; ".join(f"{a.get('ablation_name')}: AUROC {_num(a.get('ablated_auroc'))}"
                        + (f" / AUPRC {a['ablated_auprc']}" if a.get("ablated_auprc") is not None else "")
                        for a in ev.get("ablations") or []) or "none declared"
        parts.append(f"- **`{e['entry_id']}`** — limits: {ev['limitations_ref']} · config `{ev['config_hash']}` · "
                     f"ablations: {abl}")
    return "\n".join(parts) + "\n"


def board_path(entries: Path) -> Path:
    return Path(entries).parent / "BOARD.md"


def write_or_check(entries: Path, check: bool) -> int:
    try:
        out = render(entries)
    except BoardError as e:
        print(f"✗ {e}"); return 1
    b = board_path(entries)
    if check:
        if not b.exists() or b.read_text() != out:
            print(f"✗ {b.name} {'missing' if not b.exists() else 'stale'} — regenerate with `python -m atlantis_core.board --index`")
            return 1
        print(f"✅ {b.name} up to date"); return 0
    b.write_text(out)
    print(f"→ {b}  ({out.count(chr(10) + '| [`')} entries)")
    return 0
