"""Inject outputs/site_data.json into site/template.html → site/hab_crash_risk.html."""
from hab import ROOT, OUT

def main():
    tpl = (ROOT / "site" / "template.html").read_text()
    data = (OUT / "site_data.json").read_text().replace("</script", "<\\/script")
    assert "__SITE_DATA__" in tpl
    out = ROOT / "site" / "hab_crash_risk.html"
    out.write_text(tpl.replace("__SITE_DATA__", data))
    print(f"→ {out} ({out.stat().st_size/1e6:.2f} MB)")

if __name__ == "__main__":
    main()
