from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from typing import List, Optional
import re
import webbrowser

from google.api_core import exceptions as api_exceptions
from .structures import ResultContainer
from .queryutils import clean, find_last_word


class CommandNotFound(Exception):
    pass


class CommandError(Warning):
    pass


class Command:
    __metaclass__ = ABCMeta

    @classmethod
    @abstractmethod
    def command(cls) -> (str, bool):
        """
        :return:
            abbreviation of the command
            is case sensitive or not
        """

    @classmethod
    @abstractmethod
    def alias(cls) -> (str, bool):
        """
        :return:
            abbreviation the command
            is case sensitive or not
        """

    @abstractmethod
    def handler(self, cli, **kwargs) -> Optional[ResultContainer]:
        """Run the command
        :param cli: instance of spannercli.main.SpannerCli
        :param kwargs:
        :return:
        """

    @abstractmethod
    def help_message(self) -> List[str]:
        """
        :return:
            List of [Command(abbr), Shortcut and Usage, Description]
        """


class HelpCommand(Command):
    @classmethod
    def command(cls) -> (str, bool):
        return "help", True

    @classmethod
    def alias(cls) -> (str, bool):
        return "\\?", True

    def handler(self, cli, **kwargs) -> ResultContainer:
        available = kwargs.get("commands")
        header = ["Command(abbr)", "Shortcut and Usage", "Description"]
        data = []
        for c in self.uniq_command(available):
            help_message = c.help_message()
            if help_message:
                data.append(c.help_message())

        return ResultContainer(data=data, header=header)

    @staticmethod
    def uniq_command(_commands: OrderedDict):
        """uniq by command and keep order"""
        seen = set()
        for v in _commands.values():
            if v not in seen:
                yield v
            seen.update([v])

    def help_message(self) -> List[str]:
        return [self.command()[0], self.alias()[0], "Show this help."]


class QuitCommand(Command):
    @classmethod
    def command(cls) -> (str, bool):
        return "exit", True

    @classmethod
    def alias(cls) -> (str, bool):
        return "\\q", True

    def handler(self, cli, **kwargs) -> ResultContainer:
        # to send quit signal
        raise EOFError

    def help_message(self) -> List[str]:
        return [self.command()[0], self.alias()[0], "Exit."]


class ChangeDatabase(Command):
    @classmethod
    def command(cls) -> (str, bool):
        return "use", True

    @classmethod
    def alias(cls) -> (str, bool):
        return "\\u", True

    def handler(self, cli, **kwargs) -> ResultContainer:
        query = kwargs.get("text")
        inputs = query.split()
        if len(inputs) != 2:
            raise CommandError(
                "Invalid call to change database, try `use dbname`")
        dbname = clean(inputs[1])
        current_id = cli.database.database_id
        cli.change_database(dbname)

        try:
            cli.query("SELECT 1")
        except api_exceptions.NotFound as e:
            # rollback to current if not found
            cli.change_database(current_id)
            raise CommandError(e) from e

        meta = dict(message="change database to {0}".format(dbname))
        return ResultContainer(data=[], header=[], **meta)

    def help_message(self) -> List[str]:
        return [self.command()[0], self.alias()[0], "Change to a new database."]


class ListTable(Command):
    @classmethod
    def command(cls) -> (str, bool):
        return "SHOW TABLES", False

    @classmethod
    def alias(cls) -> (str, bool):
        return "\\lt", True

    def handler(self, cli, **kwargs) -> ResultContainer:
        sql = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_CATALOG='' AND TABLE_SCHEMA='';"
        return cli.query(sql)

    def help_message(self) -> List[str]:
        return [self.command()[0], self.alias()[0], "List tables."]


class DescribeTable(Command):
    @classmethod
    def command(cls) -> (str, bool):
        return "DESCRIBE", False

    @classmethod
    def alias(cls) -> (str, bool):
        return "\\dt", True

    def handler(self, cli, **kwargs) -> ResultContainer:
        query = clean(kwargs.get("text"))
        if len(query.split()) != 2:
            return ResultContainer(data=[], header=[], message="Missing table name.")

        table = find_last_word(query)
        sql = "SELECT COLUMN_NAME, SPANNER_TYPE, COLUMN_DEFAULT, IS_NULLABLE  FROM INFORMATION_SCHEMA.COLUMNS t"\
              " WHERE t.TABLE_NAME = '{0}' ORDER BY ORDINAL_POSITION ASC;"
        return cli.query(sql.format(table))

    def help_message(self) -> List[str]:
        return [self.command()[0], "\\dt[+], desc [table] ", "Describe table."]


class DescTable(DescribeTable):
    """Yet another alias of DescribeTable command"""
    @classmethod
    def command(cls) -> (str, bool):
        return "DESC", False

    @classmethod
    def alias(cls) -> (str, bool):
        # not available
        return None, False

    def help_message(self) -> List[str]:
        # not available
        return []


