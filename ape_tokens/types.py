from typing import TYPE_CHECKING, Any, cast

from ape.contracts.base import ContractCallHandler, ContractContainer, ContractInstance
from ape.types import ContractType
from eth_utils import to_checksum_address

if TYPE_CHECKING:
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


class ImmutableCallHandler(ContractCallHandler):
    # TODO: Should this move upstream into Ape as `ImmutableCallHandler`?
    _cached_value: Any

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if not hasattr(self, "_cached_value"):
            self._cached_value = super().__call__(*args, **kwargs)

        return self._cached_value


class TokenInstance(ContractInstance):
    # NOTE: Subclass this so that we don't create a breaking interface (still is a ContractInstance)

    def __repr__(self) -> str:
        return f"<{self.symbol()} {self.address}>"

    @classmethod
    def from_tokeninfo(cls, token_info: "TokenInfo"):
        contract_instance = cls.chain_manager.contracts.instance_at(
            to_checksum_address(token_info.address),
            contract_type=ERC20,
            # NOTE: Use default setting for proxy detection as we don't
            #       know if token is proxy (e.g. USDC)
        )

        # NOTE: Patch all of our "immutable" fields with caching call handler subclass
        for field in ("name", "symbol", "decimals"):
            method = contract_instance._view_methods_[field]
            method.__class__ = ImmutableCallHandler
            method.__doc__ = f"""The {field} of the token (sourced from 'py-tokenlists')"""
            method._cached_value = getattr(token_info, field)
            contract_instance._view_methods_[field] = method

        # NOTE: Inject class for custom repr/class instancing
        contract_instance.__class__ = cls

        return contract_instance


class TokenContainer(ContractContainer):
    def __init__(self):
        super().__init__(ERC20)

    def at(self, *args, **kwargs) -> TokenInstance:
        contract_instance = super().at(*args, **kwargs)

        # NOTE: Patch all of our "immutable" fields with caching call handler subclass
        for field in ("name", "symbol", "decimals"):
            method = contract_instance._view_methods_[field]
            method.__class__ = ImmutableCallHandler
            method.__doc__ = f"""The {field} of the token (sourced from 'py-tokenlists')"""
            contract_instance._view_methods_[field] = method

        # NOTE: Inject class for custom repr/class instancing
        contract_instance.__class__ = TokenInstance

        return cast(TokenInstance, contract_instance)


# NOTE: Just ned one singleton
Token = TokenContainer()
