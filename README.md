# Signup Mailer (FieldServicely + FieldTask)

## Flow
1. Check platform on the new signup.
2. **FieldTask** -> generic FieldTask email to the *Agency Owner Email*, "Hi there,".
3. **FieldServicely** -> email to the registered email.
   - members < CUSTOMIZE_MIN_MEMBERS (default 3) -> generic
   - otherwise generic domain (gmail etc.) -> generic
   - otherwise custom domain -> Claude researches the company and drafts a targeted email
   - Greeting: "Hi Matt," for human names, "Hi there," for company names.

## Setup
1. `pip install -r requirements.txt`; copy `.env.example` to `.env` and fill in.
2. Edit `templates/*_generic.txt` (first line `Subject: ...`, then body with NO greeting).
3. Edit `FIELD_MAP` in `portal.py` to match your marketing portal's field names.
4. Run: `uvicorn app:app --port 8000` and point the portal webhook at `POST /webhook/signup`
   with header `X-Webhook-Secret`. (No webhooks? implement `fetch_new_signups()` and run `python poll.py`.)
5. Keep `DRY_RUN=true` until the logged emails look right, then set it to false.

## Links
Write links in templates as `[Label](https://url)` or a bare `https://url`. They are sent as clickable
HTML with a plain-text fallback. In personalised emails every link from the generic template must be
present with the exact same URL; Claude gets one retry if it drops or alters one, and if it still
fails, the generic email is sent instead.

## Reviewing personalised emails
With `REVIEW_PERSONALIZED=true`, AI-written emails are held: `python review.py`, then
`python review.py approve <id>` or `reject <id>`.

## Before going live
- Verify SPF/DKIM/DMARC on your sending domain.
- Add an unsubscribe link / physical address to the templates if required in your region.
