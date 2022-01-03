from ape.api import AddressAPI
from ape.types import ContractType
from ape.utils import cached_property
from eth_utils import to_checksum_address
from tokenlists import TokenListManager

ERC20 = ContractType.from_dict(
    {
        "contractName": "ERC20",  # type: ignore
        "abi": [
            {
                "type": "function",
                "stateMutability": "view",
                "name": "name",
                "outputs": [{"type": "string"}],
            },
            {
                "type": "function",
                "stateMutability": "view",
                "name": "symbol",
                "outputs": [{"type": "string"}],
            },
            {
                "type": "function",
                "stateMutability": "view",
                "name": "decimals",
                "outputs": [{"type": "uint8"}],
            },
            {
                "type": "function",
                "stateMutability": "view",
                "name": "totalSupply",
                "outputs": [{"type": "uint256"}],
            },
            {
                "type": "function",
                "stateMutability": "view",
                "name": "balanceOf",
                "inputs": [{"name": "holder", "type": "address"}],
                "outputs": [{"type": "uint256"}],
            },
        ],
    }
)


class TokenManager(dict):
    @cached_property
    def _manager(self) -> TokenListManager:
        return TokenListManager()

    @cached_property
    def _Contract(self):
        from ape import Contract

        return Contract

    def __getitem__(self, symbol: str) -> AddressAPI:
        try:
            token_info = self._manager.get_token_info(symbol)

        except ValueError as e:
            raise KeyError(f"Symbol '{symbol}' is not a known token symbol") from e

        return self._Contract(to_checksum_address(token_info.address), contract_type=ERC20)
