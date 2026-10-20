import requests
import config
from links import to_html, to_plain, extract_urls

def send(platform: str, to_email: str, subject: str, body: str) -> None:
    """`body` may contain [Label](url) links; they are sent as clickable HTML
    with a plain-text fallback."""
    if config.DRY_RUN:
        print(f"\n[DRY RUN] {platform} -> {to_email}\nSubject: {subject}\n\n{to_plain(body)}")
        print(f"Links in email: {extract_urls(body)}\n{'-'*50}")
        return
    r = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {config.RESEND_API_KEY}"},
        json={"from": config.FROM_ADDRESS[platform], "to": [to_email], "subject": subject,
              "html": to_html(body), "text": to_plain(body)},
        timeout=20,
    )
    r.raise_for_status()
