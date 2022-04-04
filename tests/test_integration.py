import pytest
from ape._cli import cli
from click.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def ape_cli():
    return cli


def test_help(runner, ape_cli):
    result = runner.invoke(ape_cli, ["tokens", "--help"])
    assert result.exit_code == 0, result.output
