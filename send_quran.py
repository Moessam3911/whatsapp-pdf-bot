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

    # High-quality Madinah Mushaf page from KSU Ayah Portal
    image_url = f"https://quran.ksu.edu.sa/ayat/safahat1/{page_num}.png"
    file_name = f"quran_page_{page_num}.png"

    print(f"Sending Quran Page {page_num} from KSU...")

    url = f"{API_HOST}/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN_INSTANCE}"
    payload = {
        "chatId": CHAT_ID,
        "urlFile": image_url,
        "fileName": file_name
    }

    response = requests.post(url, json=payload, timeout=30)

    if response.status_code == 200:
        print(f"Successfully sent Quran page {page_num}")
        state["quran_page"] = page_num + 1
        save_state(state)
    else:
        print(f"Failed to send Quran page: {response.text}")
        raise RuntimeError(f"API Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    send_quran_page()
