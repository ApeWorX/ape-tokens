import asyncio
import os
from decimal import Decimal

from silverback import SilverbackBot
from silverback.exceptions import CircuitBreaker

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
    await asyncio.sleep(2)  # NOTE: Add some de-bounce

    if balance != (TOKEN.balanceOf(ADDRESS) / Decimal(10 ** TOKEN.decimals())):
        raise CircuitBreaker("Balances are off!")
