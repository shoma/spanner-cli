# spanner-cli
[![image](https://img.shields.io/pypi/v/spanner-cli.svg)](https://python.org/pypi/spanner-cli)
[![image](https://img.shields.io/pypi/l/spanner-cli.svg)](https://python.org/pypi/spanner-cli)

A Terminal Client for [Google Cloud Spanner](https://cloud.google.com/spanner/) with Completion and Syntax Highlighting.

Quick Start
-----------
```
pip3 install -U --user spanner-cli
```

### Usage
```
usage: spanner-cli [-h] -p PROJECT -i INSTANCE [-d DATABASE] [-c CREDENTIAL]
                   [-e EXECUTE]

A Google Cloud Spanner terminal client with auto-completion and syntax
highlighting.

optional arguments:
  -h, --help            show this help message and exit
  -p PROJECT, --project PROJECT
                        Google Cloud Platform Project for spanner.
  -i INSTANCE, --instance INSTANCE
                        Google Cloud Spanner instance to connect.
  -d DATABASE, --database DATABASE
                        Google Cloud Spanner Database to connect.
  -c CREDENTIAL, --credential CREDENTIAL
                        path to credential file for Google Cloud Platform.
  -e EXECUTE, --execute EXECUTE
                        Execute command and quit.

https://github.com/shoma/spanner-cli
```

```
> help
+----------------+-----------------------+----------------------------------------------+
| Command(abbr)  | Shortcut and Usage    | Description                                  |
+----------------+-----------------------+----------------------------------------------+
| use            | \u                    | Change to a new database.                    |
| SHOW TABLES    | \lt                   | List tables.                                 |
| DESCRIBE       | \dt[+], desc [table]  | Describe table.                              |
| SHOW INDEX     |                       | Show Index (from Table).                     |
| SHOW DATABASES | \l                    | List databases in current instance.          |
| browse         |                       | Open Google Spanner console in your browser. |
| help           | \?                    | Show this help.                              |
| exit           | \q                    | Exit.                                        |
+----------------+-----------------------+----------------------------------------------+
```
And, you can also edit query with readline's keybindings.
see https://readline.kablamo.org/emacs.html

### Note
- build on top of [prompt\-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)
- inspired by [dbcli](https://github.com/dbcli)
