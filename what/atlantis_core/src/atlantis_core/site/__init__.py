"""atlantis_core.site — the explainer page as a core template whose every word is instance data (M-1b-ii-b).

    python -m atlantis_core.site --instance <dir>        # → <instance>/<site.yaml output>

An instance opts in with two files: `site.yaml` (what to draw: board entry, groups and colours, vital display, strips,
trace, cases, map) and `site_copy.yaml` (every word: sections as HTML fragments with `{{path|fmt}}` value tokens and
`{{fig:NAME}}` figure tokens, figure words, strip words, the JS's nouns). The template (`template.html`) carries structure,
style and generic renderers only — a test holds it free of exemplar literals. The build refuses an unknown figure, an
unresolved value path, a missing copy key, an orphaned figure or strip word, and outputs that disagree with the board entry
the page cites. Method demonstration, not an operational forecast (SO-4)."""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

from atlantis_core.config import load_instance, load_yaml
from atlantis_core.site.assemble import TOKEN, SiteError, assemble, load_site, resolve

TEMPLATE = Path(__file__).with_name("template.html")
REQUIRED = ("title", "hero", "sections", "figures", "strips", "strings", "footer")
STRINGS = ("obs_plural", "event_followed", "event_not_followed", "below_threshold", "at_threshold", "threshold_short",
           "trace_panels", "whatif_scenario", "whatif_down", "whatif_not_down", "whatif_non_lever", "compare_rows",
           "unit_weeks", "episode", "lever_suffix", "lead_axis", "case_this_week", "no_obs", "availability_group",
           "whatif_only_non_lever")
FORMATS = {"", "1", "2", "3", "4", "pct0", "pct1", "comma", "k", "sci", "label"}   # the template's fmt() — keep in step
FIG = re.compile(r"\{\{fig:(\w+)\}\}")


def template_figures(tpl: str) -> set:
    """The figure names the template can draw (its FIGS and RAW tables)."""
    block = tpl[tpl.index("const FIGS = {"):tpl.index("const DYN")]
    return set(re.findall(r"(?:^|[{,]\s*)(\w+):['`]", block, re.M))


def walk(o):
    if isinstance(o, dict):
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)
    elif isinstance(o, str):
        yield o


def check_copy(copy: dict, data: dict, tpl: str, site: dict) -> None:
    """Every refusal the build makes, in one place (each has a test that feeds it the defect)."""
    errs = [f"copy: missing key {k!r}" for k in REQUIRED if k not in copy]
    errs += [f"copy.strings: missing {k!r}" for k in STRINGS if k not in (copy.get("strings") or {})]
    figs = template_figures(tpl)
    used = []
    for s in walk({k: copy.get(k) for k in ("hero", "sections", "footer")}):
        for name in FIG.findall(s):
            used.append(name)
            if name not in figs:
                errs.append(f"copy: unknown figure {{{{fig:{name}}}}} (template draws {sorted(figs)})")
    errs += [f"copy: figure {{{{fig:{n}}}}} placed {used.count(n)} times (one chart per id)" for n in sorted(set(used)) if used.count(n) > 1]
    # fields the page inserts verbatim, never through the token expander (III F-3b: a token there renders as "{{…}}")
    verbatim = {"sections[].nav": [x.get("nav") for x in copy.get("sections") or []], "strings": copy.get("strings"),
                "figures.label_diagram": (copy.get("figures") or {}).get("label_diagram"),
                "strips[].label": [v.get("label") for v in (copy.get("strips") or {}).values()]}
    for where, val in verbatim.items():
        if any("{{" in x for x in walk(val)):
            errs.append(f"copy.{where}: tokens are not expanded here — write the words")
    errs += [f"copy.figures.{n}: words for a figure no section places" for n in (copy.get("figures") or {}) if n not in used]
    for s in walk(copy):
        for path, f in TOKEN.findall(FIG.sub("", s)):
            try:
                resolve(data, path)
            except KeyError:
                errs.append(f"copy: {{{{{path}}}}} does not resolve in the site data")
            if f not in FORMATS:
                errs.append(f"copy: {{{{{path}|{f}}}}} — unknown format {f!r} (known: {sorted(FORMATS - {''})})")
    keys = {s["key"] for s in site.get("strips", []) or []}
    errs += [f"copy.strips.{k}: no such strip in site.yaml" for k in (copy.get("strips") or {}) if k not in keys]
    errs += [f"site.yaml strip {k!r}: no words in copy.strips" for k in keys if k not in (copy.get("strips") or {})]
    tp = (copy.get("strings") or {}).get("trace_panels") or {}
    errs += [f"copy.strings.trace_panels: no words for trace panel {p!r}" for p in ((site.get("trace") or {}).get("panels") or []) if p not in tp]
    if errs:
        raise SiteError("site copy refused:\n  " + "\n  ".join(errs))


def group_css(site: dict) -> str:
    def block(i):
        return "".join(f"--g-{g}:{spec['color'][i]};" for g, spec in site["groups"].items())
    light, dark = block(0), block(1)
    return (f":root{{{light}}}\n@media (prefers-color-scheme:dark){{:root:not([data-theme=\"light\"]){{{dark}}}}}\n"
            f":root[data-theme=\"dark\"]{{{dark}}}")


def render(tpl: str, data: dict, copy: dict, site: dict) -> str:
    for ph in ("__TITLE__", "/*__GROUP_CSS__*/", "__SITE_DATA__", "__SITE_COPY__"):
        if tpl.count(ph) != 1:
            raise SiteError(f"template: placeholder {ph} must appear exactly once")
    js = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"), allow_nan=False).replace("</", "<\\/")
    return (tpl.replace("__TITLE__", html.escape(re.sub(r"<[^>]+>", "", copy["title"])))
               .replace("/*__GROUP_CSS__*/", group_css(site))
               .replace("__SITE_COPY__", js(copy)).replace("__SITE_DATA__", js(data)))


def build(instance, out: str | None = None) -> Path:
    inst = load_instance(instance)
    site = load_site(inst)
    copy = load_yaml(inst.root / site.get("copy", "site_copy.yaml"))
    data = assemble(inst, site)
    tpl = TEMPLATE.read_text()
    check_copy(copy, data, tpl, site)
    path = inst.root / (out or site["output"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(tpl, data, copy, site))
    return path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="atlantis_core.site")
    ap.add_argument("--instance", required=True)
    ap.add_argument("--out", help="override site.yaml output (relative to the instance)")
    a = ap.parse_args(argv)
    try:
        p = build(a.instance, a.out)
    except SiteError as e:
        print(f"✗ {e}", file=sys.stderr)
        return 1
    print(f"→ {p} ({p.stat().st_size / 1e6:.2f} MB)")
    return 0
