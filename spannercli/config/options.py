import argparse
from spannercli.__version__ import version


def create_option_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spanner-cli",
        description='A Google Cloud Spanner terminal client with auto-completion and syntax highlighting.',
        epilog=f"https://github.com/shoma/spanner-cli version: {version}")
    parser.add_argument("-p", "--project", type=str, required=True,
                        help="Google Cloud Platform Project for spanner.")
    parser.add_argument("-i", "--instance", type=str, required=True,
                        help="Google Cloud Spanner instance to connect.")
    parser.add_argument("-d", "--database", type=str,
                        help="Google Cloud Spanner Database to connect.")
    parser.add_argument("-c", "--credential", type=str,
                        help="path to credential file for Google Cloud Platform.")
    parser.add_argument("-e", "--execute", type=str,
                        help="Execute command and quit.")
    parser.add_argument("--debug", type=bool, nargs='?', const=True, default=False,
                        help="Debug mode.")
    return parser
