from ape import plugins

from .converters import TokenConversions


@plugins.register(plugins.ConversionPlugin)
def converters():
    yield int, TokenConversions
