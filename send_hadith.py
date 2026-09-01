import os
import json
import requests
from bs4 import BeautifulSoup

STATE_FILE = "state.json"
TOTAL_HADITHS = 1896
MAX_WORDS = 160

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
        json.dump(state, f, indent=2, ensure_ascii=False)

def fetch_hadith_text_from_sunnah(hadith_num):
    url = f"https://sunnah.com/riyadussalihin:{hadith_num}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers, timeout=20)
    if response.status_code != 200:
        raise RuntimeError(f"Could not load Hadith {hadith_num} from Sunnah.com. Status {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract pure Arabic Hadith Text
    text_elem = soup.find("div", class_="arabic_hadith_full") or soup.find("div", class_="arabic_hadith")
    if not text_elem:
        raise ValueError(f"Could not extract Arabic text for Hadith #{hadith_num}")

    return text_elem.get_text(separator=" ", strip=True)

def send_hadith():
    state = load_state()
    hadith_num = state.get("hadith_index", 1)

    while True:
        if hadith_num > TOTAL_HADITHS:
            hadith_num = 1

        print(f"Checking Hadith #{hadith_num} from Sunnah.com...")
        hadith_text = fetch_hadith_text_from_sunnah(hadith_num)
        
        word_count = len(hadith_text.split())
        print(f"Hadith #{hadith_num} word count: {word_count} words.")

        if word_count <= MAX_WORDS:
            # Hadith is within the limit, proceed to send
            break
        else:
            print(f"Hadith #{hadith_num} exceeded {MAX_WORDS} words ({word_count} words). Skipping to next...")
            hadith_num += 1

    # Send the chosen hadith
    url = f"{API_HOST}/waInstance{ID_INSTANCE}/sendMessage/{API_TOKEN_INSTANCE}"
    payload = {
        "chatId": CHAT_ID,
        "message": hadith_text
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print(f"Successfully sent Hadith #{hadith_num} ({word_count} words)")
        state["hadith_index"] = hadith_num + 1
        save_state(state)
    else:
        print(f"Failed to send: {response.text}")
        raise RuntimeError(f"API Error {response.status_code}")

if __name__ == "__main__":
    send_hadith()
