import os
import json
import time
import send_quran
import send_hadith

STATE_FILE = "state.json"
TEST_ITERATIONS = 8   # Will run 8 tasks total (alternating Quran -> Hadith -> Quran -> Hadith...)
DELAY_SECONDS = 30     # 30-second delay between tasks

def get_state():
    if not os.path.exists(STATE_FILE):
        return {"quran_page": 1, "hadith_index": 1, "next_task": "quran"}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def run_test_cycle():
    for step in range(TEST_ITERATIONS):
        state = get_state()
        current_task = state.get("next_task", "quran")

        print(f"\n==========================================")
        print(f"Step [{step + 1}/{TEST_ITERATIONS}] -> Next Task: {current_task.upper()}")
        print(f"Current State: Quran Page {state.get('quran_page')}, Hadith Index {state.get('hadith_index')}")
        print(f"==========================================")

        if current_task == "quran":
            send_quran.send_quran_page()
            # Reload fresh state saved by send_quran and switch turn
            fresh_state = get_state()
            fresh_state["next_task"] = "hadith"
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(fresh_state, f, indent=2, ensure_ascii=False)
        else:
            send_hadith.send_hadith()
            # Reload fresh state saved by send_hadith and switch turn
            fresh_state = get_state()
            fresh_state["next_task"] = "quran"
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(fresh_state, f, indent=2, ensure_ascii=False)

        if step < TEST_ITERATIONS - 1:
            print(f"--> Task finished. Waiting {DELAY_SECONDS} seconds before next task...")
            time.sleep(DELAY_SECONDS)

if __name__ == "__main__":
    run_test_cycle()
