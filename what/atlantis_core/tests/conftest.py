from pathlib import Path
import pytest

EXEMPLAR = Path(__file__).resolve().parents[2] / "exemplars" / "gulf_karenia_brevis"


@pytest.fixture(scope="session")
def exemplar_dir():
    if not (EXEMPLAR / "atlantis.yaml").exists():
        pytest.skip("exemplar not present")
    return EXEMPLAR
