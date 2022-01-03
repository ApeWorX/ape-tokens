from ape import plugins

from .converters import TokenConversions
from .managers import TokenManager as _TokenManager


@plugins.register(plugins.ConversionPlugin)
def converters():
    yield int, TokenConversions


tokens = _TokenManager()

__all__ = [
    "tokens",
]
