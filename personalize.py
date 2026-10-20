"""Claude-powered pieces: research a company from its domain and write a
targeted email, plus an optional human-vs-company name check."""
import json
import re
import config
from links import extract_urls, missing_links

def _client():
    import anthropic
    return anthropic.Anthropic()

def _text(resp) -> str:
    return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")

def llm_is_person_name(name: str):
    """True/False, or None if the check failed (caller falls back to heuristic)."""
    try:
        resp = _client().messages.create(
            model=config.CLAUDE_MODEL, max_tokens=5,
            messages=[{"role": "user", "content":
                f'Is "{name}" the name of an individual person (not a business)? '
                "Answer only PERSON or BUSINESS."}],
        )
        out = _text(resp).strip().upper()
        return True if out.startswith("PERSON") else False if out.startswith("BUSINESS") else None
    except Exception as e:
        print(f"[name-check] failed: {e}")
        return None

PROMPT = """You write onboarding emails for FieldServicely (field service management software).

A new organization just signed up. Research the company behind the domain "{domain}" using web search
(what they do, services, size, region, anything relevant to field service work).

Then adapt the GENERIC EMAIL below into a targeted email for this specific company.
Rules:
- Keep the core message, offer and call-to-action of the generic email.
- LINKS ARE MANDATORY: every link in the generic email must appear in your email, with the URL
  copied EXACTLY (character for character, no changes to the URL, no shortening, no tracking
  params added or removed). Keep links in the same [Label](URL) format. You may adjust the
  surrounding sentence so the link fits naturally, but never drop a link or invent new ones.
  Links that must appear: {links}
- Weave in 1-2 genuinely relevant details from your research. Never invent facts. If research is
  thin or you are unsure the company is the right one, stay close to the generic email.
- Do NOT include a greeting line (it is added separately). Do NOT include a signature unless the template has one.
- Plain text, concise.
{feedback}
Signup details: organization name "{org}", team members: {members}.

GENERIC EMAIL
Subject: {subject}

{body}

Respond with ONLY a JSON object: {{"subject": "...", "body": "..."}}"""

def research_and_draft(domain: str, org: str, members: int, subject: str, body: str):
    """Returns {"subject","body"} or None (caller falls back to the generic email).
    A draft is rejected unless it contains every link from the generic template."""
    feedback = ""
    for attempt in (1, 2):
        try:
            resp = _client().messages.create(
                model=config.CLAUDE_MODEL, max_tokens=2000,
                tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 4}],
                messages=[{"role": "user", "content": PROMPT.format(
                    domain=domain, org=org, members=members, subject=subject, body=body,
                    links=", ".join(extract_urls(body)) or "(none)", feedback=feedback)}],
            )
            m = re.search(r"\{.*\}", _text(resp), re.S)
            data = json.loads(m.group(0))
            if not (data.get("subject") and data.get("body")):
                continue
            missing = missing_links(body, data["body"])
            if missing:
                print(f"[personalize] attempt {attempt}: draft missing links {missing}")
                feedback = f"\nYOUR PREVIOUS DRAFT WAS REJECTED because it was missing or altered these links: {missing}. Include them exactly.\n"
                continue
            return {"subject": data["subject"].strip(), "body": data["body"].strip()}
        except Exception as e:
            print(f"[personalize] failed for {domain}: {e}")
    return None
