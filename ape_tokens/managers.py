from collections.abc import Iterable, Iterator
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, cast

from tokenlists import TokenListManager

from ape.contracts import ContractInstance
from ape.exceptions import ConversionError
from ape.logging import get_logger
from ape.types import AddressType
from ape.utils import ManagerAccessMixin, cached_property

from .types import ConvertsToToken, Token, TokenInstance

if TYPE_CHECKING:
    from silverback import SilverbackBot

    from ape.api.address import BaseAddress

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

    def filter(self, tags: Optional[set[str]] = None) -> Iterator[TokenInstance]:
        chain_id = ManagerAccessMixin.network_manager.network.chain_id
        tag_ids = {
            tag_id
            for tag_id in (self._manager.get_tokenlist().tags or [])
            if tag_id in (tags or set())
        }

        # TODO: Move `tags=tags` of `tokenlists.TokenListManager.get_tokens`
        for token_info in self._manager.get_tokens(chain_id=chain_id):
            if tags is None or set(token_info.tags) <= tag_ids:
                yield TokenInstance.from_tokeninfo(token_info)

    def __iter__(self) -> Iterator[TokenInstance]:
        yield from self.filter()  # NOTE: No filter applied = all tokens


class TokenBalances(ManagerAccessMixin):
    def __init__(self, token: TokenInstance):
        self.token = token

        # NOTE: Only used if live-tracking
        self._balances: dict[AddressType, Decimal] = dict()

    def get(self, acct: "BaseAddress | AddressType | str") -> Decimal:
        """
        Get on-chain token balance by address, symbol, or contract instance.

        NOTE: Does **not** use cached value.
        """

        return self.token.balanceOf(acct) / Decimal(10 ** self.token.decimals())

    def __getitem__(self, acct: "BaseAddress | AddressType | str") -> Decimal:
        """
        Get token balance by address, symbol, or contract instance.

        NOTE: Uses cached value, if available.
        """
        address = self.conversion_manager.convert(acct, AddressType)

        # NOTE: Don't update `self._balances` (only `.monitor` can)
        if balance := self._balances.get(address):
            return balance

        return self.get(address)

    def monitor(self, bot: "SilverbackBot", *addresses: AddressType):
        from silverback.types import TaskType

        if len(addresses) == 0:
            raise ValueError("No addresses to monitor")

        # Startup task: Load current balances for all watched addresses
        async def load_balances(_):
            if len(addresses) > 1:
                from ape_ethereum import multicall
                from ape_ethereum.multicall.exceptions import UnsupportedChainError

                try:
                    call = multicall.Call()
                except UnsupportedChainError:
                    call = multicall.Call.inject()

                # NOTE: Should be fine to do only one loop for a reasonable # of addresses (<100)
                for address in addresses:
                    call.add(self.token.balanceOf, address)

                for address, raw_balance in zip(addresses, call()):
                    self._balances[address] = raw_balance / Decimal(10 ** self.token.decimals())

            else:  # NOTE: Just call directly if only 1
                self._balances[addresses[0]] = self.token.balanceOf(addresses[0]) / Decimal(
                    10 ** self.token.decimals()
                )

        # NOTE: Namespace the function to avoid conflicts
        load_balances.__name__ = f"tokens:{self.token.symbol()}:load-balances"
        bot.broker_task_decorator(TaskType.STARTUP)(load_balances)

        # Create individual event handlers per token per address
        # This improves efficiency by leveraging event filtering
        # NOTE: creates O(A) event filters, for O(T * A) total, but reduces total RPC sub events
        # TODO: Once Ape supports OR filter args, use that to reduce to only O(1)
        for idx, address in enumerate(addresses):

            async def balance_acquired(log):
                amount = Decimal(log.amount) / Decimal(10 ** self.token.decimals())

                if log.removed:
                    # Reorg: reverse the acquisition
                    self._balances[address] -= amount
                else:  # Normal: record acquisition
                    self._balances[address] += amount

                return {f"{self.token.symbol()}/{address}": self._balances[address]}

            # NOTE: Namespace the function to avoid conflicts, requires globally-unique name
            balance_acquired.__name__ = f"tokens:{self.token.symbol()}:acquisition{idx}"
            bot.broker_task_decorator(
                TaskType.EVENT_LOG,
                container=self.token.Transfer,
                filter_args=dict(receiver=address),
            )(balance_acquired)

            async def balance_disposed(log):
                amount = Decimal(log.amount) / Decimal(10 ** self.token.decimals())

                if log.removed:
                    # Reorg: reverse the disposition (add back)
                    self._balances[address] += amount
                else:  # Normal: record disposition
                    self._balances[address] -= amount

                return {f"{self.token.symbol()}/{address}": self._balances[address]}

            # NOTE: Namespace the function to avoid conflicts, requires globally-unique name
            balance_disposed.__name__ = f"tokens:{self.token.symbol()}:disposition{idx}"
            bot.broker_task_decorator(
                TaskType.EVENT_LOG,
                container=self.token.Transfer,
                filter_args=dict(sender=address),
            )(balance_disposed)


