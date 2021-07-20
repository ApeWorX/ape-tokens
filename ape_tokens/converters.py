from decimal import Decimal
from typing import Any

from ape.api import ConverterAPI
from ape.utils import cached_property
from tokenlists import TokenListManager


class TokenConversions(ConverterAPI):
    """Converts token amounts like `100 LINK` to 1e18"""

    @cached_property
    def manager(self) -> TokenListManager:
        return TokenListManager()

    def is_convertible(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False

        if " " not in value or len(value.split(" ")) > 2:
            return False

        _, symbol = value.split(" ")

        provider = self.networks.active_provider
        if not provider:
            raise Exception("Not connected to a provider!")

        tokens = self.manager.get_tokens(chain_id=provider.network.chain_id)

        return symbol in map(lambda t: t.symbol, tokens)

    def convert(self, value: str) -> int:
        value, symbol = value.split(" ")

        provider = self.networks.active_provider
        assert provider  # Really just to help mypy

        assert self.manager  # Really just to help mypy
        token = self.manager.get_token_info(symbol, chain_id=provider.network.chain_id)

        return int(Decimal(value) * 10 ** token.decimals)
