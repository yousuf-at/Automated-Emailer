"""The decision logic. Step 1: which platform. Step 2: platform-specific rules."""
import config, store, mailer, template_loader as templates
from classify import is_generic_domain, email_domain, greeting_for_fieldservicely
from portal import Signup

def _finish(s, to_email, variant, subject, body, greeting, hold=False):
    full = f"{greeting}\n\n{body}"
    if hold:
        store.record(s.id, s.platform, to_email, variant, "pending_review", subject, full)
        print(f"[hold] {s.id}: personalised email saved for review (run review.py)")
        return "pending_review"
    try:
        mailer.send(s.platform, to_email, subject, full)
        store.record(s.id, s.platform, to_email, variant, "sent", subject, full)
        return "sent"
    except Exception as e:
        # Not recorded as sent, so a retry/redelivery can try again.
        print(f"[error] send failed for {s.id}: {e}")
        return "failed"

def handle_fieldtask(s: Signup) -> str:
    if not s.agency_owner_email:
        store.record(s.id, s.platform, "", "none", "skipped", note="no agency owner email")
        return "skipped: no agency owner email"
    subject, body = templates.load("fieldtask")
    return _finish(s, s.agency_owner_email, "generic", subject, body, "Hi there,")

def handle_fieldservicely(s: Signup) -> str:
    if not s.email:
        store.record(s.id, s.platform, "", "none", "skipped", note="no email")
        return "skipped: no email"
    subject, body = templates.load("fieldservicely")
    greeting = greeting_for_fieldservicely(s.name)

    wants_custom = (s.member_count >= config.CUSTOMIZE_MIN_MEMBERS
                    and not is_generic_domain(s.email))
    if wants_custom:
        from personalize import research_and_draft
        draft = research_and_draft(email_domain(s.email), s.name, s.member_count, subject, body)
        if draft:
            return _finish(s, s.email, "personalized", draft["subject"], draft["body"],
                           greeting, hold=config.REVIEW_PERSONALIZED)
        print(f"[fallback] {s.id}: research failed, using generic")
    return _finish(s, s.email, "generic", subject, body, greeting)

HANDLERS = {"fieldtask": handle_fieldtask, "fieldservicely": handle_fieldservicely}

def handle_signup(s: Signup) -> str:
    if store.seen(s.id):
        return "duplicate: already processed"
    handler = HANDLERS.get(s.platform)
    if not handler:
        store.record(s.id, s.platform, "", "none", "skipped", note="unknown platform")
        return f"skipped: unknown platform '{s.platform}'"
    return handler(s)
