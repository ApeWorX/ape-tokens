from decimal import Decimal

from brownie import Contract, chain  # type: ignore

import tokenlists


def get_token(symbol: str) -> Contract:
    token_info = tokenlists.get_token_info(symbol, chain_id=chain.id)
    try:
        return Contract(token_info.address)
    except ValueError:
        return Contract.from_explorer(token_info.address)


def convert_token_amount(amount: str) -> int:
    """
    Convert a given "token amount string" into a value.

    NOTE: ETH (and gwei, wei, etc.) take precedence over any tokens
    """
    value_str, symbol = amount.split(" ")
    value = Decimal(value_str)

    if symbol in ("ETH", "WETH"):
        return int(value * 10 ** 18)

    elif symbol == "gwei":
        return int(value * 10 ** 9)

    elif symbol == "wei":
        return int(value)

    else:
        token = get_token(symbol)
        return int(value * 10 ** token.decimals())
