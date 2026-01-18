from typing import Any

from ape import plugins


@plugins.register(plugins.Config)
def config_class():
    from .config import TokensConfig

    return TokensConfig


@plugins.register(plugins.ConversionPlugin)
def converters():
    from ape.types.address import AddressType

    from .converters import TokenAmountConverter, TokenSymbolConverter

    yield int, TokenAmountConverter
    yield AddressType, TokenSymbolConverter


def __getattr__(name: str) -> Any:
    if name == "tokens":
        from .main import tokens

        return tokens

    elif name == "BalanceManager":
        from .managers import BalanceManager

        return BalanceManager

    elif name == "ConvertsToToken":
        from .types import ConvertsToToken

        return ConvertsToToken

    elif name == "Token":
        from .types import Token

        return Token

    elif name == "TokenInstance":
        from .types import TokenInstance

        return TokenInstance

    elif name == "TokenAmountConverter":
        from .converters import TokenAmountConverter

        return TokenAmountConverter

    elif name == "TokenSymbolConverter":
        from .converters import TokenSymbolConverter

        return TokenSymbolConverter

    else:
        raise AttributeError(name)


__all__ = [
    "tokens",
    "BalanceManager",
    "ConvertsToToken",
    "Token",
    "TokenInstance",
    "TokenAmountConverter",
    "TokenSymbolConverter",
]
