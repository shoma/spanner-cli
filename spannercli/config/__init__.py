from google.oauth2 import service_account

from .constant import Constants
from .env import EnvironmentVariables


def resolve_credential(credential):
    if credential is not None:
        return service_account.Credentials.from_service_account_file(credential)
    return None


__all__ = [
    "resolve_credential",
    "Constants",
    "EnvironmentVariables"
]
