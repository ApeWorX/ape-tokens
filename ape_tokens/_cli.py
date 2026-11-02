try:
  from tokenlists._cli import cli
except ModuleNotFoundError:
  # NOTE: Support v2+
  # TODO: Remove in v0.9
  from tokenlists.__main__ import cli

__all__ = ["cli"]
