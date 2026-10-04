"""atlantis_core.board.index — `BOARD.md`, generated from `entries/` (M-1d-ii; closes WI-8; RareArchive `board_index.py`
precedent). Never hand-edited.

    python -m atlantis_core.board --index [--entries <…/what/board/entries>] [--check]

Byte-stable: entries sorted by `entry_id`, no timestamps, numbers printed as recorded, written and compared as bytes.
`--check` writes nothing and exits 1 if `BOARD.md` is missing or differs from a fresh render.

Nothing an entry carries can write markdown (III F-2): the top level is closed, every rendered string is refused if it
carries a line break or control character, and `|` is escaped. Supersession is DERIVED, never written into an entry
(SO-2, III F-9): within one (source, instance, stem) the highest version supersedes the lower ones.

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
SHA = re.compile(r"^[0-9a-f]{64}\Z")   # \Z, not $ — Python's $ accepts a trailing newline (C-002)
TOP_KEYS = {"board_entry_schema", "tier", "accuracy_claim", "entry_id", "source", "instance", "method_version",
            "recorded_by", "recorded_at", "run_date", "evaluation", "evaluation_extras", "provenance", "notes",
            "superseded_by"}   # atl_board_entry_v1's top level, closed (III F-2)
ENTRY_ID = re.compile(r"^(\d{4}-\d{2}-\d{2})_([a-z0-9_]+)_v(0|[1-9]\d{0,3})\Z")
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
    for k in sorted(set(entry) - TOP_KEYS):
        errs.append(f"unknown top-level key {k!r} (atl_board_entry_v1 is closed)")
    if not ENTRY_ID.match(str(eid)):
        errs.append(f"entry_id {eid!r} is not <YYYY-MM-DD>_<stem>_v<n>")
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
    ids = {e.get("entry_id") for _, e, _ in out}
    for p, e, _ in out:
        sb = e.get("superseded_by")
        if sb is not None and sb not in ids:
            bad.append(f"{p.name}: superseded_by {sb!r} names no entry on this board")
    if bad:
        raise BoardError("REFUSING to render — the board never displays an unchecked entry:\n  " + "\n  ".join(bad))
    return sorted(out, key=lambda t: t[1]["entry_id"])


def supersession(docs) -> dict[str, str]:
    """entry_id → the entry that supersedes it. DERIVED, never written into an entry (SO-2; III F-9): within one
    (source, instance, stem), the highest version supersedes every lower one. An explicit `superseded_by` must agree."""
    latest: dict = {}
    for _, e, _ in docs:
        _, stem, v = ENTRY_ID.match(e["entry_id"]).groups()
        k = (e["source"], e["instance"], stem)
        if k not in latest or int(v) > latest[k][0]:
            latest[k] = (int(v), e["entry_id"])
    out = {}
    for _, e, _ in docs:
        _, stem, v = ENTRY_ID.match(e["entry_id"]).groups()
        top = latest[(e["source"], e["instance"], stem)]
        if top[1] != e["entry_id"]:
            out[e["entry_id"]] = top[1]
        if e.get("superseded_by") and out.get(e["entry_id"]) != e["superseded_by"]:
            raise BoardError(f"REFUSING to render — {e['entry_id']}: superseded_by {e['superseded_by']!r} disagrees with "
                             f"the derived {out.get(e['entry_id'])!r} (the newest version of the same stem)")
    return out


_BAD = re.compile(r"[\x00-\x1f\x7f\u2028\u2029]")


def _cell(x) -> str:
    """Every rendered string goes through here (III F-2): a control character or line break would let entry content
    write its own markdown — refused, not repaired; `|` is escaped so a value cannot open a column."""
    s = "—" if x is None else str(x)
    if _BAD.search(s):
        raise BoardError(f"REFUSING to render — a rendered value carries a line break or control character: {s[:80]!r}")
    return s.replace("\\", "\\\\").replace("|", "\\|").replace("`", "'")


def _num(x) -> str:
    return _cell(x)


def _event(ev: dict, extras: dict) -> str:
    e = ev.get("event") or extras.get("event") or {}
    if not e:
        return f"`{_cell(ev.get('event_ref'))}`"
    name = e.get("event_id") or ev.get("event_ref") or e.get("variable")
    op = {"above": "≥", "below": "≤"}.get(e.get("direction"), "?")
    return f"`{_cell(name)}` {op} {_cell(e.get('threshold'))} {_cell(e.get('unit', ''))} within {_cell(e.get('horizon'))} wk".replace("  ", " ")


def _patients(ev: dict, extras: dict) -> str:
    p = ev.get("patient") or extras.get("patient") or {}
    return f"{_cell(p.get('n_units'))} × {_cell(p.get('unit_kind'))}" if p else f"`{_cell(ev.get('unit_ref'))}`"


def render(entries: Path) -> str:
    docs = load(entries)
    sup = supersession(docs)
    parts = [HEADER, f"**{len(docs)} entries** ({len(sup)} superseded by a newer version of the same stem; "
                     f"{sum(1 for *_, s in docs if s == 'open')} open-shape, grandfathered by id).", "",
             "## Entries", "",
             "| Entry | Source | Event | Patients | Base rate | AUROC / AUPRC | Climatology AUROC / AUPRC | Lead (budget) | Claim | Shape | Status |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for p, e, shape in docs:
        ev, ex = e["evaluation"], e.get("evaluation_extras") or {}
        lt = ev.get("lead_time") or {}
        lead = (f"{_cell(lt.get('flagged_fraction'))} of {_cell(lt.get('n_onsets'))} onsets flagged, median "
                f"{_cell(lt.get('median_lead'))} wk (@ {_cell(lt.get('budget_rate'))})") if lt else "—"
        claim = _cell(ev["claim"]) + (f" ({_cell(ev['owner_ruling_ref'])})" if ev.get("owner_ruling_ref") else "")
        sh = "closed `AtlEvaluation`" if shape == "closed" else GRANDFATHERED_OPEN[e["entry_id"]][1]
        status = f"superseded → `{sup[e['entry_id']]}`" if e["entry_id"] in sup else "live"
        parts.append(f"| [`{e['entry_id']}`](entries/{p.name}) | {_cell(e['source'])} | {_event(ev, ex)} | {_patients(ev, ex)} | "
                     f"{_num(ev.get('base_rate'))} | {_num(ev.get('auroc'))} / {_num(ev.get('auprc'))} | "
                     f"{_num(ev.get('climatology_auroc'))} / {_num(ev.get('climatology_auprc'))} | {lead} | {claim} | {sh} | {status} |")
    parts += ["", "*Status is derived, never written into an entry (SO-2): within one source, instance and stem, the "
                  "highest version supersedes the lower ones. A superseded entry stays on the board.*",
              "", "## Alert budgets", "",
              "*Precision and recall when the steward can staff alerts on this fraction of patient-weeks. **Budget** is "
              "nominal; **Realised** is the share of test patient-weeks a threshold fixed beforehand actually flagged "
              "(atl_v0 0.4.0). A threshold chosen on the test years themselves (before M-1e) has no realised rate: its "
              "precision and recall are after the fact (F-8).*", "",
              "| Entry | Budget | Threshold fixed on | Realised | Precision | Recall | Alerts |", "|---|---|---|---|---|---|---|"]
    for _, e, _ in docs:
        for b in e["evaluation"]["alert_budgets"]:
            src = b.get("threshold_from") or "test, after the fact (F-8)"
            parts.append(f"| `{e['entry_id']}` | {_num(b.get('rate'))} | {_cell(src)} | {_num(b.get('realised_rate'))} | "
                         f"{_num(b.get('precision'))} | {_num(b.get('recall'))} | {_num(b.get('n_alerts'))} |")
    parts += ["", "## Limits and ablations", ""]
    for _, e, _ in docs:
        ev = e["evaluation"]
        abl = "; ".join(f"{_cell(a.get('ablation_name'))}: AUROC {_num(a.get('ablated_auroc'))}"
                        + (f" / AUPRC {_num(a['ablated_auprc'])}" if a.get("ablated_auprc") is not None else "")
                        for a in ev.get("ablations") or []) or "none declared"
        parts.append(f"- **`{e['entry_id']}`**: limits: {_cell(ev['limitations_ref'])} · config `{_cell(ev['config_hash'])}` · "
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
    if check:   # bytes, not decoded text (III F-11: a CRLF copy compared equal as text)
        if not b.exists() or b.read_bytes() != out.encode():
            print(f"✗ {b.name} {'missing' if not b.exists() else 'stale'} — regenerate with `python -m atlantis_core.board --index`")
            return 1
        print(f"✅ {b.name} up to date"); return 0
    b.write_bytes(out.encode())
    print(f"→ {b}  ({out.count(chr(10) + '| [`')} entries)")
    return 0
