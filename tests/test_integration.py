import pytest
from ape._cli import cli
from click.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


def test_help(runner):
    result = runner.invoke(cli, ["tokens", "--help"])
    assert result.exit_code == 0, result.output
