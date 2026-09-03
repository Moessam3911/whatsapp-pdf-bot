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

def download_quran_page_image(page_num, destination):
    # Formats page numbers: 1 -> "page001.png", 311 -> "page311.png"
    page_str = f"page{page_num:03d}.png"
    url = f"https://android.quran.com/data/width_1260/{page_str}"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=20)
    
    if response.status_code != 200:
        # Fallback CDN if primary mirror fails
        fallback_url = f"https://raw.githubusercontent.com/thetruereligion/Quran-Images/master/pages/{page_num}.png"
        response = requests.get(fallback_url, headers=headers, timeout=20)
        if response.status_code != 200:
            raise RuntimeError(f"Could not download page {page_num}. Status: {response.status_code}")

    with open(destination, "wb") as f:
        f.write(response.content)

def send_quran_page():
    state = load_state()
    page_num = state.get("quran_page", 1)

    if page_num > TOTAL_PAGES:
        page_num = 1

    print(f"Fetching clean Quran Page {page_num}...")
    image_path = f"quran_page_{page_num}.png"
    download_quran_page_image(page_num, image_path)

    url = f"{API_HOST}/waInstance{ID_INSTANCE}/sendFileByUpload/{API_TOKEN_INSTANCE}"
    payload = {
        "chatId": CHAT_ID
    }

    with open(image_path, "rb") as file:
        files = [('file', (image_path, file, 'image/png'))]
        response = requests.post(url, data=payload, files=files)

    if response.status_code == 200:
        print(f"Successfully sent Quran page {page_num}")
        state["quran_page"] = page_num + 1
        save_state(state)
    else:
        print(f"Failed to send: {response.text}")
        raise RuntimeError(f"API Error {response.status_code}")

    if os.path.exists(image_path):
        os.remove(image_path)

if __name__ == "__main__":
    send_quran_page()
