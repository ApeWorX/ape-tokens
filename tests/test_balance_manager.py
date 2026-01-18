import pytest
from ape.utils import ZERO_ADDRESS

from ape_tokens import BalanceManager


def test_balances_init():
    balances = BalanceManager(0x1)
    assert repr(balances) == "<BalanceManager tokens=1>"

    balances = BalanceManager(0x1, 0x2)
    assert repr(balances) == "<BalanceManager tokens=2>"


def test_balances_getitem_unwatched_token():
    balances = BalanceManager(0x1)

    with pytest.raises(KeyError):
        balances[0x2]

    with pytest.raises(KeyError):
        balances.get_balance(0x2, 0x3)


def test_balances_getter_vs_onchain():
    from ape_tokens import tokens

    balances = BalanceManager(usdt := tokens["USDT"])
    assert usdt.balanceOf(ZERO_ADDRESS) == balances["USDT"][ZERO_ADDRESS] * 10 ** usdt.decimals()
