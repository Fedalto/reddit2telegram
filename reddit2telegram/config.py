import os
from dataclasses import dataclass
from distutils.version import Version, StrictVersion

from reddit2telegram.version import version


@dataclass
class Configuration:
    version: Version

    reddit_client_id: str
    reddit_client_secret: str

    telegram_token: str


def _read_env(env_name: str):
    env = os.getenv(env_name)
    if env is None:
        raise RuntimeError(f"Missing configuration: {env_name}")
    return env


settings = Configuration(
    version=StrictVersion(version),
    reddit_client_id=_read_env("reddit_client_id"),
    reddit_client_secret=_read_env("reddit_client_secret"),
    telegram_token=_read_env("telegram_token"),
)
