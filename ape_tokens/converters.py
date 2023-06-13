from decimal import Decimal
from typing import Any, Iterator

from ape.api import ConverterAPI
from ape.exceptions import ConversionError, ProviderNotConnectedError
from ape.logging import logger
from ape.types import AddressType
from ape.utils import cached_property
from tokenlists import TokenInfo, TokenListManager


class _BaseTokenConverter(ConverterAPI):
    _did_warn_no_lists_installed = False

    @cached_property
    def manager(self) -> TokenListManager:
        return TokenListManager()

    def get_tokens(self) -> Iterator[TokenInfo]:
        try:
            provider = self.provider
        except ProviderNotConnectedError as e:
            raise ConversionError(
                "Must be connected to a provider to use the token converter."
            ) from e

        try:
            return self.manager.get_tokens(chain_id=provider.network.chain_id)
        except ValueError as err:
            if not self._did_warn_no_lists_installed:
                logger.warn_from_exception(err, "There are no token lists installed")
                self._did_warn_no_lists_installed = True

            return iter([])


class TokenAmountConverter(_BaseTokenConverter):
    """Converts token amounts like `100 LINK` to 1e18"""

    def is_convertible(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False

        if " " not in value or len(value.split(" ")) > 2:
            return False

        _, symbol = value.split(" ")

        token_map = map(lambda t: t.symbol, self.get_tokens())

        return symbol in token_map

    def convert(self, value: str) -> int:
        value, symbol = value.split(" ")

        provider = self.network_manager.active_provider
        assert provider  # Really just to help mypy

        token = self.manager.get_token_info(symbol, chain_id=provider.network.chain_id)

        return int(Decimal(value) * 10**token.decimals)


class TokenSymbolConverter(_BaseTokenConverter):
    """Converts token symbols like `LINK` to their address"""

    def is_convertible(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False

        token_map = map(lambda t: t.symbol, self.get_tokens())

        return value in token_map

    def convert(self, symbol: str) -> AddressType:
        token = self.manager.get_token_info(symbol, chain_id=self.provider.network.chain_id)

        return AddressType(token.address)  # type: ignore[arg-type]
