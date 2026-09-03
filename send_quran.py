import os
import json
import requests

STATE_FILE = "state.json"
TOTAL_PAGES = 604

ID_INSTANCE = os.getenv("GREEN_API_ID")
API_TOKEN_INSTANCE = os.getenv("GREEN_API_TOKEN")
CHAT_ID = os.getenv("WHATSAPP_CHAT_ID")
API_HOST = "https://7107.api.greenapi.com"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"quran_page": 1, "hadith_index": 1, "next_task": "quran"}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def send_quran_page():
    state = load_state()
    page_num = state.get("quran_page", 1)

    if page_num > TOTAL_PAGES:
        page_num = 1

    page_file_name = f"page{page_num:03d}.png"
    image_url = f"https://android.quran.com/data/width_1260/{page_file_name}"

    print(f"Sending Quran Page {page_num} via direct URL...")

    # Use Green API sendFileByUrl
    url = f"{API_HOST}/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN_INSTANCE}"
    payload = {
        "chatId": CHAT_ID,
        "urlFile": image_url,
        "fileName": page_file_name
    }

    response = requests.post(url, json=payload, timeout=30)

    if response.status_code == 200:
        print(f"Successfully sent Quran page {page_num}")
        state["quran_page"] = page_num + 1
        save_state(state)
    else:
        print(f"Failed to send: {response.text}")
        raise RuntimeError(f"API Error {response.status_code}")

if __name__ == "__main__":
    send_quran_page()
