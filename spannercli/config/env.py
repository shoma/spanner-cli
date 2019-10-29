# Environment Variables


class EnvironmentVariables(object):
    """str: path to Google Project Credential file
    https://cloud.google.com/docs/authentication/getting-started
    """
    GOOGLE_APPLICATION_CREDENTIALS = "GOOGLE_APPLICATION_CREDENTIALS"

    """str: Possible color depth values for the output.
    [DEPTH_1_BIT,DEPTH_4_BIT,DEPTH_8_BIT,DEPTH_24_BIT]
    DEPTH_8_BIT is default.
    prompt_toolkit/output/color_depth.py
    """
    PROMPT_TOOLKIT_COLOR_DEPTH = "PROMPT_TOOLKIT_COLOR_DEPTH"

    """str: Default gRPC logging verbosity
    [DEBUG, INFO, ERROR]
    https://github.com/grpc/grpc/blob/master/doc/environment_variables.md#GRPC_VERBOSITY
    """
    GRPC_VERBOSITY = "GRPC_VERBOSITY"

    """
    path to query history file, default is `~/.spanner-cli-history` defined as Constants.HISTORY_FILE
    """
    HISTORY_FILE = "SPANNER_CLI_HISTORY"
