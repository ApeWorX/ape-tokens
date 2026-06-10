from ape.api import PluginConfig
from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict


class ListInfo(BaseModel):
    # TODO: Allow `| None` and source from installed list
    #       (requires install by '.uri' instead of name)
    # NOTE: Doesn't seem to be a way to check the URI?
    name: str
    uri: str


class TokensConfig(PluginConfig):
    default: str | None = None  # TODO: Remove in v1.0
    required: list[ListInfo] = []
    order: list[str] | None = None

    model_config = SettingsConfigDict(env_prefix="APE_TOKENS_")
