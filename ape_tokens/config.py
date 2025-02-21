from ape.api import PluginConfig
from pydantic import BaseModel


class ListInfo(BaseModel):
    # TODO: Allow `| None` and source from installed list
    #       (requires install by '.uri' instead of name)
    # NOTE: Doesn't seem to be a way to check the URI?
    name: str
    uri: str


class TokensConfig(PluginConfig):
    default: str | None = None
    required: list[ListInfo] = []
