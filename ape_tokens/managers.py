from typing import TYPE_CHECKING

from ape.exceptions import ContractNotFoundError
from ape.utils import ManagerAccessMixin, cached_property
from eth_utils import to_checksum_address
from tokenlists import TokenListManager

from .types import ERC20

if TYPE_CHECKING:
    from ape.contracts import ContractInstance



class TokenManager(ManagerAccessMixin, dict):
    @cached_property
    def _manager(self) -> TokenListManager:
        return TokenListManager()

    def __repr__(self) -> str:
        return f"<ape_tokens.TokenManager default='{self._manager.default_tokenlist}'>"

    def __getitem__(self, symbol: str) -> "ContractInstance":
        try:
            token_info = self._manager.get_token_info(
                symbol, chain_id=self.network_manager.network.chain_id
            )

        except ValueError as err:
            raise KeyError(f"Symbol '{symbol}' is not a known token symbol") from err

        checksummed_address = to_checksum_address(token_info.address)
        try:
            return self.chain_manager.contracts.instance_at(checksummed_address)
        except ContractNotFoundError:
            return self.chain_manager.contracts.instance_at(
                checksummed_address, contract_type=ERC20
            )
