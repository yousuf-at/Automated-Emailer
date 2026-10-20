"""Approve AI-personalised emails before they go out.
  python review.py            -> list pending drafts
  python review.py approve ID -> send that draft
  python review.py reject ID  -> discard it"""
import sys
import store, mailer

args = sys.argv[1:]
if not args:
    for sid, plat, to, subj, body in store.pending_review():
        print(f"\n=== {sid} | {plat} | {to}\nSubject: {subj}\n\n{body}")
elif len(args) == 2 and args[0] in ("approve", "reject"):
    row = store.get(args[1])
    if not row:
        sys.exit("not found")
    sid, plat, to, subj, body = row
    if args[0] == "approve":
        mailer.send(plat, to, subj, body)
        store.set_status(sid, "sent")
    else:
        store.set_status(sid, "rejected")
    print(f"{args[0]}d {sid}")
