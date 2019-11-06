# spanner-cli
[![image](https://img.shields.io/pypi/v/spanner-cli.svg)](https://python.org/pypi/spanner-cli)
[![image](https://img.shields.io/pypi/l/spanner-cli.svg)](https://python.org/pypi/spanner-cli)

A Terminal Client for [Google Cloud Spanner](https://cloud.google.com/spanner/) with Completion and Syntax Highlighting.

Quick Start
-----------
```
pip3 install -U --user spanner-cli
```
or, for the latest develop version
```
pip3 install -U --user git+https://github.com/shoma/spanner-cli
```

### Usage
```
Usage: spanner-cli [OPTIONS]

  A Google Cloud Spanner terminal client with auto-completion and syntax
  highlighting.

  https://github.com/shoma/spanner-cli

Options:
  -p, --project TEXT     Google Cloud Platform Project for spanner.
                         ${GCP_PROJECT}  [required]
  -i, --instance TEXT    Google Cloud Spanner instance to connect.
                         ${SPANNER_INSTANCE_ID}  [required]
  -d, --database TEXT    Google Cloud Spanner Database to connect.
                         ${SPANNER_DATABASE}  [required]
  -c, --credential PATH  path to credential file for Google Cloud Platform.
                         ${GOOGLE_APPLICATION_CREDENTIALS}
  --pager / --no-pager   use ${PAGER} (default LESS) to print output.
                         [default: False]
  -e, --execute TEXT     Execute command and quit.
  -v, --version          show version.
  --debug                Debug mode.
  --help                 Show this message and exit.
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
- build on top of [prompt\-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit), [pallets/click](https://github.com/pallets/click)
- inspired by [dbcli](https://github.com/dbcli), [yfuruyama/spanner\-cli](https://github.com/yfuruyama/spanner-cli)
