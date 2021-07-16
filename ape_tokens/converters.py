from decimal import Decimal
from typing import Any, Optional

from ape.api import ConverterAPI
from tokenlists import TokenListManager


class TokenConversions(ConverterAPI):
    """Converts token amounts like `100 LINK` to 1e18"""

    manager: Optional[TokenListManager] = None

    def __post_init__(self):
        self.manager = TokenListManager()

    def is_convertible(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False

        if " " not in value or len(value.split(" ")) > 2:
            return False

        _, symbol = value.split(" ")

        provider = self.networks.active_provider
        if not provider:
            raise Exception("Not connected to a provider!")

        assert self.manager  # Really just to help mypy
        tokens = self.manager.get_tokens(chain_id=provider.network.chain_id)

        return symbol in map(lambda t: t.symbol, tokens)

    def convert(self, value: str) -> int:
        value, symbol = value.split(" ")

        provider = self.networks.active_provider
        assert provider  # Really just to help mypy

        assert self.manager  # Really just to help mypy
        token = self.manager.get_token_info(symbol, chain_id=provider.network.chain_id)

        return int(Decimal(value) * 10 ** token.decimals)
