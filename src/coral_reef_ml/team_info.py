"""Small shared helper for team identity used by generated deliverables."""
from pathlib import Path


def get_team_members(root: Path) -> str:
    """Read the plain-text team names, returning a visible placeholder if unset."""
    path = Path(root) / "TEAM_MEMBERS.txt"
    try:
        names = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        names = ""
    return names or "[Add both names]"
