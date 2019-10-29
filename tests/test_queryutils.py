from spannercli import queryutils


def test_is_write_query():
    # write
    for n in [
        "UPDATE TARGET SET NAME='foo';",
        "DELETE FROM TARGET",
        "INSERT INTO TARGET SET NAME='bar'",
    ]:
        assert queryutils.is_write_query(n)

    # other
    for n in [
        "SELECT * FROM TARGET SET NAME='foo';",
        "CREATE DATABASE TARGET",
        "DROP DATABASE TARGET",
    ]:
        assert not queryutils.is_write_query(n)


def test_is_ddl_query():
    # ddl
    for n in [

        "CREATE DATABASE TARGET",
        "DROP TABLE TARGET",
        "ALTER COLUMN TARGET",
    ]:
        assert queryutils.is_ddl_query(n)

    # other
    for n in [
        "SELECT * FROM TARGET SET NAME='foo';",
        "UPDATE TARGET SET NAME='foo';",
        "DELETE FROM TARGET",
        "INSERT INTO TARGET SET NAME='bar'",
    ]:
        assert not queryutils.is_ddl_query(n)


def test_find_last_word():
    assert queryutils.find_last_word("") == ""
    assert queryutils.find_last_word("SELECT 1") == "1"
    assert queryutils.find_last_word("SELECT 1;") == ""
    assert queryutils.find_last_word("SELECT 1\\G") == "G"
    assert queryutils.find_last_word("CREATE DATABASE test") == "test"


def test_clean():
    assert queryutils.clean(" SELECT 1 ") == "SELECT 1"
    assert queryutils.clean("SELECT 1;") == "SELECT 1"
