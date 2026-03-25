# Comma Remover

Strips trailing commas before `)`, `]`, and `}` in Python source (multi-line and single-line).

## Install

```bash
pip install .
```

## Use

```bash
remove-commas path/to/file.py    # one file
remove-commas .                  # all *.py under this dir and subdirs
```

Or: `python comma_remover.py <file_or_directory>`

Only `.py` files are touched; modified files are overwritten in place.
