from ape._cli import cli


def test_help(runner):
    result = runner.invoke(cli, ("tokens", "--help"))
    assert result.exit_code == 0, result.output
