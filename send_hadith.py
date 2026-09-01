import os
import json
import requests

DATA_FILE = "hadiths.json"
STATE_FILE = "state.json"

ID_INSTANCE = os.getenv("GREEN_API_ID")
API_TOKEN_INSTANCE = os.getenv("GREEN_API_TOKEN")
CHAT_ID = os.getenv("WHATSAPP_CHAT_ID")
API_HOST = "https://7107.api.greenapi.com"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"quran_page": 1, "hadith_index": 0}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def send_hadith():
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"{DATA_FILE} does not exist.")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        hadiths = json.load(f)

    if not hadiths:
        print("Hadith list empty.")
        return

    state = load_state()
    index = state.get("hadith_index", 0)

    if index >= len(hadiths):
        print("Completed all hadiths. Looping back to index 0.")
        index = 0

    item = hadiths[index]

    message_text = (
        f"✨ *حديث اليوم من رياض الصالحين* ✨\n\n"
        f"🔹 *{item.get('chapter', '')}*\n"
        f"🔢 حديث رقم: {item.get('number', index + 1)}\n\n"
        f"{item['text']}\n\n"
        f"📚 *التخريج:* {item.get('reference', '')}"
    )

    url = f"{API_HOST}/waInstance{ID_INSTANCE}/sendMessage/{API_TOKEN_INSTANCE}"
    payload = {
        "chatId": CHAT_ID,
        "message": message_text
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print(f"Successfully sent Hadith index {index}")
        state["hadith_index"] = index + 1
        save_state(state)
    else:
        print(f"Failed to send: {response.text}")
        raise RuntimeError(f"API Error {response.status_code}")

if __name__ == "__main__":
    send_hadith()
