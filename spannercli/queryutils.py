import re


def is_write_query(sql: str) -> bool:
    q = ["INSERT", "UPDATE", "DELETE"]
    return True in [sql.upper().startswith(n) for n in q]


def is_ddl_query(sql: str) -> bool:
    q = ["CREATE", "ALTER", "DROP"]
    return True in [sql.upper().startswith(n) for n in q]


def find_last_word(sql: str) -> str:
    # empty
    if not sql:
        return ""
    if sql[-1].isspace():
        return ""

    regex = re.compile(r'(\w+)$')
    matches = regex.search(sql)
    if matches:
        return matches.group(0)

    return ""


def clean(sql: str) -> str:
    sql = sql.strip()
    if sql.endswith(';'):
        sql = sql[:-1]
    return sql
