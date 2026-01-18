import os
from decimal import Decimal

from silverback import SilverbackBot

from ape_tokens import BalanceManager, tokens

# Initialize bot first (initializing `BalanceManager` requires network connection)
bot = SilverbackBot()

# Create balance watcher for specific token(s)
TOKEN = tokens[SYMBOL := os.environ.get("TOKEN", "USDT")]
balances = BalanceManager(TOKEN)  # NOTE: use the default tokenlist by omitting any `*tokens`

# Monitor balance updates for specific account(s), using above configured tokens
# NOTE: 0xaA8b...3efb is kraken's USDT hot wallet, so monitor will be very active
ADDRESS = os.environ.get("ADDRESS", "0xaA8ba7D4611437141192e7ceCed531Bc0A133efb")
balances.monitor(bot, ADDRESS)  # NOTE: can monitor more accounts by adding more `*addresses` here
# NOTE: `balances.monitor(bot)` will just track the bot's signer address


@bot.on_metric(f"{SYMBOL}/{ADDRESS}")
async def check(balance: Decimal):
    # NOTE: Metric value may temporarily mismatch on-chain if multiple balance updates occur in
    #       the same block, so take care to double-check the answer if it is critical to operation
    #       see: https://github.com/ApeWorX/silverback/issues/290
    onchain_balance = TOKEN.balanceOf(ADDRESS) / Decimal(10 ** TOKEN.decimals())

    assert not (diff := balance - onchain_balance), f"Cache mismatched by {diff} {SYMBOL}"


if bot.signer:
    # NOTE: Will never happen in practice, but a good demo for how to use balance metrics
    @bot.on_metric(f"{SYMBOL}/{ADDRESS}", lt=Decimal(100))
    async def refill(balance: Decimal):
        TOKEN.transfer(ADDRESS, f"{100 - balance} {SYMBOL}", sender=bot.signer)
