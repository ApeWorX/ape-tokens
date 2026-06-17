import click
import pytest
from ape.contracts import ContractInstance

from ape_tokens.cli import TokenArg, token_option


def test_default_option_name(runner):
    @click.command()
    @token_option()
    def cli(token):
        click.echo(token.symbol())

    result = runner.invoke(cli, ["--token", "USDC"])
    assert result.exit_code == 0, result.output
    assert "USDC" in result.output


def test_custom_option_name(runner):
    @click.command()
    @token_option("--asset-in")
    def cli(asset_in):
        click.echo(asset_in.symbol())

    result = runner.invoke(cli, ["--asset-in", "USDC"])
    assert result.exit_code == 0, result.output
    assert "USDC" in result.output


def test_multiple_options_stack(runner):
    @click.command()
    @token_option("--asset-in")
    @token_option("--asset-out")
    def cli(asset_in, asset_out):
        click.echo(f"{asset_in.symbol()},{asset_out.symbol()}")

    result = runner.invoke(cli, ["--asset-in", "USDC", "--asset-out", "DAI"])
    assert result.exit_code == 0, result.output
    assert "USDC,DAI" in result.output


def test_short_and_long_param_decls(runner):
    @click.command()
    @token_option("-t", "--token")
    def cli(token):
        click.echo(token.symbol())

    result = runner.invoke(cli, ["-t", "USDC"])
    assert result.exit_code == 0, result.output
    assert "USDC" in result.output


def test_default_help_and_metavar(runner):
    @click.command()
    @token_option()
    def cli(token):
        pass

    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0, result.output
    assert "TOKEN" in result.output
    assert "A token symbol or address" in result.output


def test_help_and_metavar_overridable(runner):
    @click.command()
    @token_option("--asset", help="The asset to use", metavar="ASSET")
    def cli(asset):
        pass

    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0, result.output
    assert "ASSET" in result.output
    assert "The asset to use" in result.output


def test_optional_value_passes_through_as_none(runner):
    @click.command()
    @token_option("--token", required=False)
    def cli(token):
        click.echo("none" if token is None else token.symbol())

    result = runner.invoke(cli, [])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "none"


def test_prompt_does_not_double_wrap(runner):
    captured = {}

    @click.command()
    @token_option(prompt=True)
    def cli(token):
        captured["token"] = token

    result = runner.invoke(cli, input="USDC\n", standalone_mode=False)
    assert result.exit_code == 0, result.output
    assert isinstance(captured["token"], TokenArg)
    assert repr(captured["token"]) == "TokenArg<USDC>"


def test_unknown_symbol_raises_on_use(runner):
    @click.command()
    @token_option()
    def cli(token):
        click.echo(token.symbol())

    result = runner.invoke(cli, ["--token", "NOT_A_REAL_TOKEN_XYZ"])
    assert result.exit_code != 0


def test_custom_callback_overrides_default(runner):
    @click.command()
    @token_option("--asset", callback=lambda _ctx, _param, value: value.upper())
    def cli(asset):
        click.echo(asset)

    result = runner.invoke(cli, ["--asset", "usdc"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "USDC"


def test_resolves_to_contract_instance(runner):
    captured = {}

    @click.command()
    @token_option()
    def cli(token):
        captured["token"] = token

    result = runner.invoke(cli, ["--token", "USDC"], standalone_mode=False)
    assert result.exit_code == 0, result.output
    assert isinstance(captured["token"], TokenArg)
    assert repr(captured["token"]) == "TokenArg<USDC>"
    assert isinstance(captured["token"]._resolve(), ContractInstance)
    assert captured["token"].symbol() == "USDC"


def test_works_with_click_group(runner):
    @click.group()
    def cli():
        pass

    @cli.command()
    @token_option()
    def show(token):
        click.echo(token.symbol())

    result = runner.invoke(cli, ["show", "--token", "USDC"])
    assert result.exit_code == 0, result.output
    assert "USDC" in result.output


@pytest.mark.parametrize("symbol", ["USDC", "DAI", "WETH"])
def test_resolves_common_symbols(runner, symbol):
    @click.command()
    @token_option()
    def cli(token):
        click.echo(token.symbol())

    result = runner.invoke(cli, ["--token", symbol])
    assert result.exit_code == 0, result.output
    assert symbol in result.output
