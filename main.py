import os
import json
import random
import requests

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PINTEREST_SESS = os.getenv("PINTEREST_SESSION_COOKIE")
PINTEREST_CSRF = os.getenv("PINTEREST_CSRF_TOKEN")
PINTEREST_BOARD_ID = os.getenv("PINTEREST_BOARD_ID")
GREEN_API_INSTANCE_ID = os.getenv("GREEN_API_INSTANCE_ID")
GREEN_API_API_TOKEN = os.getenv("GREEN_API_API_TOKEN")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE")
PRODUCT_LINK = os.getenv("PRODUCT_LINK", "https://aahmedalmno.gumroad.com/l/gmvtlk")

def get_pexels_image(query):
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": str(PEXELS_API_KEY).strip()}
    params = {"query": str(query).strip(), "orientation": "portrait", "per_page": 5}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=20)
        res.raise_for_status()
        photos = res.json().get("photos", [])
        if photos:
            return random.choice(photos)["src"]["large2x"]
    except Exception as e:
        print(f"Pexels fetch error: {e}")
    return None

def create_pin_via_session(title, description, image_url, link):
    if not PINTEREST_SESS:
        print("❌ Error: PINTEREST_SESSION_COOKIE is missing.")
        return None

    sess_cookie = PINTEREST_SESS.strip().strip('"').strip("'")
    csrf_val = (PINTEREST_CSRF or "").strip().strip('"').strip("'")

    session = requests.Session()
    session.cookies.set("_pinterest_sess", sess_cookie, domain=".pinterest.com")
    if csrf_val:
        session.cookies.set("csrftoken", csrf_val, domain=".pinterest.com")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.pinterest.com/pin-builder/",
        "Origin": "https://www.pinterest.com",
        "Accept": "application/json, text/javascript, */*, q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "X-Pinterest-AppState": "active",
        "X-CSRFToken": csrf_val
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
        res = session.post(endpoint, data=data, headers=headers, timeout=30)
        try:
            res_json = res.json()
        except Exception:
            print(f"Server returned non-JSON. Status: {res.status_code}, Body: {res.text[:300]}")
            return None

        if res.status_code == 200 and "resource_response" in res_json:
            status = res_json.get("resource_response", {}).get("status")
            if status == "success":
                return res_json["resource_response"]["data"]["id"]
            else:
                print(f"Pinterest API Response: {res_json}")
        else:
            print(f"Session failed: Status {res.status_code} - {res_json}")
    except Exception as e:
        print(f"Network error on session: {e}")

    return None

def send_whatsapp_notification(title, pin_id):
    if not (GREEN_API_INSTANCE_ID and GREEN_API_API_TOKEN and WHATSAPP_PHONE):
        return
    url = f"https://api.green-api.com/waInstance{GREEN_API_INSTANCE_ID}/sendMessage/{GREEN_API_API_TOKEN}"
    chat_id = f"{WHATSAPP_PHONE}@c.us" if "@" not in str(WHATSAPP_PHONE) else str(WHATSAPP_PHONE)
    pin_link = f"https://www.pinterest.com/pin/{pin_id}/" if pin_id else "Uploaded"
    msg = f"🚀 *تم نشر دبوس تلقائياً بنجاح!*\n\n📌 *العنوان:* {title}\n🔗 *رابط البن:* {pin_link}\n💰 *المنتج:* {PRODUCT_LINK}"
    try:
        requests.post(url, headers={"Content-Type": "application/json"}, json={"chatId": chat_id, "message": msg}, timeout=15)
    except Exception:
        pass

def main():
    print("Starting Pinterest Session Publisher (V2 Direct)...")
    title = "Top 5 Digital Products You Can Sell on Gumroad"
    desc = "Create once, sell forever. Here are high-margin digital products to sell online. #DigitalProducts #Gumroad #MakeMoneyOnline"
    search = "minimalist desk setup"

    print(f"Fetching image for: {search}...")
    img = get_pexels_image(search)
    if not img:
        print("No image found.")
        return

    print(f"Publishing Pin: '{title}'...")
    pin_id = create_pin_via_session(title, desc, img, PRODUCT_LINK)

    if pin_id:
        print(f"✅ Published successfully via Session! Pin ID: {pin_id}")
        send_whatsapp_notification(title, pin_id)
    else:
        print("❌ Failed to publish pin via session.")

if __name__ == "__main__":
    main()
