import os
import json
import send_quran
import send_hadith

STATE_FILE = "state.json"

def get_state():
    if not os.path.exists(STATE_FILE):
        return {"quran_page": 1, "hadith_index": 1, "next_task": "quran"}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_next_task(next_task):
    state = get_state()
    state["next_task"] = next_task
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def run():
    state = get_state()
    current_task = state.get("next_task", "quran")

    if current_task == "quran":
        print("--- Running Scheduled Task: QURAN PAGE ---")
        send_quran.send_quran_page()
        save_next_task("hadith")
    else:
        print("--- Running Scheduled Task: HADITH ---")
        send_hadith.send_hadith()
        save_next_task("quran")

if __name__ == "__main__":
    run()
