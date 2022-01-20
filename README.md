# Ape Token Utilities

A series of utilities for working with tokens, based on the [`py-tokenlists`](https://github.com/ApeWorX/py-tokenlists).

## Dependencies

* [python3](https://www.python.org/downloads) version 3.7 or greater, python3-dev

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

### Python Usage

One of the main reasons to use the `ape-tokens` plugin is to have nicer UX for providing token amounts to contract transactions.
For example, let's say you have a smart-contract named `MyContract` with a function `provideLinkToken()` that takes a decimal value of `LINK` tokens.
The following is an example script that deploys the contract and makes a transaction by expressing the value of LINK as `8.23 LINK`:

```python
from ape import accounts, project

my_account = accounts[0]
contract = my_account.deploy(project.MyContract)

contract.provideLinkTokens("8.23 LINK")
```

Alternatively, if you need the converted value returned to you, you can use the `convert` tool from the root `ape` namespace:

```python
from ape import convert

convert("100.1234 BAT", int)
```

Lastly, to get information about a token, including its contract address, you can do so by importing the `tokens` member from the root `ape_tokens` namespace:

```python
from ape_tokens import tokens

bat = tokens["BAT"]

print(bat.address)
```

## Development

This project is in development and should be considered a beta.
Things might not be in their final state and breaking changes may occur.
Comments, questions, criticisms and pull requests are welcomed.

## License

This project is licensed under the [Apache 2.0](LICENSE).