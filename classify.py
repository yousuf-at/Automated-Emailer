import re
import config

FREE_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "yahoo.co.uk", "ymail.com",
    "outlook.com", "hotmail.com", "hotmail.co.uk", "live.com", "msn.com",
    "microsoft.com", "icloud.com", "me.com", "mac.com", "aol.com",
    "proton.me", "protonmail.com", "pm.me", "gmx.com", "gmx.net", "mail.com",
    "zoho.com", "yandex.com", "yandex.ru", "fastmail.com", "hey.com",
    "comcast.net", "att.net", "verizon.net", "sbcglobal.net", "rocketmail.com",
}

def email_domain(email: str) -> str:
    return email.rsplit("@", 1)[-1].lower().strip()

def is_generic_domain(email: str) -> bool:
    d = email_domain(email)
    return d in FREE_DOMAINS or d.startswith(("yahoo.", "hotmail.", "outlook.", "live."))

COMPANY_WORDS = {
    "llc", "inc", "ltd", "corp", "co", "company", "group", "services", "service",
    "solutions", "systems", "technologies", "tech", "enterprises", "holdings",
    "plumbing", "hvac", "electric", "electrical", "heating", "cooling", "roofing",
    "landscaping", "cleaning", "construction", "contractors", "contracting",
    "maintenance", "repair", "repairs", "mechanical", "pest", "control",
    "agency", "team", "studio", "partners", "associates", "bros", "brothers",
    "sons", "supply", "hardware", "air", "home", "pro", "pros", "express",
    "the", "and",
}

def heuristic_is_person(name: str) -> bool:
    """Conservative: only True when the name clearly looks like a person."""
    name = name.strip()
    if not name or re.search(r"[\d&@/+]", name):
        return False
    tokens = name.split()
    if not 2 <= len(tokens) <= 4:
        return False
    for t in tokens:
        if not re.fullmatch(r"[A-Za-z][A-Za-z.'\-]*", t):
            return False
        if t.lower().strip(".") in COMPANY_WORDS:
            return False
    return True

def is_person_name(name: str) -> bool:
    if not heuristic_is_person(name):
        return False
    if config.USE_LLM_NAME_CHECK:
        from personalize import llm_is_person_name
        verdict = llm_is_person_name(name)
        if verdict is not None:
            return verdict
    return True

def greeting_for_fieldservicely(name: str) -> str:
    if is_person_name(name):
        first = name.split()[0].strip()
        if first == first.lower() or first == first.upper():
            first = first.title()
        return f"Hi {first},"
    return "Hi there,"
