from ape.contracts import ContractInstance

from ape_tokens import tokens


def test_tokens():
    assert tokens is not None

    # Show is the same
    from ape_tokens import tokens as tokens2

    assert id(tokens2) == id(tokens)


def test_immutable():
    # Test if we are able to access tokens as `ContractInstance` objects
    # NOTE: Also checks our Ape config loading feature
    usdc = tokens["USDC"]
    assert isinstance(usdc, ContractInstance)
    # NOTE: Canonical address of USDC on Ethereum Mainnet
    assert usdc.address == "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

    # Test our "immutable" call logic doesn't break things
    # NOTE: the `name` is actually incorrect w/ `CoinGecko` tokenlist
    assert usdc.symbol() == "USDC"
    assert usdc.decimals() == 6


def test_getattr():
    assert tokens.USDC == tokens["USDC"]


def test_iter():
    assert len(tokens) > 0
    assert next(iter(tokens))
