import os
import json
import random
import time
import requests

# Secrets & Environment Variables
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PINTEREST_SESS = os.getenv("PINTEREST_SESSION_COOKIE")
PINTEREST_CSRF = os.getenv("PINTEREST_CSRF_TOKEN")
PINTEREST_BOARD_ID = os.getenv("PINTEREST_BOARD_ID")
GREEN_API_INSTANCE_ID = os.getenv("GREEN_API_INSTANCE_ID")
GREEN_API_API_TOKEN = os.getenv("GREEN_API_API_TOKEN")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE")
PRODUCT_LINK = os.getenv("PRODUCT_LINK", "https://aahmedalmno.gumroad.com/l/gmvtlk")
SHEET_WEBHOOK_URL = os.getenv("GOOGLE_SHEET_WEBHOOK_URL")

SAFE_OBJECT_SEARCH_TERMS = [
    "esp32 microcontroller circuit board",
    "arduino breadboard electronics",
    "raspberry pi hardware tech",
    "electronic components circuit pcb",
    "soldering iron workbench electronics"
]

FORBIDDEN_WORDS = [
    "woman", "girl", "female", "model", "lady", "person", "portrait",
    "bikini", "lingerie", "sexy", "body", "people", "couple", "face", "man"
]

def get_pin_from_sheet():
    """Fetch next pin where Status = Ready from Google Sheets."""
    if not SHEET_WEBHOOK_URL:
        print("⚠️ GOOGLE_SHEET_WEBHOOK_URL is not set.")
        return None
    try:
        res = requests.get(SHEET_WEBHOOK_URL, timeout=15)
        data = res.json()
        if data.get("found"):
            print(f"📋 Fetched row {data.get('row')} from Google Sheets: {data.get('title')}")
            return data
        else:
            print("ℹ️ No rows found with Status = 'Ready' in Google Sheets.")
    except Exception as e:
        print(f"Error fetching from Google Sheets: {e}")
    return None

def update_sheet_status(row_number, pin_url):
    """Mark row as Published in Google Sheets."""
    if not SHEET_WEBHOOK_URL or not row_number:
        return
    try:
        payload = {"row": row_number, "pin_url": pin_url}
        requests.post(SHEET_WEBHOOK_URL, json=payload, timeout=15)
        print(f"✅ Row {row_number} updated to 'Published' in Google Sheets.")
    except Exception as e:
        print(f"Failed to update Google Sheet: {e}")

def get_clean_pexels_image(query):
    """Strictly objects-only images."""
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": str(PEXELS_API_KEY).strip()}
    clean_query = f"{query} -woman -girl -people -person"
    params = {"query": clean_query, "orientation": "portrait", "per_page": 10}

    try:
        res = requests.get(url, headers=headers, params=params, timeout=20)
        res.raise_for_status()
        photos = res.json().get("photos", [])
        
        valid_photos = []
        for photo in photos:
            alt_text = photo.get("alt", "").lower()
            if not any(bad_word in alt_text for bad_word in FORBIDDEN_WORDS):
                valid_photos.append(photo["src"]["large2x"])

        if valid_photos:
            return random.choice(valid_photos)
        elif photos:
            return photos[0]["src"]["large2x"]
    except Exception as e:
        print(f"Pexels error: {e}")
    return None

def create_pin_via_session(title, description, image_url, link):
    if not PINTEREST_SESS:
        print("❌ Error: PINTEREST_SESSION_COOKIE is missing.")
        return None

    sess_cookie = PINTEREST_SESS.strip().strip('"').strip("'")
    session = requests.Session()

    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    })

    session.cookies.set("_pinterest_sess", sess_cookie, domain=".pinterest.com", path="/")

    try:
        session.get("https://www.pinterest.com/", timeout=15)
        csrf_val = session.cookies.get("csrftoken") or (PINTEREST_CSRF or "").strip()
    except Exception:
        csrf_val = (PINTEREST_CSRF or "").strip()

    if not csrf_val:
        csrf_val = "1234567890abcdef1234567890abcdef"
        session.cookies.set("csrftoken", csrf_val, domain=".pinterest.com", path="/")

    post_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.pinterest.com/pin-builder/",
        "Origin": "https://www.pinterest.com",
        "Accept": "application/json, text/javascript, */*, q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "X-Pinterest-AppState": "active",
        "X-CSRFToken": csrf_val,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }

    payload_data = {
        "options": {
            "board_id": str(PINTEREST_BOARD_ID).strip(),
            "image_url": str(image_url).strip(),
            "title": str(title).strip(),
            "description": str(description).strip(),
            "link": str(link).strip(),
            "scrape_metric": {"source": "pinner_upload"}
        },
        "context": {}
    }

    data = {
        "source_url": "/pin-builder/",
        "data": json.dumps(payload_data)
    }

    endpoint = "https://www.pinterest.com/resource/PinResource/create/"

    try:
        res = session.post(endpoint, data=data, headers=post_headers, timeout=30)
        res_json = res.json()
        if res.status_code == 200 and "resource_response" in res_json:
            if res_json.get("resource_response", {}).get("status") == "success":
                return res_json["resource_response"]["data"]["id"]
        print(f"Pinterest error response: {res_json}")
    except Exception as e:
        print(f"Network error on session: {e}")
    return None

def send_whatsapp_notification(title, pin_id):
    if not (GREEN_API_INSTANCE_ID and GREEN_API_API_TOKEN and WHATSAPP_PHONE):
        return
    url = f"https://api.green-api.com/waInstance{GREEN_API_INSTANCE_ID}/sendMessage/{GREEN_API_API_TOKEN}"
    chat_id = f"{WHATSAPP_PHONE}@c.us" if "@" not in str(WHATSAPP_PHONE) else str(WHATSAPP_PHONE)
    pin_link = f"https://www.pinterest.com/pin/{pin_id}/"

    msg = (
        f"🚀 *تم نشر دبوس من Google Sheets!*\n\n"
        f"📌 *العنوان:* {title}\n"
        f"🔗 *الرابط:* {pin_link}\n"
        f"💰 *المنتج:* {PRODUCT_LINK}"
    )
    try:
        requests.post(url, headers={"Content-Type": "application/json"}, json={"chatId": chat_id, "message": msg}, timeout=15)
    except Exception:
        pass

def main():
    print("Starting Pinterest Sheet Automation Pipeline...")
    
    # جلب الدبوس التالي من Google Sheets
    sheet_data = get_pin_from_sheet()
    
    if sheet_data:
        title = sheet_data.get("title")
        desc = sheet_data.get("description")
        search = sheet_data.get("search_query") or "electronics circuit board"
        row_num = sheet_data.get("row")
    else:
        print("No item fetched from sheet. Stopping execution.")
        return

    print(f"Searching clean visual for: {search}...")
    img = get_clean_pexels_image(search)
    if not img:
        img = get_clean_pexels_image("circuit board electronics")

    if not img:
        print("Skipping pin due to missing image asset.")
        return

    print(f"Publishing Pin: '{title}'...")
    pin_id = create_pin_via_session(title, desc, img, PRODUCT_LINK)

    if pin_id:
        pin_url = f"https://www.pinterest.com/pin/{pin_id}/"
        print(f"✅ Published successfully! Pin ID: {pin_id}")
        
        # تحديث الحالة إلى Published في الشيت
        if row_num:
            update_sheet_status(row_num, pin_url)
            
        send_whatsapp_notification(title, pin_id)
    else:
        print("❌ Failed to publish pin via session.")

if __name__ == "__main__":
    main()
