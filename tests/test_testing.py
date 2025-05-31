from ape_tokens.testing import MockERC20


def test_test_tokens(accounts):
    owner = accounts[0]

    # Inputs: Initial owner, name, symbol, decimals.
    token = MockERC20.deploy(owner, "Test token", "TEST", 18, sender=owner)

    assert token.decimals() == 18
    assert token.name() == "Test token"
    assert token.symbol() == "TEST"
