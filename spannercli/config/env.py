# Environment Variables


class EnvironmentVariables(object):
    """EnvironmentVariables is a holder that have environment variables names affects spanner-cli"""

    GCP_PROJECT = "GCP_PROJECT"
    """Google Cloud Project ID"""

    SPANNER_INSTANCE_ID = "SPANNER_INSTANCE_ID"
    """Spanner instance id to connect"""

    SPANNER_DATABASE = "SPANNER_DATABASE"
    """Spanner database name to connect"""

    GOOGLE_APPLICATION_CREDENTIALS = "GOOGLE_APPLICATION_CREDENTIALS"
    """path to Google Project Credential file
    https://cloud.google.com/docs/authentication/getting-started
    """

    PROMPT_TOOLKIT_COLOR_DEPTH = "PROMPT_TOOLKIT_COLOR_DEPTH"
    """Possible color depth values for the output.
    [DEPTH_1_BIT,DEPTH_4_BIT,DEPTH_8_BIT,DEPTH_24_BIT]
    DEPTH_8_BIT is default.
    prompt_toolkit/output/color_depth.py
    """

    GRPC_VERBOSITY = "GRPC_VERBOSITY"
    """Default gRPC logging verbosity
    [DEBUG, INFO, ERROR]
    https://github.com/grpc/grpc/blob/master/doc/environment_variables.md#GRPC_VERBOSITY
    """

    HISTORY_FILE = "SPANNER_CLI_HISTORY"
    """
    path to query history file, default is `~/.spanner-cli-history` defined as Constants.HISTORY_FILE
    """

    PAGER = "PAGER"
    """
    A pager cmd to use, default is /bin/less
    """

    LESS = "LESS"
    """
    Options which are passed to less automatically. default is "-RXF" defined as Constants.LESS_FLAG
    """

    PYGMENT_STYLE = "PYGMENT_STYLE"
    """
    The builtin styles of PYGMENT. default is Constants.PYGMENT_STYLE
    see https://pygments.org/docs/styles/
    """
