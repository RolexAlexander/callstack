"""Generic codebase ingestion -- this is what lets the support agent spin
up on ANY codebase, not just the one it happens to be demoed on.

Given a local path or a git URL (public or private -- private works if
your local git/gh credentials already have access, exactly like `git
clone` would), reads the README plus a sampling of real source files and
returns a grounded technical knowledge snapshot, capped to a reasonable
size so the diagnosis prompt doesn't blow its context budget.

This replaced an earlier, hand-curated, single-codebase-specific snapshot
(see process-notes.md) -- that version worked but wasn't actually generic,
and was accidentally built against a private repo. This version is real:
point it at any repo you have access to.
"""

import subprocess
import tempfile
from pathlib import Path

SOURCE_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".rb"}
EXCLUDE_DIRS = {
    "node_modules", ".git", "dist", "build", "__pycache__", ".venv", "venv",
    ".next", "target", "vendor", "coverage",
}
MAX_CONTEXT_CHARS = 60_000
MAX_FILE_CHARS = 8_000


def ingest_codebase(source: str) -> str:
    """Build a technical knowledge snapshot from any codebase.

    Args:
        source: A local directory path, or a git URL (https:// or git@).
            Private repos work if your local git credentials already have
            access -- this behaves exactly like a normal `git clone`.

    Returns:
        A markdown-formatted string: the README plus a sampling of real
        source files, capped at MAX_CONTEXT_CHARS.
    """
    if source.startswith(("http://", "https://", "git@")):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                ["git", "clone", "--depth", "1", source, tmp],
                check=True,
                capture_output=True,
                timeout=60,
            )
            return _read_repo(Path(tmp))
    return _read_repo(Path(source))


def _read_repo(root: Path) -> str:
    chunks: list[str] = []
    total = 0

    readme = _find_readme(root)
    if readme:
        text = _truncate(readme.read_text(encoding="utf-8", errors="ignore"))
        chunk = f"# README\n{text}"
        chunks.append(chunk)
        total += len(chunk)

    for path in sorted(root.rglob("*")):
        if total >= MAX_CONTEXT_CHARS:
            break
        if path.is_dir() or any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        if path.suffix not in SOURCE_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if not text.strip():
            continue
        rel = path.relative_to(root)
        chunk = f"\n\n# {rel}\n{_truncate(text)}"
        chunks.append(chunk)
        total += len(chunk)

    return "".join(chunks) or "(no readable README or source files found at this location)"


def _find_readme(root: Path) -> Path | None:
    for name in ("README.md", "README.MD", "Readme.md", "readme.md", "README"):
        candidate = root / name
        if candidate.exists():
            return candidate
    return None


def _truncate(text: str) -> str:
    return text[:MAX_FILE_CHARS]
