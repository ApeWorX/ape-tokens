from typing import Any

from ape import plugins


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

    else:
        raise AttributeError(name)


__all__ = [
    "tokens",
]
