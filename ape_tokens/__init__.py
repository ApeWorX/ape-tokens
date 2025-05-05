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
    "Token",
    "TokenInstance",
    "TokenAmountConverter",
    "TokenSymbolConverter",
]
