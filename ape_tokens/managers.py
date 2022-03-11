from ape.api import Address
from ape.types import ContractType
from ape.utils import cached_property
from eth_utils import to_checksum_address
from tokenlists import TokenListManager

ERC20 = ContractType(
    **{
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
            {
                "type": "function",
                "stateMutability": "nonpayable",
                "name": "transfer",
                "inputs": [
                    {"name": "receiver", "type": "address"},
                    {"name": "amount", "type": "uint256"},
                ],
                "outputs": [{"type": "bool"}],
            },
            {
                "type": "function",
                "stateMutability": "nonpayable",
                "name": "approve",
                "inputs": [
                    {"name": "spender", "type": "address"},
                    {"name": "amount", "type": "uint256"},
                ],
                "outputs": [{"type": "bool"}],
            },
            {
                "type": "function",
                "stateMutability": "view",
                "name": "allowance",
                "inputs": [
                    {"name": "owner", "type": "address"},
                    {"name": "spender", "type": "address"},
                ],
                "outputs": [{"type": "uint256"}],
            },
            {
                "type": "function",
                "stateMutability": "nonpayable",
                "name": "transferFrom",
                "inputs": [
                    {"name": "sender", "type": "address"},
                    {"name": "receiver", "type": "address"},
                    {"name": "amount", "type": "uint256"},
                ],
                "outputs": [{"type": "bool"}],
            },
            {
                "type": "event",
                "name": "Transfer",
                "anonymous": False,
                "inputs": [
                    {"name": "sender", "indexed": True, "type": "address"},
                    {"name": "receiver", "indexed": True, "type": "address"},
                    {"name": "amount", "indexed": False, "type": "uint256"},
                ],
            },
            {
                "type": "event",
                "name": "Approval",
                "anonymous": False,
                "inputs": [
                    {"name": "owner", "indexed": True, "type": "address"},
                    {"name": "spender", "indexed": True, "type": "address"},
                    {"name": "amount", "indexed": False, "type": "uint256"},
                ],
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

    def __getitem__(self, symbol: str) -> Address:
        try:
            token_info = self._manager.get_token_info(symbol)

        except ValueError as e:
            raise KeyError(f"Symbol '{symbol}' is not a known token symbol") from e

        return self._Contract(to_checksum_address(token_info.address), contract_type=ERC20)
