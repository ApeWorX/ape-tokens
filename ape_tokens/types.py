from typing import Any

from ape.contracts.base import ContractCallHandler, ContractInstance
from ape.types import ContractType
from ape.utils import ManagerAccessMixin, cached_property
from eth_utils import to_checksum_address
from tokenlists import TokenInfo

ERC20 = ContractType.model_validate(
    {
        "contractName": "ERC20",
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


class CachedCallHandler(ContractCallHandler):
    _cached_value: Any

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self._cached_value


class TokenInstance(ContractInstance, ManagerAccessMixin):
    # NOTE: Subclass this so that we don't create a breaking interface (still is a ContractInstance)
    _token_info: TokenInfo | None = None

    # Cached "immutable" method calls (skip RPC request, return cached token info)
    @cached_property
    def name(self) -> ContractCallHandler:
        assert self._token_info  # mypy happy
        name_method = self._view_methods_["name"]
        name_method.__class__ = CachedCallHandler
        name_method.__doc__ = """The name of the token (sourced from 'py-tokenlists')"""
        name_method._cached_value = self._token_info.name
        return name_method

    @cached_property
    def symbol(self) -> ContractCallHandler:
        assert self._token_info  # mypy happy
        symbol_method = self._view_methods_["symbol"]
        symbol_method.__class__ = CachedCallHandler
        symbol_method.__doc__ = """The symbol of the token (sourced from 'py-tokenlists')"""
        symbol_method._cached_value = self._token_info.symbol
        return symbol_method

    @cached_property
    def decimals(self) -> ContractCallHandler:
        assert self._token_info  # mypy happy
        decimals_method = self._view_methods_["decimals"]
        decimals_method.__class__ = CachedCallHandler
        decimals_method.__doc__ = """The decimals of the token (sourced from 'py-tokenlists')"""
        decimals_method._cached_value = self._token_info.decimals
        return decimals_method

    def __repr__(self) -> str:
        return f"<{self.symbol()} {self.address}>"

    @classmethod
    def from_tokeninfo(cls, token_info: "TokenInfo"):
        checksummed_address = to_checksum_address(token_info.address)
        contract_instance = cls.chain_manager.contracts.instance_at(
            checksummed_address,
            contract_type=ERC20,
        )
        contract_instance.__class__ = cls
        contract_instance._token_info = token_info
        return contract_instance
