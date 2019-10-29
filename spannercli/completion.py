from typing import Iterable, List

from prompt_toolkit.completion import Completer, Completion

from spannercli.lexer import syntax, keywords, functions, datatypes, ddl
from spannercli import queryutils, commands


class SQLCompleter(Completer):
    databases: List[str] = []
    tables: List[str] = []
    columns: List[str] = []

    def set_databases(self, databases: List[str]):
        self.databases = databases

    def set_tables(self, tables: List[str]):
        self.tables = tables

    def set_columns(self, columns: List[str]):
        self.columns = columns

    def all_candidates(self):
        return set(list(syntax) + list(keywords) + list(functions) + list(datatypes) + list(ddl) + commands.keys()
                   + self.databases + self.tables + self.columns)

    def get_completions(self, document, complete_event) -> Iterable[Completion]:
        word_before_cursor = document.get_word_before_cursor()
        if len(document.text.split()) == 1:
            # first word
            return self.find_matches(word_before_cursor, set(list(syntax) + list(ddl) + commands.keys()))
        return self.find_matches(word_before_cursor, self.all_candidates())

    # pylint: disable=no-self-use
    def find_matches(self, text: str, collection: Iterable[str]) -> Iterable[Completion]:
        last = queryutils.find_last_word(text)
        text = last.lower()

        completions = []
        for item in sorted(collection):
            match_limit = len(text)
            found = item.lower().find(text, 0, match_limit)
            if found >= 0:
                completions.append(Completion(item, -len(text)))

        return completions
