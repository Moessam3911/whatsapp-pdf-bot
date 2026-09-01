import os
import json
import requests
from bs4 import BeautifulSoup

STATE_FILE = "state.json"
TOTAL_CHAPTERS = 372  # Total chapters in Riyadh as-Salihin on Sunnah.com

ID_INSTANCE = os.getenv("GREEN_API_ID")
API_TOKEN_INSTANCE = os.getenv("GREEN_API_TOKEN")
CHAT_ID = os.getenv("WHATSAPP_CHAT_ID")
API_HOST = "https://7107.api.greenapi.com"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"quran_page": 1, "chapter_num": 3, "hadith_in_chapter": 1}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def fetch_chapter_hadiths(chapter_num):
    url = f"https://sunnah.com/riyadussalihin/chapters/{chapter_num}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers, timeout=25)
    if response.status_code != 200:
        raise RuntimeError(f"Could not load Chapter {chapter_num} from Sunnah.com. Status {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract Book and Chapter Titles
    book_title_elem = soup.find("div", class_="book_page_number")
    book_title = book_title_elem.get_text(strip=True) if book_title_elem else "رياض الصالحين"

    chapter_elem = soup.find("div", class_="arabic_chapter")
    chapter_title = chapter_elem.get_text(strip=True) if chapter_elem else f"باب رقم {chapter_num}"

    # Extract all hadith containers on this chapter page
    containers = soup.find_all("div", class_="actualHadithContainer")
    hadiths = []

    for c in containers:
        text_elem = c.find("div", class_="arabic_hadith_full") or c.find("div", class_="arabic_hadith")
        ref_elem = c.find("table", class_="hadith_reference")
        
        ref_text = ""
        if ref_elem:
            ref_text = ref_elem.get_text(separator=" ", strip=True)

        if text_elem:
            hadiths.append({
                "text": text_elem.get_text(separator=" ", strip=True),
                "reference": ref_text
            })

    return book_title, chapter_title, hadiths

def send_hadith():
    state = load_state()
    chapter_num = state.get("chapter_num", 3)
    hadith_in_chapter = state.get("hadith_in_chapter", 1)

    print(f"Fetching Chapter {chapter_num} from Sunnah.com...")
    book_title, chapter_title, hadiths = fetch_chapter_hadiths(chapter_num)

    if not hadiths:
        # If no hadiths found, move to next chapter
        print(f"No hadiths found in Chapter {chapter_num}. Moving to next.")
        state["chapter_num"] = chapter_num + 1
        state["hadith_in_chapter"] = 1
        save_state(state)
        return

    # 1-based index to 0-based array index
    idx = hadith_in_chapter - 1

    if idx >= len(hadiths):
        # Chapter finished, move to next chapter
        chapter_num += 1
        if chapter_num > TOTAL_CHAPTERS:
            chapter_num = 1
        print(f"Chapter completed. Transitioning to Chapter {chapter_num}...")
        book_title, chapter_title, hadiths = fetch_chapter_hadiths(chapter_num)
        idx = 0
        hadith_in_chapter = 1

    current_hadith = hadiths[idx]

    # Format WhatsApp Message
    message_text = (
        f"✨ *رياض الصالحين — Sunnah.com* ✨\n\n"
        f"📖 *{book_title}*\n"
        f"🔹 *{chapter_title}*\n"
        f"🔢 حديث رقم ({hadith_in_chapter} من {len(hadiths)} في هذا الباب)\n\n"
        f"{current_hadith['text']}\n\n"
        f"🔗 *المصدر:* https://sunnah.com/riyadussalihin/chapters/{chapter_num}"
    )

    url = f"{API_HOST}/waInstance{ID_INSTANCE}/sendMessage/{API_TOKEN_INSTANCE}"
    payload = {
        "chatId": CHAT_ID,
        "message": message_text
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print(f"Successfully sent Hadith {hadith_in_chapter}/{len(hadiths)} from Chapter {chapter_num}")
        
        # Advance index
        if hadith_in_chapter >= len(hadiths):
            state["chapter_num"] = chapter_num + 1
            state["hadith_in_chapter"] = 1
        else:
            state["chapter_num"] = chapter_num
            state["hadith_in_chapter"] = hadith_in_chapter + 1
            
        save_state(state)
    else:
        print(f"Failed to send: {response.text}")
        raise RuntimeError(f"API Error {response.status_code}")

if __name__ == "__main__":
    send_hadith()
