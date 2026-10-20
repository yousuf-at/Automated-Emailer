import sqlite3
import config

def _conn():
    c = sqlite3.connect(config.DB_PATH)
    c.execute("""CREATE TABLE IF NOT EXISTS sends (
        signup_id TEXT PRIMARY KEY, platform TEXT, to_email TEXT, variant TEXT,
        status TEXT, subject TEXT, body TEXT, note TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    return c

def seen(signup_id: str) -> bool:
    with _conn() as c:
        return c.execute("SELECT 1 FROM sends WHERE signup_id=?", (signup_id,)).fetchone() is not None

def record(signup_id, platform, to_email, variant, status, subject="", body="", note=""):
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO sends (signup_id,platform,to_email,variant,status,subject,body,note) "
                  "VALUES (?,?,?,?,?,?,?,?)",
                  (signup_id, platform, to_email, variant, status, subject, body, note))

def pending_review():
    with _conn() as c:
        return c.execute("SELECT signup_id,platform,to_email,subject,body FROM sends "
                         "WHERE status='pending_review'").fetchall()

def get(signup_id):
    with _conn() as c:
        return c.execute("SELECT signup_id,platform,to_email,subject,body FROM sends WHERE signup_id=?",
                         (signup_id,)).fetchone()

def set_status(signup_id, status):
    with _conn() as c:
        c.execute("UPDATE sends SET status=? WHERE signup_id=?", (status, signup_id))
