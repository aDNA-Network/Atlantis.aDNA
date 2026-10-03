"""hab_crash_risk — Karenia brevis bloom-onset early warning (sepsis analog).

ARCHIVED IN PLACE 2026-10-03 (M-1b-ii-b): superseded by what/atlantis_core; see src/hab/ARCHIVED.md for what still runs."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROC = ROOT / "data" / "processed"
OUT = ROOT / "outputs"


def load_config():
    with open(ROOT / "config.yaml") as f:
        return yaml.safe_load(f)
