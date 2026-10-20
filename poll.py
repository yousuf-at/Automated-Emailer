"""Alternative to webhooks: poll the portal every few minutes."""
import time
import portal, workflow

while True:
    try:
        for raw in portal.fetch_new_signups():
            print(workflow.handle_signup(portal.from_portal(raw)))
    except Exception as e:
        print(f"[poll] error: {e}")
    time.sleep(120)
