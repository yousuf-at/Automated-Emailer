"""Webhook receiver. Point your marketing portal's 'new signup' webhook at POST /webhook/signup."""
import hmac
from fastapi import FastAPI, Header, HTTPException, Request
import config, portal, workflow

app = FastAPI()

@app.post("/webhook/signup")
async def signup(request: Request, x_webhook_secret: str = Header(default="")):
    if not hmac.compare_digest(x_webhook_secret, config.WEBHOOK_SECRET):
        raise HTTPException(401, "bad secret")
    raw = await request.json()
    result = workflow.handle_signup(portal.from_portal(raw))
    return {"result": result}

@app.get("/health")
def health():
    return {"ok": True, "dry_run": config.DRY_RUN}
