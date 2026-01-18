# Example Bots

This directory contains example Silverback bots demonstrating `ape-tokens` integrations.

## Balance Watcher Example

**File:** `watcher.py`

A demonstration bot that shows how to use the `BalanceManager.monitor` function to monitor token balances in real-time using Silverback.

### Features

- **Real-time Tracking**: Monitor USDT transfers to and from Kraken's hot wallet on Ethereum mainnet
- **Balance Verification**: Shows cached balances match on-chain balances
- **Balance Threshold Action**: Sends some tokens when balance fall below a specified threshold

### How It Works

The bot uses `BalanceManager.monitor` to monitor ERC20 Transfer events and maintains an in-memory cache of token balances.
Each time a Transfer occurs, the monitoring:

1. Updates internal cached balance for the matching address
2. Returns metrics labeled using the format `f"{symbol}/{address}"`

### Running the Bot

```bash
uvx --with ape-tokens silverback watcher --network :mainnet
```

### Customization

Fork this bot and implement your own ideas!

Try:

- Changing which tokens to monitor in the `watcher.install()` call
- Adjusting balance thresholds in the `@bot.on_metric()` decorators
- Adding additional addresses to watch: `BalanceWatcher(address1, address2, ...)`
- Monitoring all tokens from the default tokenlist: `watcher.install(bot)` (without specifying tokens)
