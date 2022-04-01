from decimal import Decimal
from typing import Any

from ape.api import ConverterAPI
from ape.exceptions import ConversionError
from ape.logging import logger
from ape.utils import cached_property
from tokenlists import TokenListManager


class TokenConversions(ConverterAPI):
    """Converts token amounts like `100 LINK` to 1e18"""

    _did_warn_no_lists_installed = False

    @cached_property
    def manager(self) -> TokenListManager:
        return TokenListManager()

    def is_convertible(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False

        if " " not in value or len(value.split(" ")) > 2:
            return False

        _, symbol = value.split(" ")

        provider = self.network_manager.active_provider
        if not provider:
            raise ConversionError("Must be connected to a provider to use the token converter.")
        try:
            tokens = self.manager.get_tokens(chain_id=provider.network.chain_id)
        except ValueError as err:
            if not self._did_warn_no_lists_installed:
                logger.warn_from_exception(err, "There are no token lists installed")
                self._did_warn_no_lists_installed = True
            return False
        token_map = map(lambda t: t.symbol, tokens)

        return symbol in token_map

    def convert(self, value: str) -> int:
        value, symbol = value.split(" ")

        provider = self.network_manager.active_provider
        assert provider  # Really just to help mypy

        assert self.manager  # Really just to help mypy
        token = self.manager.get_token_info(symbol, chain_id=provider.network.chain_id)

        return int(Decimal(value) * 10**token.decimals)
