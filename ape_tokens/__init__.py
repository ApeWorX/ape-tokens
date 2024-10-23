from typing import Any

from ape import plugins
from ape.types.address import AddressType


@plugins.register(plugins.ConversionPlugin)
def converters():
    from .converters import TokenAmountConverter, TokenSymbolConverter

    yield int, TokenAmountConverter
    yield AddressType, TokenSymbolConverter


tokens = None  # NOTE: Initialized lazily


def __getattr__(name: str) -> Any:
    if name == "tokens":

        global tokens
        if tokens is None:
            from .managers import TokenManager as _TokenManager

            tokens = _TokenManager()

        return tokens

    else:
        raise AttributeError(name)


__all__ = [
    "tokens",
]
