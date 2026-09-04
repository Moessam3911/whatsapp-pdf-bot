import os
import json
import time
import send_quran
import send_hadith

STATE_FILE = "state.json"
TEST_DURATION_SECONDS = 2 * 60 * 60  # 2 Hours (7200 seconds)
DELAY_SECONDS = 60*60*12                  # Interval between messages

def get_state():
    if not os.path.exists(STATE_FILE):
        return {"quran_page": 1, "hadith_index": 1, "next_task": "quran"}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def run_stress_test():
    start_time = time.time()
    iteration = 1

    print(f"Starting 2-hour stress test. Interval: {DELAY_SECONDS}s.")

    while (time.time() - start_time) < TEST_DURATION_SECONDS:
        elapsed = int(time.time() - start_time)
        remaining = int(TEST_DURATION_SECONDS - elapsed)
        
        state = get_state()
        current_task = state.get("next_task", "quran")

        print(f"\n==========================================")
        print(f"Iteration #{iteration} | Elapsed: {elapsed // 60}m | Remaining: {remaining // 60}m")
        print(f"Executing: {current_task.upper()}")
        print(f"Current State: Quran Page {state.get('quran_page')}, Hadith Index {state.get('hadith_index')}")
        print(f"==========================================")

        try:
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

        except Exception as err:
            print(f"Error during iteration #{iteration}: {err}")
            print("Retrying next turn after delay...")

        iteration += 1
        print(f"Waiting {DELAY_SECONDS} seconds...")
        time.sleep(DELAY_SECONDS)

    print("2-Hour stress test completed successfully.")

if __name__ == "__main__":
    run_stress_test()
