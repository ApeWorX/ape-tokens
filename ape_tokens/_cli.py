try:
    # TODO: Remove in v0.9
    from tokenlists._cli import cli
except ModuleNotFoundError:
    # NOTE: Support v2+
    from tokenlists.__main__ import cli  # type: ignore[no-redef,import-not-found]

__all__ = ["cli"]
