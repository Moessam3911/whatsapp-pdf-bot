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

    # Format 3-digit page number: 1 -> "001.jpg", 311 -> "311.jpg"
    page_file_name = f"{page_num:03d}.jpg"
    
    # High-resolution Madinah Mushaf CDN with solid white background
    image_url = f"https://raw.githubusercontent.com/thetruereligion/Quran-Images/master/pages/{page_num}.png"
    # Alternative direct JPG source to ensure no black background:
    direct_jpg_url = f"https://www.mp3quran.net/api/quran_pages_svg/{page_num}.svg"
    clean_jpg_url = f"https://raw.githubusercontent.com/Govar-dev/quran-images-api/main/images/{page_num}.jpg"

    print(f"Sending high-quality Quran Page {page_num}...")

    url = f"{API_HOST}/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN_INSTANCE}"
    payload = {
        "chatId": CHAT_ID,
        "urlFile": clean_jpg_url,
        "fileName": page_file_name
    }

    response = requests.post(url, json=payload, timeout=30)

    # Fallback to standard mirror if needed
    if response.status_code != 200:
        fallback_url = f"https://quran.ksu.edu.sa/ayat/safahat1/{page_num}.png"
        payload["urlFile"] = fallback_url
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
