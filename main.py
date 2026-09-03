import os
import json
import random
import time
import requests

# Secrets & Environment Variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PINTEREST_SESS = os.getenv("PINTEREST_SESSION_COOKIE")
PINTEREST_CSRF = os.getenv("PINTEREST_CSRF_TOKEN")
PINTEREST_BOARD_ID = os.getenv("PINTEREST_BOARD_ID")
GREEN_API_INSTANCE_ID = os.getenv("GREEN_API_INSTANCE_ID")
GREEN_API_API_TOKEN = os.getenv("GREEN_API_API_TOKEN")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE")
PRODUCT_LINK = os.getenv("PRODUCT_LINK", "https://aahmedalmno.gumroad.com/l/gmvtlk")

SAFE_OBJECT_SEARCH_TERMS = [
    "minimalist desk laptop dark screen",
    "developer monitor code terminal",
    "crypto trading charts screen setup",
    "financial growth stock market graph",
    "modern minimalist home office desk setup",
    "notebook pen coffee productivity desk",
    "clean macbook dark aesthetic workspace",
    "server room led technology hardware",
    "business charts paperwork fountain pen",
    "mechanical keyboard clean desk setup"
]

FORBIDDEN_WORDS = [
    "woman", "girl", "female", "model", "lady", "person", "portrait",
    "bikini", "lingerie", "sexy", "body", "people", "couple", "face", "man"
]

def get_trending_pin_ideas(count=1):
    safe_templates = [
        ("Top 5 Digital Products to Sell Automatically", "Build recurring passive income streams without inventory. Click the link to start today! #PassiveIncome #Gumroad #DigitalProducts"),
        ("How to Automate Workflows Using Python Scripts", "Save 10+ hours weekly with intelligent background automation. Learn more inside! #Automation #Python #Developer"),
        ("Build a $1,000/Month Digital Asset Portfolio", "Step-by-step framework to launch high-margin downloadable assets online. #SideHustle #OnlineBusiness #PassiveRevenue"),
        ("Best Productivity Tools for Solopreneurs in 2026", "Scale your online venture effortlessly with minimal software overhead. #Productivity #NoCode #TechTools"),
        ("The Complete Gumroad Sales Blueprint", "A simple roadmap to drive targeted organic traffic and close sales on autopilot. #Marketing #ECommerce #SalesFunnel")
    ]
    chosen = random.choice(safe_templates)
    return [{
        "title": chosen[0],
        "description": chosen[1],
        "pexels_search": random.choice(SAFE_OBJECT_SEARCH_TERMS)
    }]

def get_clean_pexels_image(query):
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
        print(f"Pexels fetch error: {e}")

    return None

def create_pin_via_session(title, description, image_url, link):
    if not PINTEREST_SESS:
        print("❌ Error: PINTEREST_SESSION_COOKIE is missing in secrets.")
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
    except Exception as e:
        print(f"Handshake warning: {e}")
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
        f"🚀 *تم نشر دبوس تلقائياً بنجاح!*\n\n"
        f"📌 *العنوان:* {title}\n"
        f"🔗 *رابط البن:* {pin_link}\n"
        f"💰 *المنتج:* {PRODUCT_LINK}"
    )

    try:
        requests.post(url, headers={"Content-Type": "application/json"}, json={"chatId": chat_id, "message": msg}, timeout=15)
    except Exception:
        pass

def main():
    print("Starting Clean Automation Pipeline (Safe Objects Only)...")
    pins = get_trending_pin_ideas(count=1)

    for item in pins:
        title = item.get("title")
        desc = item.get("description")
        search = item.get("pexels_search") or random.choice(SAFE_OBJECT_SEARCH_TERMS)

        print(f"Searching clean visual for: {search}...")
        img = get_clean_pexels_image(search)
        if not img:
            print("No matching safe image found, trying fallback...")
            img = get_clean_pexels_image("laptop coffee desk")

        if not img:
            print("Skipping pin due to missing image asset.")
            continue

        print(f"Publishing Pin: '{title}'...")
        pin_id = create_pin_via_session(title, desc, img, PRODUCT_LINK)

        if pin_id:
            print(f"✅ Published successfully! Pin ID: {pin_id}")
            send_whatsapp_notification(title, pin_id)
        else:
            print("❌ Failed to publish pin via session.")

if __name__ == "__main__":
    main()
