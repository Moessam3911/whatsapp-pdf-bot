import os
import json
import requests
from pdf2image import convert_from_path

PDF_PATH = "your_book.pdf"
STATE_FILE = "state.json"

# Load credentials from Environment Variables
ID_INSTANCE = os.getenv("GREEN_API_ID")
API_TOKEN_INSTANCE = os.getenv("GREEN_API_TOKEN")
CHAT_ID = os.getenv("WHATSAPP_CHAT_ID")

def get_current_page():
    if not os.path.exists(STATE_FILE):
        return 1
    with open(STATE_FILE, "r") as f:
        return json.load(f).get("current_page", 1)

def save_current_page(page_num):
    with open(STATE_FILE, "w") as f:
        json.dump({"current_page": page_num}, f, indent=2)

def send_daily_page():
    page_num = get_current_page()
    
    # Render page to image
    images = convert_from_path(
        PDF_PATH,
        first_page=page_num,
        last_page=page_num,
        dpi=200
    )
    
    if not images:
        print(f"No page found at index {page_num}. Ending run.")
        return

    image_path = f"page_{page_num}.jpg"
    images[0].save(image_path, "JPEG")

    # Send file via WhatsApp API
    url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendFileByUpload/{API_TOKEN_INSTANCE}"
    payload = {
        "chatId": CHAT_ID,
        "caption": f"📖 Daily Reading — Page {page_num}"
    }
    
    with open(image_path, "rb") as file:
        files = [('file', (image_path, file, 'image/jpeg'))]
        response = requests.post(url, data=payload, files=files)
    
    if response.status_code == 200:
        print(f"Successfully sent page {page_num}")
        save_current_page(page_num + 1)
    else:
        print(f"Failed to send: {response.text}")
        raise RuntimeError(f"API call failed with status {response.status_code}")

    if os.path.exists(image_path):
        os.remove(image_path)

if __name__ == "__main__":
    send_daily_page()
