import pytest

from kt_trial.config import generating_theta_dict, load_scenario
from kt_trial.moments import Theta
from kt_trial.schedule import build_templates


@pytest.fixture(scope="session")
def cfg():
    return load_scenario("S1")


@pytest.fixture(scope="session")
def templates(cfg):
    return build_templates(cfg)


@pytest.fixture(scope="session")
def theta(cfg):
    return Theta.from_dict(generating_theta_dict(cfg))
