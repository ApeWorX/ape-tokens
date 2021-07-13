from ape import plugins
from ape.managers.converters import SIGNED_INTEGERS, UNSIGNED_INTEGERS

from .converters import TokenConversions


@plugins.register(plugins.ConversionPlugin)
def converters():
    for abi_type in SIGNED_INTEGERS + UNSIGNED_INTEGERS:
        yield abi_type, TokenConversions
