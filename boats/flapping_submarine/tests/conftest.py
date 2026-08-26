import pytest

from submarine.config import SubmarineConfig
from submarine.geometry import build_all


@pytest.fixture(scope="session")
def cfg():
    return SubmarineConfig()


@pytest.fixture(scope="session")
def parts(cfg):
    return {p.name: p for p in build_all(cfg)}
