import sys
import os
import json
import send_quran
import send_hadith

STATE_FILE = "state.json"

def get_state():
    if not os.path.exists(STATE_FILE):
        return {"quran_page": 1, "hadith_index": 1}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def run():
    # Accept command line argument: python alternate_sender.py quran
    # or python alternate_sender.py hadith
    if len(sys.argv) > 1:
        task = sys.argv[1].lower()
    else:
        # Fallback if run without arguments
        state = get_state()
        task = state.get("next_task", "quran")

    print(f"=== Starting Task: {task.upper()} ===")

    if task == "quran":
        send_quran.send_quran_page()
    elif task == "hadith":
        send_hadith.send_hadith()
    else:
        print(f"Unknown task: {task}")
        sys.exit(1)

    print(f"=== Task {task.upper()} Completed Successfully ===")

if __name__ == "__main__":
    run()
