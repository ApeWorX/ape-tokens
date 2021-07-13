from decimal import Decimal

import tokenlists  # type: ignore
from ape.api import ConverterAPI
from ape.api.contracts import ContractInstance


def get_token(symbol: str, chain_id: int = None) -> ContractInstance:
    token_info = tokenlists.get_token_info(symbol, chain_id=chain_id)

    from ape import Contract

    token = Contract(token_info.address)

    if not isinstance(token, ContractInstance):
        raise Exception(f"Could not find token contract source for '{token.address}'")

    return token


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
