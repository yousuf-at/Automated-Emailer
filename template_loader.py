from pathlib import Path

DIR = Path(__file__).parent / "templates"

def load(platform: str) -> tuple[str, str]:
    """Template format: first line 'Subject: ...', blank line, then body (no greeting)."""
    raw = (DIR / f"{platform}_generic.txt").read_text(encoding="utf-8")
    first, _, rest = raw.partition("\n")
    subject = first.removeprefix("Subject:").strip()
    return subject, rest.strip()
