#!/usr/bin/env python3
"""check_controls_json.py — atl_v0 (M-1c). Worlds 2 and 3 of run_controls.sh, plus two schema-level assertions.

Runs every control under the COMMITTED JSON Schema (descendants OFF) and under a scratch JSON Schema generated with
--include-range-class-descendants, each under the draft it declares and WITH that draft's FORMAT_CHECKER (as
linkml-validate does — ASOAtlas S15 / R46: without it the worlds silently disagree on every `datetime` slot). Same
contract as run_controls.sh: pos validates; neg rejects and every error matches its REJECTS_ON regex and, when the fixture
has `# REJECTS_AT:`, its path too. A nested (anyOf/oneOf) error counts as named only if its OWN message+path match, or if
EVERY branch beneath it is named — "any branch" would let a wrong-reason rejection through (M-1c III review F-11).
Also FAILS if (a) the committed file is stale against a fresh `gen-json-schema --closed`, (b) the format checker cannot
reject a malformed date-time (a missing format package makes jsonschema skip formats silently — an instrument failure),
or (c) Rule 4 is broken: a class used as a slot range has a concrete descendant (then descendants ON/OFF diverge).
A fixture runner, not a validator: it adds no rule of its own. Usage: check_controls_json.py <LINKML_BIN>"""
import glob, json, os, re, subprocess, sys
import yaml
from jsonschema import validators
BIN = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__))
LINKML = os.path.join(HERE, '..', '..', 'atl_ontology_v0.linkml.yaml')
COMMITTED = os.path.join(HERE, '..', '..', 'atl_ontology_v0.schema.json')
def gen(*flags):
    return subprocess.run([os.path.join(BIN, 'gen-json-schema'), '--closed', *flags, LINKML], capture_output=True, text=True, check=True).stdout
fail = 0
# Rule 4 — flag-proof: no range class has a concrete descendant.
from linkml_runtime.utils.schemaview import SchemaView
sv = SchemaView(LINKML)
ranges = {sv.induced_slot(s, c).range for c in sv.all_classes() for s in sv.class_slots(c)} & set(sv.all_classes())
bad = sorted((r, d) for r in ranges for d in sv.class_descendants(r, reflexive=False) if not sv.get_class(d).abstract)
if bad: print(f"FAIL  Rule 4 (flag-proof): range class with a concrete descendant: {bad}"); fail += 1
else: print(f"== Rule 4 (flag-proof): {len(ranges)} range classes, no concrete descendants ==")
fresh = gen()
stale = (not os.path.exists(COMMITTED)) or open(COMMITTED).read() != fresh
worlds = {'committed(desc-off)': json.load(open(COMMITTED)) if os.path.exists(COMMITTED) else json.loads(fresh),
          'scratch(desc-on)': json.loads(gen('--include-range-class-descendants'))}
def path(e): return '/' + '/'.join(map(str, e.absolute_path))
def named(e, pat, at):   # own message+path match, or every branch beneath it is named (F-11)
    if re.search(pat, e.message) and (at is None or re.search(at, path(e))): return True
    return bool(e.context) and all(named(c, pat, at) for c in e.context)
for name, S in worlds.items():
    VC = validators.validator_for(S); FC = VC.FORMAT_CHECKER
    if FC.conforms('never', 'date-time') or FC.conforms('2026-13-45T99:00:00Z', 'date-time'):
        print(f"FAIL  [{name}] FORMAT_CHECKER does not check date-time here (missing rfc3339-validator?) — instrument failure"); sys.exit(1)
    V = VC(S, format_checker=FC); p = f = 0
    for fx in sorted(glob.glob(os.path.join(HERE, 'pos_*.yaml')) + glob.glob(os.path.join(HERE, 'neg_*.yaml'))):
        b = os.path.basename(fx); errs = list(V.iter_errors(yaml.safe_load(open(fx))))
        if b.startswith('pos_'):
            ok = not errs; why = '' if ok else errs[0].message[:110]
        else:
            pat = next((l.split(':', 1)[1].strip() for l in open(fx) if l.startswith('# REJECTS_ON:')), None)
            at = next((l.split(':', 1)[1].strip() for l in open(fx) if l.startswith('# REJECTS_AT:')), None)
            if pat is None: ok, why = False, 'no REJECTS_ON line'
            else:
                unnamed = [e for e in errs if not named(e, pat, at)]
                ok = bool(errs) and not unnamed
                why = 'validates' if not errs else ('unnamed: ' + unnamed[0].message[:100] + ' @ /' + '/'.join(map(str, unnamed[0].absolute_path)) if unnamed else '')
        if ok: p += 1
        else: f += 1; print(f"FAIL  [{name}] {b} {why}")
    print(f"== {name} ({V.__class__.__name__}): {p} pass · {f} fail =="); fail += f
if stale: print("FAIL  committed atl_ontology_v0.schema.json is STALE or ABSENT — regenerate with gen-json-schema --closed"); fail += 1
else: print("== committed JSON Schema == fresh gen-json-schema --closed (byte-identical) ==")
sys.exit(1 if fail else 0)
