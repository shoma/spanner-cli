import pytest
from spannercli import commands


def test_help_command():
    sut = commands.HelpCommand()
    cmd, alias, msg = sut.help_message()
    assert cmd == "help"
    assert alias == "\\?"
    assert msg == "Show this help."


def test_help_command_handler():
    class DummyCommand:
        def help_message(self):
            return ["Command", "Shortcut", "Description"]

    class OtherCommand:
        def help_message(self):
            return ["foo", "bar", "hoge"]

    class NoHelpCommand:
        def help_message(self):
            return []

    cmds = {"dummy": DummyCommand(), "none": NoHelpCommand(), "other": OtherCommand()}
    sut = commands.HelpCommand()
    res = sut.handler(None, commands=cmds)
    for h in res.header:
        assert h in ["Command(abbr)", "Shortcut and Usage", "Description"]
    assert len(res.data) == 2
    assert all([a == b for a, b in zip(res.data[0], ["Command", "Shortcut", "Description"])])


def test_find_command():
    with pytest.raises(commands.CommandNotFound):
        commands.find("")

    with pytest.raises(commands.CommandNotFound):
        commands.find("NoSuchCommand")

    # small case
    cmd = commands.find("desc")
    assert type(cmd) is commands.DescTable

    # uppercase
    cmd = commands.find("DESC")
    assert type(cmd) is commands.DescTable

    # mixed case
    cmd = commands.find("DesC")
    assert type(cmd) is commands.DescTable

    cmd = commands.find("browse")
    assert type(cmd) is commands.BrowserCommand

    # double words
    cmd = commands.find("show index")
    assert type(cmd) is commands.ShowIndexCommand

    # double words with mixed case
    cmd = commands.find("show INDEX")
    assert type(cmd) is commands.ShowIndexCommand

    # double words with extra space
    cmd = commands.find(" show  index ")
    assert type(cmd) is commands.ShowIndexCommand

    # BrowserCommand is case sensitive
    with pytest.raises(commands.CommandNotFound):
        commands.find("BrOwSE")
    with pytest.raises(commands.CommandNotFound):
        commands.find("BROWSE")
