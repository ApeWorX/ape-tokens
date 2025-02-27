from typing import TYPE_CHECKING, Iterator

from ape.logging import get_logger
from ape.utils import ManagerAccessMixin, cached_property
from tokenlists import TokenListManager

from .types import TokenInstance

if TYPE_CHECKING:
    from ape.contracts import ContractInstance

    from .config import TokensConfig

logger = get_logger(__package__)


class TokenManager(ManagerAccessMixin, dict):
    @property
    def config(self) -> "TokensConfig":
        return self.config_manager.get_config("tokens")

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

    def __getitem__(self, symbol: str) -> "ContractInstance":
        try:
            token_info = self._manager.get_token_info(
                symbol, chain_id=self.network_manager.network.chain_id
            )

        except ValueError as err:
            raise KeyError(f"Symbol '{symbol}' is not a known token symbol") from err

        return TokenInstance.from_tokeninfo(token_info)

    def __len__(self) -> int:
        tokenlist = self._manager.get_tokenlist()
        return len(tokenlist.tokens)

    def __iter__(self) -> Iterator["ContractInstance"]:
        for token_info in self._manager.get_tokens(chain_id=self.network_manager.network.chain_id):
            yield TokenInstance.from_tokeninfo(token_info)
