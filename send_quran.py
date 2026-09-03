import os
import json
import requests
from pdf2image import convert_from_path

PDF_URL = "https://ia800300.us.archive.org/29/items/Quran_Pdf_format/Quran.pdf"
PDF_PATH = "quran.pdf"
STATE_FILE = "state.json"

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

def download_quran_pdf():
    # Only download if missing or corrupt (< 1 MB)
    if not os.path.exists(PDF_PATH) or os.path.getsize(PDF_PATH) < 1_000_000:
        print("Downloading Quran PDF from reliable mirror...")
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(PDF_URL, headers=headers, stream=True, timeout=60)
        
        if response.status_code != 200:
            raise RuntimeError(f"Download failed with status {response.status_code}")

        with open(PDF_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
        print("Quran PDF downloaded successfully.")

def send_quran_page():
    download_quran_pdf()

    state = load_state()
    page_num = state.get("quran_page", 1)
    print(f"Processing Quran Page {page_num}...")

    images = convert_from_path(
        PDF_PATH,
        first_page=page_num,
        last_page=page_num,
        dpi=200
    )

    if not images:
        print(f"Reached end of Quran or page {page_num} invalid.")
        return

    image_path = f"quran_page_{page_num}.jpg"
    images[0].save(image_path, "JPEG")

    url = f"{API_HOST}/waInstance{ID_INSTANCE}/sendFileByUpload/{API_TOKEN_INSTANCE}"
    payload = {
        "chatId": CHAT_ID
    }

    with open(image_path, "rb") as file:
        files = [('file', (image_path, file, 'image/jpeg'))]
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
