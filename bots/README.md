# Example Bots

This directory contains example Silverback bots demonstrating `ape-tokens` features.

## Balance Watcher Example

**File:** `watcher-example.py`

A demonstration bot that shows how to use the `BalanceWatcher` class to monitor token balances in real-time with Silverback.

### Features

- **Real-time Balance Tracking**: Monitors USDC, DAI, and WETH balances for the bot's signer address
- **Balance Verification**: Includes a circuit breaker that verifies cached balances match on-chain balances
- **Low Balance Alerts**: Triggers notifications when balances fall below specified thresholds:
  - USDC < 100
  - DAI < 50
  - WETH < 0.1
- **Startup Logging**: Displays initial balances when the bot starts

### How It Works

The bot uses `BalanceWatcher` to monitor Transfer events and maintain an in-memory cache of token balances. Each time a transfer occurs, the watcher:

1. Updates the cached balance
2. Returns a metrics dictionary in the format `{f"{symbol}/{address}": balance}`
3. Triggers any `@bot.on_metric()` handlers that match the metric key

The circuit breaker handler verifies data integrity by comparing cached balances against on-chain balances, raising a `CircuitBreaker` exception if there's a mismatch.

### Running the Bot

```bash
# Make sure you have silverback and ape-tokens installed
pip install silverback ape-tokens

# Run the bot (requires a configured network and signer)
silverback run watcher-example:bot --network ethereum:mainnet:alchemy
```

### Customization

You can customize this bot by:

- Changing which tokens to monitor in the `watcher.install()` call
- Adjusting balance thresholds in the `@bot.on_metric()` decorators
- Adding additional addresses to watch: `BalanceWatcher(address1, address2, ...)`
- Monitoring all tokens from the default tokenlist: `watcher.install(bot)` (without specifying tokens)
