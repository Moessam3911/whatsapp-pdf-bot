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

def run():
    state = get_state()
    current_task = state.get("next_task", "quran")

    print(f"Executing scheduled turn: {current_task.upper()}")

    if current_task == "quran":
        send_quran.send_quran_page()
        fresh_state = get_state()
        fresh_state["next_task"] = "hadith"
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(fresh_state, f, indent=2, ensure_ascii=False)
    else:
        send_hadith.send_hadith()
        fresh_state = get_state()
        fresh_state["next_task"] = "quran"
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(fresh_state, f, indent=2, ensure_ascii=False)

    print("Task completed successfully.")

if __name__ == "__main__":
    run()
