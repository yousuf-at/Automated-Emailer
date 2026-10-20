"""Adapter for the marketing portal. THIS IS THE ONLY FILE YOU NEED TO ADAPT
to your portal's field names / API."""
from dataclasses import dataclass
import re

# Map our field names -> the portal's field names. Edit the right-hand side.
FIELD_MAP = {
    "id": "signup_id",
    "platform": "platform",
    "name": "name",
    "email": "email",
    "agency_owner_email": "agency_owner_email",
    "member_count": "member_count",
}

@dataclass
class Signup:
    id: str
    platform: str            # "fieldservicely" | "fieldtask" | other
    name: str
    email: str               # registered email
    agency_owner_email: str  # used by FieldTask
    member_count: int        # used by FieldServicely

def normalize_platform(value: str) -> str:
    v = re.sub(r"[^a-z]", "", (value or "").lower())
    if "fieldservicely" in v:
        return "fieldservicely"
    if "fieldtask" in v:
        return "fieldtask"
    return v

def from_portal(raw: dict) -> Signup:
    g = lambda k: raw.get(FIELD_MAP[k])
    try:
        members = int(g("member_count") or 0)
    except (TypeError, ValueError):
        members = 0
    return Signup(
        id=str(g("id")),
        platform=normalize_platform(g("platform")),
        name=(g("name") or "").strip(),
        email=(g("email") or "").strip().lower(),
        agency_owner_email=(g("agency_owner_email") or "").strip().lower(),
        member_count=members,
    )

def fetch_new_signups() -> list[dict]:
    """Polling mode: call your portal's API and return raw signup dicts.
    Not needed if your portal can send webhooks instead."""
    raise NotImplementedError("Implement against your portal's API")
