import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def _bool(name, default):
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes")

DRY_RUN = _bool("DRY_RUN", True)
REVIEW_PERSONALIZED = _bool("REVIEW_PERSONALIZED", True)
USE_LLM_NAME_CHECK = _bool("USE_LLM_NAME_CHECK", True)
CUSTOMIZE_MIN_MEMBERS = int(os.getenv("CUSTOMIZE_MIN_MEMBERS", "3"))

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FROM_ADDRESS = {
    "fieldservicely": os.getenv("FIELDSERVICELY_FROM", "FieldServicely <hello@example.com>"),
    "fieldtask": os.getenv("FIELDTASK_FROM", "FieldTask <hello@example.com>"),
}
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
DB_PATH = os.getenv("DB_PATH", "mailer.db")
