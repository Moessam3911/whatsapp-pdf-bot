"""
Decides what (if anything) to send right now, and sends it.

Runs every 15 minutes from GitHub Actions. It is safe to run as often as
you like: each message is sent at most ONCE per day, because the date of
the last successful send is stored in state.json.

- Quran page: sent on the first run at or after QURAN_TIME
- Hadith:     sent on the first run at or after HADITH_TIME
"""
import json
import os
import sys
from datetime import datetime, time
from zoneinfo import ZoneInfo

STATE_FILE = "state.json"
TIMEZONE = os.getenv("BOT_TIMEZONE", "Africa/Cairo")
QURAN_TIME = time(8, 0)
HADITH_TIME = time(20, 0)


def load_state():
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def due_tasks(now, state):
    today = now.date().isoformat()
    tasks = []
    if now.time() >= QURAN_TIME and state.get("last_quran_date") != today:
        tasks.append("quran")
    if now.time() >= HADITH_TIME and state.get("last_hadith_date") != today:
        tasks.append("hadith")
    return tasks


def run(force=None):
    now = datetime.now(ZoneInfo(TIMEZONE))
    today = now.date().isoformat()
    state = load_state()
    tasks = [force] if force else due_tasks(now, state)

    print(f"Local time ({TIMEZONE}): {now:%Y-%m-%d %H:%M}  ->  tasks: {tasks or 'nothing'}")

    for task in tasks:
        if task == "quran":
            import send_quran
            send_quran.send_quran_page()        # raises on failure
            state = load_state()
            state["last_quran_date"] = today
        elif task == "hadith":
            import send_hadith
            send_hadith.send_hadith()           # raises on failure
            state = load_state()
            state["last_hadith_date"] = today
        else:
            sys.exit(f"Unknown task: {task}")
        save_state(state)
        print(f"{task} sent and recorded for {today}")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else None)
