from decimal import Decimal

from ape.api import ConverterAPI
from tokenlists import TokenInfo, TokenListManager  # type: ignore

manager = TokenListManager()


def get_token(symbol: str, chain_id: int = None) -> TokenInfo:
    breakpoint()
    return manager.get_token_info(symbol, chain_id=chain_id)


class TokenConversions(ConverterAPI):
    """Converts token amounts like `100 LINK` to 1e18"""

    def is_convertible(self, value: str) -> bool:
        try:
            return self.convert(value) is not None

        except Exception:
            return False

    def convert(self, value: str) -> int:
        value, symbol = value.split(" ")

        provider = self.networks.active_provider
        if not provider:
            raise Exception("Not connected to a provider!")

        token = get_token(symbol, chain_id=provider.network.chain_id)

        return int(Decimal(value) * 10 ** token.decimals)
