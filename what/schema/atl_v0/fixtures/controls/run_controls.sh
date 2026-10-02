#!/usr/bin/env bash
# run_controls.sh — atl_v0 (M-1c). Every pos_*.yaml must validate; every neg_*.yaml must FAIL, and ONLY on the constraint
# it names. Precedent: ASOAtlas.aDNA/what/schema/aso_v0/fixtures/controls/run_controls.sh (itself after Ray.aDNA).
# Nothing is installed on the node: set LINKML_BIN to a scratch venv's bin/ holding linkml-validate, gen-json-schema and
# a python with jsonschema[format] + rfc3339-validator + pyyaml + linkml-runtime.
#
# Three validators, one verdict (ASOAtlas rule 1 — a constraint is claimed only if BOTH declared validators enforce it):
#   1. linkml-validate            (generates its own JSON Schema, include_range_class_descendants ON)
#   2. the COMMITTED atl_ontology_v0.schema.json   (descendants OFF), under the draft it declares, with FORMAT_CHECKER
#   3. a scratch JSON Schema from --include-range-class-descendants, same draft, with FORMAT_CHECKER
# …plus: the committed JSON Schema must equal a fresh `gen-json-schema --closed` byte-for-byte (a stale file fails the
# run), and Rule 4 (flag-proof) is asserted: no class used as a slot range has a concrete descendant.
#
# A negative carries `# REJECTS_ON: <regex>`: EVERY error it raises must match it. An optional `# REJECTS_AT: <regex>`
# names the path every error must be at. A negative that rejects for any other reason proves nothing and FAILS the run.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; SCHEMA="$HERE/../../atl_ontology_v0.linkml.yaml"
[ -n "${LINKML_BIN:-}" ] || { echo "set LINKML_BIN to a scratch venv's bin/"; exit 2; }
LV="$LINKML_BIN/linkml-validate"; PY="$LINKML_BIN/python"
[ -x "$LV" ] && [ -x "$PY" ] || { echo "linkml-validate / python not found under LINKML_BIN=$LINKML_BIN"; exit 2; }
[ -f "$SCHEMA" ] || { echo "SCHEMA NOT FOUND at $SCHEMA — every negative would be a false pass"; exit 2; }
ls "$HERE"/pos_*.yaml >/dev/null 2>&1 && ls "$HERE"/neg_*.yaml >/dev/null 2>&1 || { echo "no pos_/neg_ fixtures under $HERE"; exit 2; }
pass=0; fail=0
for f in "$HERE"/pos_*.yaml "$HERE"/neg_*.yaml; do
  b=$(basename "$f"); out=$("$LV" -s "$SCHEMA" -C AtlDocument "$f" 2>&1); rc=$?
  errs=$(printf '%s\n' "$out" | grep '^\[ERROR\]' | sed -E 's/^\[ERROR\] \[[^]]*\] //')   # anchored: ASOAtlas's greedy `s/.*\] \[[^]]*\] //` ate a message's own `[] ` (M-1c finding)
  case "$b" in
    pos_*) if [ $rc -eq 0 ]; then echo "PASS  $b validates"; pass=$((pass+1));
           else echo "FAIL  $b should validate:"; printf '%s\n' "$out" | head -5; fail=$((fail+1)); fi ;;
    neg_*) pat=$(grep -m1 '^# REJECTS_ON:' "$f" | sed 's/^# REJECTS_ON: //')
           at=$(grep -m1 '^# REJECTS_AT:' "$f" | sed 's/^# REJECTS_AT: //')
           if [ -z "$pat" ]; then echo "FAIL  $b has no REJECTS_ON line"; fail=$((fail+1));
           elif [ $rc -eq 0 ]; then echo "FAIL  $b should be rejected but validates"; fail=$((fail+1));
           elif [ -z "$errs" ]; then echo "FAIL  $b rejected with NO error line — instrument failure, not a result"; printf '%s\n' "$out" | head -3; fail=$((fail+1));
           elif printf '%s\n' "$errs" | grep -vqE "$pat"; then echo "FAIL  $b rejected for an UNNAMED reason:"; printf '%s\n' "$errs" | grep -vE "$pat" | head -3; fail=$((fail+1));
           elif [ -n "$at" ] && printf '%s\n' "$errs" | awk 'match($0, / in \/[^ ]*$/) {print substr($0, RSTART+4); next} {print "<no path>"}' | grep -vqE "$at"; then
             echo "FAIL  $b rejected at an UNNAMED site (REJECTS_AT $at):"; printf '%s\n' "$errs" | awk 'match($0, / in \/[^ ]*$/) {print "      " substr($0, RSTART+4)}' | head -3; fail=$((fail+1))
           else echo "PASS  $b rejected — $(printf '%s\n' "$errs" | head -1 | cut -c1-120)"; pass=$((pass+1)); fi ;;
  esac
done
echo "== linkml-validate: $pass pass · $fail fail =="
"$PY" "$HERE/check_controls_json.py" "$LINKML_BIN"; jrc=$?
[ "$fail" -eq 0 ] && [ "$jrc" -eq 0 ] && echo "== ALL WORLDS AGREE ==" && exit 0
echo "== RUN FAILED =="; exit 1
