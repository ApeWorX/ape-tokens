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

To see all the available CLI commands, type:

```bash
ape tokens --help
```

To use the `ConversionAPI` (via `ape.convert`) in your python script, import `convert` from ape:

```python
from ape import convert

converted_val = convert("10 BAT", int)
print(converted_val)  # prints 10000000000000000000
```

## Development

This project is in development and should be considered a beta.
Things might not be in their final state and breaking changes may occur.
Comments, questions, criticisms and pull requests are welcomed.

## License

This project is licensed under the [Apache 2.0](LICENSE).