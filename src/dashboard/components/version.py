"""Public Git revision for verifying the Streamlit deployment."""
import re
import subprocess
from pathlib import Path


def get_git_revision(root: Path | None = None) -> str:
    """Return the checkout SHA, or an explicit unknown value outside Git."""
    root = root if root is not None else Path(__file__).resolve().parents[3]
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--verify', 'HEAD'],
            cwd=root, capture_output=True, text=True, check=True, timeout=2,
        )
    except (OSError, subprocess.SubprocessError):
        return 'desconocida'
    revision = result.stdout.strip()
    return revision if re.fullmatch(r'[0-9a-f]{40}', revision) else 'desconocida'
