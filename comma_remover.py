import re
import sys
import subprocess
from pathlib import Path


USAGE = "Usage: remove-commas <file_or_directory> [--all] [--dry-run] [--exclude NAME ...]"

DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    ".tox",
    ".nox",
    "__pycache__",
    "site-packages",
    "dist-packages",
    "build",
    "dist",
}


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


def _is_under_excluded_directory(path: Path, root: Path, excluded_dirs: set[str]) -> bool:
    root = root.resolve()
    path = path.resolve()
    rp = root.parts
    pp = path.parts
    if len(pp) <= len(rp) or pp[: len(rp)] != rp:
        return False
    for part in pp[len(rp) : -1]:
        if part in excluded_dirs:
            return True
    return False


def _git_tracked_python_files(root: Path) -> list[Path] | None:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(root), "ls-files", "*.py"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except Exception:
        return None
    return [root / ln for ln in out.splitlines() if ln.strip()]


def iter_python_files(target: Path, *, all_files: bool, excluded_dirs: set[str]) -> list[Path]:
    if target.is_file():
        return [target]

    root = target.resolve()

    if not all_files:
        tracked = _git_tracked_python_files(root)
        if tracked is not None:
            return [p for p in tracked if p.exists()]

    files: list[Path] = []
    for file_path in root.rglob("*.py"):
        if _is_under_dot_prefixed_directory(file_path, root):
            continue
        if _is_under_excluded_directory(file_path, root, excluded_dirs):
            continue
        files.append(file_path)
    return files


def process_file(file_path: Path, *, dry_run: bool) -> bool:
    """
    Process one file.
    Returns True if modified, False otherwise.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    updated = remove_trailing_commas(content)
    if content != updated:
        if not dry_run:
            file_path.write_text(updated, encoding="utf-8")
        print(f"✅ Fixed: {file_path}")
        return True
    return False


def main(argv=None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args:
        print(USAGE)
        return 1

    all_files = False
    dry_run = False
    excluded_dirs = set(DEFAULT_EXCLUDE_DIRS)

    target_str = None
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--all":
            all_files = True
            i += 1
            continue
        if a == "--dry-run":
            dry_run = True
            i += 1
            continue
        if a == "--exclude" and i + 1 < len(args):
            excluded_dirs.add(args[i + 1])
            i += 2
            continue
        target_str = a
        i += 1

    if not target_str:
        print(USAGE)
        return 1

    target = Path(target_str)
    if not target.exists():
        print(f"❌ Target does not exist: {target}")
        return 1

    for file_path in iter_python_files(target, all_files=all_files, excluded_dirs=excluded_dirs):
        process_file(file_path, dry_run=dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())