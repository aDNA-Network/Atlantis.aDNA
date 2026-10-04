"""The Atlantis gitleaks config's one allowlist (P1-gate push, 2026-10-03) is as narrow as it says: a chart panel key
passes; a real-looking key in the same position, or in a site page beside it, is still caught. The first draft was
path-scoped and let ANY secret in a site page pass (gitleaks 8.30 skips a whole file on a `paths` match) — planted
here so it cannot come back."""
import shutil
import subprocess

import pytest

from atlantis_core.lattice import ROOT

CFG = ROOT / "what" / "atlantis_core" / "src" / "atlantis_core" / "gitleaks_atlantis.toml"
pytestmark = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks not installed")
TOKEN = "sk_" + "live_" + "4eC39HqLyjWDarjtT1zdp7dcXb"   # Stripe-shaped, not a real key; assembled so this file never carries one


def leaks(tmp_path, rel, text):
    f = tmp_path / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text)
    r = subprocess.run(["gitleaks", "detect", "--no-git", "--no-banner", "-c", str(CFG), "-s", str(tmp_path)],
                       capture_output=True, text=True)
    return r.returncode != 0


CHART = '{"panels":[{"key":"discharge_30d_t0","y":[1,2]}]}'


def test_chart_key_in_a_site_page_passes(tmp_path):
    assert not leaks(tmp_path, "site/page_v1.html", f"<script>const D={CHART};</script>")


def test_real_looking_key_in_the_same_position_is_caught(tmp_path):
    assert leaks(tmp_path, "site/page_v1.html", '<script>const D={"panels":[{"key":"' + TOKEN + '"}]};</script>')


@pytest.mark.parametrize("line", [f'stripe_key = "{TOKEN}"', '"api_' + 'key": "' + 'Zx9qT4mW8rL2' + 'vB6nK1pH5sD3fG7jC0aE"'])
def test_a_secret_in_a_site_page_is_still_caught(tmp_path, line):
    """The path-scoped first draft passed both of these."""
    assert leaks(tmp_path, "site/page_v1.html", f"<script>const D={CHART};</script>\n{line}\n")


def test_long_segment_snake_key_is_caught(tmp_path):
    assert leaks(tmp_path, "site/page_v1.html", '{"key":"live_' + "a1b2c3d4e5f6g7h8i9j0k1l2" + '"}')
