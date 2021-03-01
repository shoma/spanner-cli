import logging
import os
import sys
import warnings

from google.cloud import spanner
from google.cloud.spanner_v1 import types
from google.api_core import exceptions as api_exceptions
from google.api_core.gapic_v1 import client_info
import click
from cli_helpers import tabular_output
from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.completion import DynamicCompleter
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import style_from_pygments_cls
from prompt_toolkit.input import posix_pipe
from prompt_toolkit.filters import HasFocus, IsDone
from prompt_toolkit.layout.processors import (HighlightMatchingBracketProcessor,
                                              ConditionalProcessor)
from pygments.styles import get_style_by_name

from spannercli import __version__
from spannercli import config, commands, structures, lexer, queryutils
from spannercli.completion import SQLCompleter


class SpannerCli(object):
    client = None
    instance = None
    database = None
    project = None
    history = None

    def __init__(self, project=None, instance=None, database=None, credentials=None, with_pager=False,
                 inp=None, output=None):
        # setup environment variables
        # less option for pager
        if not os.environ.get(config.EnvironmentVariables.LESS):
            os.environ[config.EnvironmentVariables.LESS] = config.Constants.LESS_FLAG
        self.with_pager = with_pager
        self.logger = logging.getLogger('spanner-cli')
        self.logger.debug("Staring spanner-cli project=%s, instance=%s, database=%s", project, instance, database)
        self.project = project
        with warnings.catch_warnings(record=True) as warns:
            warnings.simplefilter("always")
            self.client = spanner.Client(
                project=self.project,
                credentials=credentials,
                client_info=client_info.ClientInfo(user_agent=__name__),
            )
            if len(warns) > 0:
                for w in warns:
                    self.logger.debug(w)
                    click.echo(message=w.message, err=True, nl=True)

        self.instance = self.client.instance(instance)
        self.database = self.instance.database(database)
        self.prompt_message = self.get_prompt_message()
        self.completer = SQLCompleter()
        self.open_history_file()
        self.rehash()
        self.session = PromptSession(
            message=self.prompt_message,
            lexer=PygmentsLexer(lexer.SpannerLexer),
            completer=DynamicCompleter(lambda: self.completer),
            style=style_from_pygments_cls(get_style_by_name(config.get_pygment_style())),
            history=self.history,
            auto_suggest=AutoSuggestFromHistory(),
            input_processors=[ConditionalProcessor(
                processor=HighlightMatchingBracketProcessor(
                    chars='[](){}'),
                filter=HasFocus(DEFAULT_BUFFER) & ~IsDone()  # pylint: disable=invalid-unary-operand-type
            )],
            input=inp,
            output=output,
        )

        self.formatter = tabular_output.TabularOutputFormatter('ascii')

    def rehash(self):
        """
        rehashing for completion
        """
        self.set_completion_databases()
        self.set_completion_tables()
        self.set_completion_columns()

    def set_completion_databases(self):
        data = self.list_databases()
        self.completer.set_databases(data)

    def set_completion_tables(self):
        sql = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_CATALOG='' AND TABLE_SCHEMA='';"
        res = self.read_query(sql)
        tables = []
        for d in res.data:
            tables.append(d[0])
        self.completer.set_tables(tables)

    def set_completion_columns(self):
        sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_CATALOG='' AND TABLE_SCHEMA='' "
        res = self.read_query(sql)
        columns = []
        for d in res.data:
            columns.append(d[0])
        self.completer.set_columns(columns)

    def open_history_file(self):
        history_file = os.path.expanduser(os.environ.get(config.EnvironmentVariables.HISTORY_FILE,
                                                         config.Constants.HISTORY_FILE))
        if os.path.exists(os.path.dirname(history_file)):
            self.history = FileHistory(history_file)
        else:
            self.history = None

    def get_prompt_message(self) -> str:
        return f"Spanner [{self.project}/{self.instance.display_name}/{self.database.database_id}]:\n> "

    def list_databases(self):
        data = []
        try:
            databases = self.instance.list_databases()
            for d in databases:
                data.append(d.database_id)
        except api_exceptions.GoogleAPIError as e:
            # google.api_core.exceptions.PermissionDenied, if does not have sufficient permission
            self.logger.exception(e)
        return data

    def change_database(self, dbname):
        self.database = self.instance.database(dbname)
        self.prompt_message = self.get_prompt_message()

    def query(self, sql) -> structures.ResultContainer:
        self.logger.debug("QUERY: %s", sql)
        if queryutils.is_write_query(sql):
            return self.write_query(sql)
        if queryutils.is_ddl_query(sql):
            return self.ddl_query(sql)
        return self.read_query(sql)

    def read_query(self, sql) -> structures.ResultContainer:
        meta = {}
        if sql.strip().endswith('\\G'):
            meta['format'] = 'vertical'
            sql = sql[:-2]

        with self.database.snapshot() as snapshot:
            result_set = snapshot.execute_sql(sql,
                                              query_mode=types.spanner.ExecuteSqlRequest.QueryMode.PROFILE)
            data = []
            limit = config.Constants.MAX_RESULT
            count = 0
            for row in result_set:
                data.append(row)
                count = count+1
                if count > limit:
                    break
            header = []
            for h in result_set.fields:
                header.append(h.name)
            message = ""
            if result_set.stats:
                # stats.query_stats
                # {
                #   'elapsed_time': string_value: "0.91 msecs",
                #   'query_text': string_value: "select 1;"
                #   'rows_scanned': string_value: "0",
                #   'rows_returned': string_value: "1",
                #   'cpu_time': string_value: "0.23 msecs",
                #   'runtime_creation_time': string_value: "0 msecs",
                #   'query_plan_creation_time': string_value: "0.23 msecs"
                # }
                message = "rows_returned: {returned:,}, " \
                    "scanned: {scanned:}, " \
                    "elapsed_time: {elapsed}, " \
                    "cpu_time:{cpu}".format(
                        returned=int(result_set.stats.query_stats['rows_returned']),
                        scanned=int(result_set.stats.query_stats['rows_scanned']),
                        elapsed=result_set.stats.query_stats['elapsed_time'],
                        cpu=result_set.stats.query_stats['cpu_time'],
                    )
            if count > limit and message == "":
                message = f"returns over limit: {limit}, aborted to read all results, stats is not available."
            meta['message'] = message

        return structures.ResultContainer(
            data=data,
            header=header,
            **meta
        )

    def write_query(self, sql: str) -> structures.ResultContainer:
        meta = {}

        def execute(transaction):
            status, sequence = transaction.batch_update([sql])
            if status.code != 0:
                raise ValueError(f"code={status.code}, {status.message}")
            meta['message'] = f"{sequence[0]} row affected."

        self.database.run_in_transaction(execute)
        return structures.ResultContainer(
            data=[],
            header=[],
            **meta
        )

    def ddl_query(self, sql: str) -> structures.ResultContainer:
        sql = queryutils.clean(sql)
        if sql.upper().startswith("CREATE DATABASE") or sql.upper().startswith("DROP DATABASE"):
            return self.create_or_drop_database(sql)
        meta = {}
        operation = self.database.update_ddl([sql])
        operation.result()
        meta['message'] = "operation done."
        self.rehash()
        return structures.ResultContainer(
            data=[],
            header=[],
            **meta
        )

    def create_or_drop_database(self, sql: str) -> structures.ResultContainer:
        meta = {}
        database_id = queryutils.find_last_word(sql)
        database = self.instance.database(database_id, [])
        if sql.startswith("CREATE"):
            operation = database.create()
            operation.result()
            meta['message'] = f"Created database {database_id} on instance {self.instance.display_name}"
        elif sql.startswith("DROP"):
            database.drop()
            meta['message'] = f"Drop database {database_id} on instance {self.instance.display_name}"
        else:
            raise NotImplementedError(f"NotImplemented operation: {sql}")

        self.rehash()
        return structures.ResultContainer(
            data=[],
            header=[],
            **meta
        )

    def interact(self):  # pylint: disable=too-many-return-statements
        try:
            text = self.session.prompt(self.prompt_message)
        except KeyboardInterrupt:
            return
        except EOFError as e:
            raise e
        else:
            if not text.strip():
                return

        try:
            # command
            result = commands.execute(self, text)
            if result is not None:
                self.output(result)
            return
        except api_exceptions.GoogleAPIError as e:
            self.logger.exception(e)
            print("\n", e, "\n")
            return
        except EOFError as e:
            self.logger.exception(e)
            raise e
        except commands.CommandError as e:
            self.logger.exception(e)
            print("\n", e, "\n")
            return
        except commands.CommandNotFound:
            pass

        try:
            # query
            result = self.query(text)
            self.output(result)
            return
        except api_exceptions.GoogleAPICallError as e:
            message = "\n" + bytes(e.message, "utf8").decode("unicode_escape") + "\n"
            click.secho(message=message, err=True, nl=True, fg="red")
            self.logger.exception(e)
            return
        except Exception as e:  # pylint: disable=broad-except
            click.secho(message="\n" + str(e) + "\n", err=True, nl=True, fg="red")
            self.logger.exception(e)

    def output(self, result: structures.ResultContainer):
        if len(result) > 0:
            opt = {
                'dialect': 'unix',
                'disable_numparse': True,
                'preserve_whitespace': True,
                'column_types': str,
            }
            format_name = result.format()
            if format_name is not None:
                opt['format_name'] = format_name

            formatted = self.formatter.format_output(
                result.data, result.header, **opt)
            if self.with_pager:
                click.echo_via_pager("\n".join(list(formatted)))
            else:
                for n in formatted:
                    click.secho(n)
        result.print_message()

    def run(self):
        try:
            while True:
                self.interact()
        except EOFError:
            print("bye")

    def batch(self, query):
        if query is None:
            buf = []
            for l in sys.stdin:
                buf.append(l)
            query = ''.join(buf)
        try:
            # query
            result = self.query(query.strip())
            result.meta['format'] = "tsv"
            result.meta['message'] = None
            self.output(result)
            return
        except api_exceptions.InvalidArgument as e:
            message = "\n" + bytes(e.message, "utf8").decode("unicode_escape") + "\n"
            click.secho(message=message, err=True, nl=True)
            self.logger.exception(e)
            sys.exit(1)
        except Exception as e:  # pylint: disable=broad-except
            click.secho(message="\n" + str(e) + "\n", err=True, nl=True)
            self.logger.exception(e)
            sys.exit(1)


