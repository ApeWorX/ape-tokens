from typing import TYPE_CHECKING, Iterable, Iterator, Optional

from ape.contracts import ContractInstance
from ape.exceptions import ConversionError
from ape.logging import get_logger
from ape.types import AddressType
from ape.utils import ManagerAccessMixin, cached_property
from tokenlists import TokenListManager

from .types import Token, TokenInstance

if TYPE_CHECKING:
    from .config import TokensConfig

logger = get_logger(__package__)


class TokenManager(Iterable[TokenInstance]):
    @property
    def config(self) -> "TokensConfig":
        return ManagerAccessMixin.config_manager.get_config("tokens")

    @cached_property
    def _manager(self) -> TokenListManager:
        manager = TokenListManager()

        for required_tokenlist in self.config.required:
            if required_tokenlist.name not in manager.installed_tokenlists:
                if (
                    installed_name := manager.install_tokenlist(required_tokenlist.uri)
                ) != required_tokenlist.name:
                    # TODO: Allow setting custom name via `TokenListManager.install_tokenlist`
                    logger.warning(
                        f"Installed list name '{installed_name}' does not match "
                        f"requirement '{required_tokenlist.name}'. This could be problematic."
                    )

        # TODO: Allow sourcing from multiple lists in `TokenListManager`,
        #       and set priority here instead
        if default_selected := self.config.default:
            manager.set_default_tokenlist(default_selected)

        return manager

    def __repr__(self) -> str:
        return f"<ape_tokens.TokenManager default='{self._manager.default_tokenlist}'>"

    def __getitem__(self, symbol_or_address: str) -> TokenInstance:
        chain_id = ManagerAccessMixin.network_manager.network.chain_id
        try:
            token_info = self._manager.get_token_info(symbol_or_address, chain_id=chain_id)
            # NOTE: Token is in our token list
            return TokenInstance.from_tokeninfo(token_info)

        except ValueError:
            # NOTE: Fallback to loading by address
            address = ManagerAccessMixin.conversion_manager.convert(symbol_or_address, AddressType)
            return Token.at(address)

    def get(self, val: str) -> Optional[TokenInstance]:
        try:
            return self.__getitem__(val)

        except ConversionError:
            return None

    def __contains__(self, obj: object) -> bool:
        if isinstance(obj, str):
            return self.get(obj) is not None

        elif isinstance(obj, ContractInstance):
            return self.get(obj.address) is not None

        return False

    def __getattr__(self, symbol: str) -> TokenInstance:
        try:
            return self[symbol]
        except KeyError as e:
            raise AttributeError(str(e)) from None

    def __len__(self) -> int:
        tokenlist = self._manager.get_tokenlist()
        return len(tokenlist.tokens)

    def __iter__(self) -> Iterator[TokenInstance]:
        chain_id = ManagerAccessMixin.network_manager.network.chain_id
        for token_info in self._manager.get_tokens(chain_id=chain_id):
            yield TokenInstance.from_tokeninfo(token_info)
