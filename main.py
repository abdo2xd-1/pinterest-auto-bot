import os
import json
import random
import requests

# Load environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PINTEREST_SESS = os.getenv("PINTEREST_SESSION_COOKIE")
PINTEREST_CSRF = os.getenv("PINTEREST_CSRF_TOKEN")
PINTEREST_BOARD_ID = os.getenv("PINTEREST_BOARD_ID")
GREEN_API_INSTANCE_ID = os.getenv("GREEN_API_INSTANCE_ID")
GREEN_API_API_TOKEN = os.getenv("GREEN_API_API_TOKEN")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE")
PRODUCT_LINK = os.getenv("PRODUCT_LINK", "https://aahmedalmno.gumroad.com/l/gmvtlk")


def get_trending_pin_ideas(count=1):
    """Fallback pin ideas for reliable execution."""
    backup_ideas = [
        {
            "title": "Top 5 Digital Products You Can Sell on Gumroad",
            "description": "Create once, sell forever. Here are high-margin digital products to sell online. #DigitalProducts #Gumroad #MakeMoneyOnline #SideHustle",
            "pexels_search": "minimalist desk setup"
        },
        {
            "title": "How to Build a $1,000/Month AI Side Hustle",
            "description": "Discover how simple AI tools can help you generate passive income starting today! #SideHustle #AIAutomation #PassiveIncome",
            "pexels_search": "laptop coffee aesthetic"
        }
    ]
    random.shuffle(backup_ideas)
    return backup_ideas[:count]


def get_pexels_image(query):
    """Fetch high-quality portrait image asset cleanly from Pexels API."""
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
    """Publish Pin directly via Web Session, managing CSRF handshake automatically."""
    if not PINTEREST_SESS:
        print("❌ Error: PINTEREST_SESSION_COOKIE is missing in secrets.")
        return None

    sess_cookie = PINTEREST_SESS.strip().strip('"').strip("'")
    session = requests.Session()

    base_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }
    session.headers.update(base_headers)

    # 1. تثبيت كوكي الجلسة الأساسي
    session.cookies.set("_pinterest_sess", sess_cookie, domain=".pinterest.com", path="/")

    # 2. جلب صفحة البداية لتوليد وتثبيت كوكي الـ CSRF الحقيقي تلقائياً
    try:
        session.get("https://www.pinterest.com/", timeout=15)
        csrf_val = session.cookies.get("csrftoken") or (PINTEREST_CSRF or "").strip()
    except Exception as e:
        print(f"Handshake warning: {e}")
        csrf_val = (PINTEREST_CSRF or "").strip()

    if not csrf_val:
        csrf_val = "1234567890abcdef1234567890abcdef"
        session.cookies.set("csrftoken", csrf_val, domain=".pinterest.com", path="/")

    # 3. إعداد ترويسات الطلب بما فيها الـ CSRF
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
    """Send delivery notification via Green-API."""
    if not (GREEN_API_INSTANCE_ID and GREEN_API_API_TOKEN and WHATSAPP_PHONE):
        return

    url = f"https://api.green-api.com/waInstance{GREEN_API_INSTANCE_ID}/sendMessage/{GREEN_API_API_TOKEN}"
    headers = {"Content-Type": "application/json"}
    chat_id = f"{WHATSAPP_PHONE}@c.us" if "@" not in str(WHATSAPP_PHONE) else str(WHATSAPP_PHONE)
    pin_link = f"https://www.pinterest.com/pin/{pin_id}/" if pin_id else "Uploaded"

    msg = (
        f"🚀 *تم نشر دبوس تلقائياً بنجاح!*\n\n"
        f"📌 *العنوان:* {title}\n"
        f"🔗 *رابط البن:* {pin_link}\n"
        f"💰 *المنتج:* {PRODUCT_LINK}"
    )

    payload = {"chatId": chat_id, "message": msg}

    try:
        requests.post(url, headers=headers, json=payload, timeout=15)
    except Exception as e:
        print(f"WhatsApp notice error: {e}")


def main():
    print("Starting Pinterest Session Publisher (V2 Direct)...")
    pins = get_trending_pin_ideas(count=1)

    for item in pins:
        title = item.get("title")
        desc = item.get("description")
        search = item.get("pexels_search", "minimalist desk setup")

        print(f"\nFetching image for: {search}...")
        img = get_pexels_image(search)
        if not img:
            print("No image found, skipping.")
            continue

        print(f"Publishing Pin: '{title}'...")
        pin_id = create_pin_via_session(title, desc, img, PRODUCT_LINK)

        if pin_id:
            print(f"✅ Published successfully via Session! Pin ID: {pin_id}")
            send_whatsapp_notification(title, pin_id)
        else:
            print("❌ Failed to publish pin via session.")


if __name__ == "__main__":
    main()