def is_batch(execute):
    return execute is not None or not sys.stdin.isatty()


def initialize_logger(debug=False):
    logging.basicConfig()
    handler = logging.NullHandler()
    level = logging.CRITICAL
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s - %(message)s')

    if debug:
        logfile = os.path.expanduser(config.Constants.LOGFILE)
        level = logging.DEBUG
        handler = logging.FileHandler(logfile)
    handler.setFormatter(formatter)
    logger = logging.getLogger('spanner-cli')
    logger.setLevel(level)
    logger.addHandler(handler)

    logger.debug('Initialized the logger for debug')


@click.command()
@click.option("-p", "--project", envvar=config.EnvironmentVariables.GCP_PROJECT, required=True,
              help="Google Cloud Platform Project for spanner. ${GCP_PROJECT}")
@click.option("-i", "--instance", envvar=config.EnvironmentVariables.SPANNER_INSTANCE_ID, required=True,
              help="Google Cloud Spanner instance to connect. ${SPANNER_INSTANCE_ID}")
@click.option("-d", "--database", envvar=config.EnvironmentVariables.SPANNER_DATABASE, required=True,
              help="Google Cloud Spanner Database to connect. ${SPANNER_DATABASE}")
@click.option("-c", "--credential", envvar=config.EnvironmentVariables.GOOGLE_APPLICATION_CREDENTIALS,
              type=click.Path(exists=True),
              help="path to credential file for Google Cloud Platform. ${GOOGLE_APPLICATION_CREDENTIALS}")
@click.option('--pager/--no-pager', default=False, show_default=True,
              help="use ${PAGER} (default LESS) to print output.")
@click.option("-e", "--execute", help="Execute command and quit.")
@click.option("-v", "--version", is_flag=True, help="show version.")
@click.option("--debug", help="Debug mode.", is_flag=True)
def main(project, instance, database, credential, pager, execute, version, debug):
    """A Google Cloud Spanner terminal client with auto-completion and syntax highlighting.

    https://github.com/shoma/spanner-cli
    """
    if version:
        print('spanner-cli:', __version__)
        sys.exit(0)
    initialize_logger(debug)
    batch_mode = is_batch(execute)
    if batch_mode:
        cli = SpannerCli(
            project=project,
            instance=instance,
            database=database,
            credentials=config.resolve_credential(credential),
            inp=posix_pipe.PosixPipeInput()
        )
        cli.batch(execute)
        sys.exit(0)

    cli = SpannerCli(
        project=project,
        instance=instance,
        database=database,
        credentials=config.resolve_credential(credential),
        with_pager=pager,
    )
    cli.run()


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
