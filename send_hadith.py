import os
import json
import requests
from bs4 import BeautifulSoup

STATE_FILE = "state.json"
TOTAL_HADITHS = 1896

ID_INSTANCE = os.getenv("GREEN_API_ID")
API_TOKEN_INSTANCE = os.getenv("GREEN_API_TOKEN")
CHAT_ID = os.getenv("WHATSAPP_CHAT_ID")
API_HOST = "https://7107.api.greenapi.com"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"quran_page": 1, "hadith_index": 25}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def fetch_hadith_from_sunnah(hadith_num):
    url = f"https://sunnah.com/riyadussalihin:{hadith_num}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers, timeout=20)
    if response.status_code != 200:
        raise RuntimeError(f"Could not load Hadith {hadith_num} from Sunnah.com. Status {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    # 1. Book title (e.g. كتاب المقدمات)
    book_title = ""
    book_elem = soup.find("div", class_="book_page_number")
    if book_elem:
        book_title = book_elem.get_text(strip=True)

    # 2. Chapter title (e.g. (3) - باب الصبر)
    chapter_title = ""
    chapter_elem = soup.find("div", class_="arabic_chapter")
    if chapter_elem:
        chapter_title = chapter_elem.get_text(strip=True)

    # 3. Arabic Hadith Text
    text_elem = soup.find("div", class_="arabic_hadith_full") or soup.find("div", class_="arabic_hadith")
    if not text_elem:
        raise ValueError(f"Could not extract Arabic text for Hadith #{hadith_num}")

    hadith_text = text_elem.get_text(separator=" ", strip=True)

    return book_title, chapter_title, hadith_text

def send_hadith():
    state = load_state()
    hadith_num = state.get("hadith_index", 25)

    if hadith_num > TOTAL_HADITHS:
        hadith_num = 1

    print(f"Fetching Hadith #{hadith_num} from Sunnah.com...")
    book_title, chapter_title, hadith_text = fetch_hadith_from_sunnah(hadith_num)

    # Format message with Book, Chapter, and Hadith details
    message_lines = ["✨ *رياض الصالحين — من موقع Sunnah.com* ✨\n"]
    if book_title:
        message_lines.append(f"📖 *{book_title}*")
    if chapter_title:
        message_lines.append(f"🔹 *{chapter_title}*")
    
    message_lines.append(f"🔢 *رقم الحديث العام:* {hadith_num}\n")
    message_lines.append(hadith_text)
    message_lines.append(f"\n🔗 *الرابط:* https://sunnah.com/riyadussalihin:{hadith_num}")

    message_text = "\n".join(message_lines)

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
