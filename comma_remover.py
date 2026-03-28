import re
import sys
from pathlib import Path


USAGE = "Usage: remove-commas <file_or_directory>"


def remove_trailing_commas(content: str) -> str:
    """Remove commas directly before closing ), ], or }."""
    # Multi-line case: comma before a closing bracket on the next line.
    content = re.sub(r",(\s*\n\s*)([)\]}])", r"\1\2", content)
    # Single-line case: e.g. [1, 2,]
    content = re.sub(r",(\s*)([)\]}])", r"\1\2", content)
    return content


def _is_under_dot_prefixed_directory(path: Path, root: Path) -> bool:
    """
    True if path sits under a directory whose name starts with '.' (e.g. .venv, .pixi).
    Only directory segments are checked, not the filename.
    """
    root = root.resolve()
    path = path.resolve()
    rp = root.parts
    pp = path.parts
    if len(pp) <= len(rp) or pp[: len(rp)] != rp:
        return False
    for part in pp[len(rp) : -1]:
        if part.startswith(".") and part not in (".", ".."):
            return True
    return False


def iter_python_files(target: Path):
    """Yield Python files from a file or directory target."""
    if target.is_dir():
        root = target.resolve()
        for file_path in target.rglob("*.py"):
            if _is_under_dot_prefixed_directory(file_path, root):
                continue
            yield file_path
    else:
        yield target


def process_file(file_path: Path) -> bool:
    """
    Process one file.
    Returns True if modified, False otherwise.
    """
    content = file_path.read_text(encoding="utf-8")
    updated = remove_trailing_commas(content)
    if content != updated:
        file_path.write_text(updated, encoding="utf-8")
        print(f"✅ Fixed: {file_path}")
        return True
    return False


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print(USAGE)
        return 1

    target = Path(args[0])
    if not target.exists():
        print(f"❌ Target does not exist: {target}")
        return 1

    for file_path in iter_python_files(target):
        process_file(file_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())