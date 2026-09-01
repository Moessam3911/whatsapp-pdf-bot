import os
import json
import requests

DATA_FILE = "hadiths_db.json"
STATE_FILE = "state.json"
DATA_URL = "https://raw.githubusercontent.com/fawazahmed0/hadith-api/1/editions/ara-riyadussalihin.json"

ID_INSTANCE = os.getenv("GREEN_API_ID")
API_TOKEN_INSTANCE = os.getenv("GREEN_API_TOKEN")
CHAT_ID = os.getenv("WHATSAPP_CHAT_ID")
API_HOST = "https://7107.api.greenapi.com"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"quran_page": 1, "hadith_index": 1}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def download_database_if_missing():
    if not os.path.exists(DATA_FILE):
        print("Downloading verified Riyadh as-Salihin database...")
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(DATA_URL, headers=headers, timeout=30)
        if res.status_code == 200:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                f.write(res.text)
        else:
            raise RuntimeError(f"Could not download hadith database. HTTP {res.status_code}")

def send_hadith():
    download_database_if_missing()

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    hadith_list = data.get("hadiths", [])
    total_hadiths = len(hadith_list)

    if total_hadiths == 0:
        raise ValueError("Hadith database is empty.")

    state = load_state()
    hadith_num = state.get("hadith_index", 1)

    # If reached the end, reset back to Hadith 1
    if hadith_num > total_hadiths:
        hadith_num = 1

    # In arrays, index is number - 1
    item = hadith_list[hadith_num - 1]
    hadith_text = item.get("text", "").strip()

    print(f"Sending Hadith #{hadith_num} of {total_hadiths}...")

    message_text = (
        f"✨ *حديث اليوم من رياض الصالحين* ✨\n\n"
        f"🔢 *الحديث رقم:* {hadith_num}\n\n"
        f"{hadith_text}\n\n"
        f"📚 *المصدر:* كتاب رياض الصالحين للإمام النووي"
    )

    url = f"{API_HOST}/waInstance{ID_INSTANCE}/sendMessage/{API_TOKEN_INSTANCE}"
    payload = {
        "chatId": CHAT_ID,
        "message": message_text
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print(f"Successfully sent Hadith #{hadith_num}")
        state["hadith_index"] = hadith_num + 1
        save_state(state)
    else:
        print(f"Failed to send: {response.text}")
        raise RuntimeError(f"API Error {response.status_code}")

if __name__ == "__main__":
    send_hadith()