class BalanceManager(ManagerAccessMixin):
    """
    Fetch token balances in Decimal format for a given set of tokens.

    ```{note}
    This class is capable of maintaining an in-memory balance cache, using Silverback.
    ```

    Usage example::

        >>> from ape.utils import ZERO_ADDRESS
        >>> from ape_tokens import BalanceManager
        >>>
        >>> # NOTE: No arguments to constructor defaults to loading configured tokenlist
        >>> balances = BalanceManager()
        >>> balances["USDC"][ZERO_ADDRESS]
        Decimal(0)  # Because USDC makes it illegal to send to 0x0

    Usage with Silverback::

        >>> from decimal import Decimal
        >>> from ape_tokens import BalanceManager, tokens
        >>> from silverback import SilverbackBot
        >>>
        >>> bot = SilverbackBot()
        >>> usdc = tokens["USDC"]
        >>>
        >>> # NOTE: This controls the amount of live indexing to just the given tokens
        >>> balances = BalanceManager(usdc, "DAI", "WETH")
        >>> # Watch balances of given tokens for `bot.signer` (if configured) and other accounts
        >>> balances.monitor(bot, *some_accounts)
        >>> # OR only watch `bot.signer` (raises if no signer configured)
        >>> balances.monitor(bot)
        >>>
        >>> @bot.on_metric("indicator", gt=TRADE_THRESHOLD)
        >>> async def perform_trade(indicator: Decimal):
        >>>     uni.swap(
        >>>         have=usdc,
        >>>         want="OTHER",
        >>>         # Access token balance directly (uses in-memory cached value):
        >>>         amount_in=indicator * balances[usdc][bot.signer],
        >>>         sender=bot.signer,
        >>>     )
        >>>
        >>> # Use metrics from monitoring to trigger alerts or other actions:
        >>> @bot.on_metric(f"USDC/{address}", lt=Decimal("100"))
        >>> async def add_inventory(balance: Decimal):
        ...     usdc.transfer(address, "100 USDC", sender=bot.signer)
    """

    def __init__(self, *tokens: ConvertsToToken):
        """
        Initialize a BalanceManager for one or more tokens (defaults to configured tokenlist).

        Args:
            *tokens: One or more tokens to monitor, by address or symbol.
                If not provided, the configured default tokenlist will be loaded and used.

        ```{important}
        When used with Silverback (`.monitor` activated), this will monitor balances from **all**
        tokens given in the constructor args. It is recommended to limit the number of tokens being
        monitored to a reasonable level (2 event log handlers per token are installed in `bot`).
        ```

        """

        if tokens:
            tokens = tuple(
                (
                    Token.at(self.conversion_manager.convert(t, AddressType))
                    if not isinstance(t, TokenInstance)
                    else t
                )
                for t in tokens
            )

        else:
            # Use default tokenlist
            from .main import tokens as tokens_manager

            tokens = tuple(tokens_manager)

        # NOTE: This is **only** to be updated by Silverback in `.monitor`
        self._token_balances: dict[AddressType, TokenBalances] = {
            token: TokenBalances(token) for token in cast(tuple[TokenInstance], tokens)
        }

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"<{cls_name} tokens={len(self._token_balances)}>"

    def __getitem__(self, token: ConvertsToToken) -> TokenBalances:
        """Get token balance reader for token by address, symbol, or contract instance."""

        if not isinstance(token, TokenInstance):
            token = Token.at(self.conversion_manager.convert(token, AddressType))

        if not (balances := self._token_balances.get(token)):
            raise KeyError(f"Not watching {token}")

        return balances

    def get(self, token: ConvertsToToken) -> TokenBalances | None:
        """
        Get token balance reader for token by address, symbol, or contract instance.

        If not configured (or not in tokenlist), returns `None`.
        """

        try:
            return self.__getitem__(token)

        except KeyError:
            return None

    def get_balance(
        self,
        token: ConvertsToToken,
        account: "BaseAddress | AddressType | str",
    ) -> Decimal:
        return self[token][account]

    def monitor(
        self,
        bot: "SilverbackBot",
        *accounts: "BaseAddress | AddressType | str",
    ):
        """
        Install the balance monitor on a Silverback bot, for all configured tokens.

        This class monitors ERC20 Transfer events for all configured tokens and maintains an
        in-memory cache of balances that updates in real-time based on blockchain events. It
        properly handles blockchain reorganizations by reverting balance changes when events
        are removed.

        The monitor automatically publishes metrics in the format "{symbol}/{address}",
        which can be used with Silverback's `@bot.on_metric(...)` decorator to trigger
        alerts or other actions based on balance updates or threshold filters.

        Args:
            bot: The `silverback.SilverbackBot` instance to install monitoring on.
            *accounts: Other accounts to watch. Includes `bot.signer`. (if one is configured)

        ```{important}
        This method registers multiple event handlers with the bot to track Transfer events
        for the specified tokens and maintain up-to-date balance information. It is recommended
        **not** to install the monitor for too many accounts and tokens at once, as it creates
        `2 * (# of tokens) * (# of accounts)` event log filters, which could dramatically increase
        your RPC utilization and/or exceed hosted service limits in practice.
        ```
        """
        if not (
            addresses := [
                *([bot.signer.address] if bot.signer else []),
                *map(lambda a: self.conversion_manager.convert(a, AddressType), accounts),
            ]
        ):
            raise ValueError(
                "Must either provide a set of accounts to watch, or enable `bot.signer`."
            )

        for token_balances in self._token_balances.values():
            token_balances.monitor(bot, *addresses)