class ShowIndexCommand(Command):
    @classmethod
    def command(cls) -> (str, bool):
        return "SHOW INDEX", False

    @classmethod
    def alias(cls) -> (str, bool):
        # not available
        return None, False

    def handler(self, cli, **kwargs) -> Optional[ResultContainer]:
        query = clean(kwargs.get("text"))
        table = find_last_word(query)
        # https://cloud.google.com/spanner/docs/information-schema
        sql = "SELECT c.TABLE_NAME, c.INDEX_NAME, c.INDEX_TYPE, c.COLUMN_NAME, c.SPANNER_TYPE, c.IS_NULLABLE,"\
              " c.COLUMN_ORDERING, i.PARENT_TABLE_NAME, i.IS_UNIQUE, i.IS_NULL_FILTERED, i.INDEX_STATE"\
              " FROM INFORMATION_SCHEMA.INDEX_COLUMNS c"\
              " LEFT JOIN INFORMATION_SCHEMA.INDEXES i ON c.TABLE_NAME = i.TABLE_NAME AND i.INDEX_NAME = c.INDEX_NAME"\
              " WHERE c.TABLE_SCHEMA='' AND c.TABLE_SCHEMA=''"

        if table.upper() != "INDEX":
            sql = sql + " AND c.TABLE_NAME='{0}' AND i.TABLE_NAME = '{0}'"
        sql = sql + " ORDER BY c.TABLE_NAME, c.INDEX_NAME ASC, c.ORDINAL_POSITION ASC;"
        return cli.query(sql.format(table))

    def help_message(self) -> List[str]:
        return [self.command()[0], "", "Show Index (from Table)."]


class ListDatabaseCommand(Command):
    @classmethod
    def command(cls) -> (str, bool):
        return "SHOW DATABASES", False

    @classmethod
    def alias(cls) -> (str, bool):
        return "\\l", True

    def handler(self, cli, **kwargs) -> Optional[ResultContainer]:
        data = []
        databases = cli.list_databases()
        if len(databases) > 0:
            data = [[n] for n in databases]
        return ResultContainer(data=data, header=["Databases"])

    def help_message(self) -> List[str]:
        return [self.command()[0], self.alias()[0], "List databases in current instance."]


class BrowserCommand(Command):
    @classmethod
    def command(cls) -> (str, bool):
        return "browse", True

    @classmethod
    def alias(cls) -> (str, bool):
        return None, False

    def handler(self, cli, **kwargs) -> None:
        url = "https://console.cloud.google.com" \
              "/spanner/" \
              "instances/{instances}" \
              "/databases/{database}" \
              "?project={project}".format(instances=cli.instance.display_name,
                                          database=cli.database.database_id,
                                          project=cli.project)
        webbrowser.open_new_tab(url)

    def help_message(self) -> List[str]:
        return [self.command()[0], "", "Open Google Spanner console in your browser."]


commands = OrderedDict()
for cmd in (
        ChangeDatabase(),
        ListTable(),
        DescribeTable(),
        DescTable(),
        ShowIndexCommand(),
        ListDatabaseCommand(),
        BrowserCommand(),
        HelpCommand(),
        QuitCommand()):
    for attr in (cmd.command(), cmd.alias()):
        name = attr[0]
        if name is None:
            continue
        case_sensitive = attr[1]
        if not case_sensitive:
            commands[name.lower()] = cmd
        commands[name] = cmd


def execute(cli, text: str) -> ResultContainer:
    """

    :param cli:  spannercli.main.SpannerCli
    :param text: input text to prompt
    :return: result of command
    """
    if not text:
        raise CommandNotFound
    command = find(text)
    # special case for help
    if isinstance(command, HelpCommand):
        return command.handler(cli, commands=commands)
    kwargs = {
        "text": text
    }
    return command.handler(cli, **kwargs)


spaces = re.compile(r"\s+")


def find(text: str) -> Command:
    if not text:
        raise CommandNotFound

    # 1st, search by raw input
    text = re.sub(spaces, " ", text)
    text = clean(text)
    found = find_command(text)
    if found is not None:
        return found
    # 2nd, search by startswith thw word
    found = startswith(text)
    if found is not None:
        return found

    raise CommandNotFound


def find_command(key: str) -> Optional[Command]:
    _names = list(commands.keys())
    if key in _names:
        return commands.get(key)
    if key.lower() in _names:
        found = commands.get(key.lower())
        if not found.command()[1]:
            return found
    return None


def startswith(key: str) -> Optional[Command]:
    _names = list(commands.keys())
    for n in _names:
        if key.startswith(n):
            return commands.get(n)
    return None


def keys() -> List[str]:
    return list(commands.keys())
