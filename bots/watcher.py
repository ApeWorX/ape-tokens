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
    assert (
        diff := balance - (TOKEN.balanceOf(ADDRESS) / Decimal(10 ** TOKEN.decimals()))
    ) == 0, f"Cache mismatches by {diff} {SYMBOL}"


if bot.signer:

    # NOTE: Will never happen in practice, but a good demo for how to use balance metrics
    @bot.on_metric(f"{SYMBOL}/{ADDRESS}", lt=Decimal(100))
    async def refill(balance: Decimal):
        TOKEN.transfer(ADDRESS, f"{100 - balance} {SYMBOL}", sender=bot.signer)
