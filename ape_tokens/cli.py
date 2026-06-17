from typing import Any

import click


class TokenArg:
    """
    Lazy proxy for a token argument from a Click option.

    Resolution is deferred to first attribute access so the lookup happens inside
    the connected-provider block when ``token_option`` is stacked with
    ``ape.cli.network_option`` (token lookup requires an active network).
    """

    def __init__(self, value: str):
        self._value = value
        self._resolved: Any = None

    def __repr__(self) -> str:
        return f"TokenArg<{self._value}>"

    def __str__(self) -> str:
        return self._value

    def _resolve(self):
        if self._resolved is None:
            from ape_tokens import tokens

            self._resolved = tokens[self._value]
        return self._resolved

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._resolve(), name)


def token_option(*param_decls: str, **kwargs: Any):
    """
    Click option that wraps a token symbol (or address) in a :class:`TokenArg`.

    Defaults to ``--token`` when no parameter declarations are given. The default
    callback returns a :class:`TokenArg` that resolves on first attribute access,
    so the lookup happens inside the command body (where a provider is connected
    when stacked with ``ape.cli.network_option``). Pass ``callback=`` to override.
    ``None`` values pass through unchanged so the option can be optional.

    Usage example::

        @click.command()
        @token_option("--asset-in")
        @token_option("--asset-out")
        def swap(asset_in, asset_out): ...
    """
    if not param_decls:
        param_decls = ("--token",)

    kwargs.setdefault("help", "A token symbol or address")
    kwargs.setdefault("metavar", "TOKEN")

    if "callback" not in kwargs:

        def _wrap_token(_ctx, _param, value):
            return None if value is None else TokenArg(value)

        kwargs["callback"] = _wrap_token

    return click.option(*param_decls, **kwargs)
