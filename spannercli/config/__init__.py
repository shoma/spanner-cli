import os

from google.oauth2 import service_account
import pygments.styles

from .constant import Constants
from .env import EnvironmentVariables


def resolve_credential(credential):
    if credential is not None:
        return service_account.Credentials.from_service_account_file(credential)
    return None


def get_pygment_style():
    e = os.getenv(EnvironmentVariables.PYGMENT_STYLE)
    if e is None:
        return Constants.PYGMENT_STYLE
    if e not in pygments.styles.STYLE_MAP.keys():
        return Constants.PYGMENT_STYLE
    return e


__all__ = [
    "resolve_credential",
    "Constants",
    "EnvironmentVariables"
]
