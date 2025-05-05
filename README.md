# Quick Start

A series of utilities for working with tokens, based on the [`py-tokenlists`](https://github.com/ApeWorX/py-tokenlists).

## Dependencies

- [python3](https://www.python.org/downloads) version 3.8 up to 3.12.

## Installation

### via `pip`

You can install the latest release via [`pip`](https://pypi.org/project/pip/):

```bash
pip install ape-tokens
```

### via `setuptools`

You can clone the repository and use [`setuptools`](https://github.com/pypa/setuptools) for the most up-to-date version:

```bash
git clone https://github.com/ApeWorX/ape-tokens.git
cd ape-tokens
python3 setup.py install
```

## Quick Usage

### CLI Usage

First, install a token list, such as the `1inch` token list, which contains many tokens that you can use:

```bash
ape tokens install tokens.1inch.eth
```

To see all the tokens you can use, run command:

```bash
ape tokens list-tokens
```

To see other available CLI commands, run:

```bash
ape tokens --help
```

### Configuration

You can configure this plugin (and by extension, configure `py-tokenlists`) using the config file:

```yaml
# ape-config.yaml
tokens:
  default: "My Default List"
  required:
    - name: "My Default List"
      uri: "http://example.com/tokenlist.json"
```

You can also configure this plugin via Environment Variable:

```sh
APE_TOKENS_DEFAULT="My Default List"
APE_TOKENS_REQUIRED='[{"name":"My Default List","uri":"http://example.com/tokenlist.json"}]'
```

Configuration like this may be useful for operating in a cloud environment

### Ape Console Extras

The `tokens` manager object is very useful for improving your ape experience.
You can install it as a ["console namespace extra"](https://docs.apeworx.io/ape/stable/userguides/console.html#namespace-extra) by adding the following lines to your project's `./ape_console_extras.py` or your global `$HOME/.ape/ape_console_extras.py`:

```py
...

try:
    from ape_tokens import tokens
except ImportError:
    pass  # Plugin not installed, skip

...
```

This way, whenever you use `ape console` (with this plugin installed) you will have `tokens` available immediately without having to import it!

### Python Usage

One of the main reasons to use the `ape-tokens` plugin is to have nicer UX for providing token amounts to contract transactions.
For example, let's say you have a smart-contract named `MyContract` with a function `provideLinkToken()` that takes a decimal value of `LINK` tokens.
The following is an example script that deploys the contract and makes a transaction by expressing the value of LINK as `8.23 LINK`:

```python
from ape import accounts, project

my_account = accounts[0]
contract = my_account.deploy(project.MyContract)

tx = contract.provideLinkTokens("8.23 LINK", sender=me)
```

Alternatively, if you need the converted value returned to you, you can use the `convert` tool from the root `ape` namespace:

```python
from ape import convert

convert("100.1234 BAT", int)
```

This plugin also provides a conversion function for addresses, for example if you want to use a `.swap` function that takes two address inputs which are expected to be tokens (as well as a 3rd argument which is an amount of the 1st token), you can do:

```python
tx = swapper.swap("BAT", "LINK", "10 BAT", sender=me)
```

To get information about a token, including its contract address, you can do so by importing the `tokens` member from the root `ape_tokens` namespace:

```python
from ape_tokens import tokens

bat = tokens["BAT"]

print(bat.address)
print(bat.symbol())
```

You can also work with the `tokens` object in an iterable context, such as iterating over a set of tokens in your token list:

```python
from ape_tokens import tokens

for token in tokens:
    print(token.balanceOf(me))
```

Or in a mapping context (similar to using it like a dict):

```python
assert "BAT" in tokens

if bat := tokens.get("BAT"):
    print("BAT is in our token list!")
```
