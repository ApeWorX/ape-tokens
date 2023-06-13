from ape import plugins
from ape.types import AddressType

from .converters import TokenAmountConverter, TokenSymbolConverter
from .managers import TokenManager as _TokenManager


@plugins.register(plugins.ConversionPlugin)
def converters():
    yield int, TokenAmountConverter
    yield AddressType, TokenSymbolConverter


tokens = _TokenManager()

__all__ = [
    "tokens",
]
