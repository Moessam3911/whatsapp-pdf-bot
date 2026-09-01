import os
import json
import requests

STATE_FILE = "state.json"

ID_INSTANCE = os.getenv("GREEN_API_ID")
API_TOKEN_INSTANCE = os.getenv("GREEN_API_TOKEN")
CHAT_ID = os.getenv("WHATSAPP_CHAT_ID")
API_HOST = "https://7107.api.greenapi.com"

# Riyadh as-Salihin has 1896 total hadiths
TOTAL_HADITHS = 1896

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"quran_page": 1, "hadith_index": 1}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def fetch_hadith(hadith_num):
    # Verified open digital edition of Riyadh as-Salihin
    url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-riyadussalihin/{hadith_num}.json"
    res = requests.get(url, timeout=15)
    if res.status_code == 200:
        data = res.json()
        return data["hadiths"][0]["text"]
    return None

def send_hadith():
    state = load_state()
    hadith_num = state.get("hadith_index", 1)

    if hadith_num > TOTAL_HADITHS:
        hadith_num = 1

    print(f"Fetching Hadith #{hadith_num}...")
    hadith_text = fetch_hadith(hadith_num)

    if not hadith_text:
        raise RuntimeError(f"Failed to fetch Hadith #{hadith_num}")

    message_text = (
        f"✨ *حديث اليوم من رياض الصالحين* ✨\n\n"
        f"🔢 *الحديث رقم:* {hadith_num}\n\n"
        f"{hadith_text.strip()}\n\n"
        f"📚 *المصدر:* رياض الصالحين للإمام النووي"
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
