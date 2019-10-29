from argparse import Namespace
from google.oauth2 import service_account

from .options import create_option_parser
from .constant import Constants
from .env import EnvironmentVariables


def resolve_credential(args: Namespace):
    if args.credential is not None:
        return service_account.Credentials.from_service_account_file(args.credential)
    return None


__all__ = [
    "Constants",
    "resolve_credential",
    "create_option_parser",
    "EnvironmentVariables"
]
