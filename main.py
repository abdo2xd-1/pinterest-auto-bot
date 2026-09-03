import json
import os
import random
import time
import requests

# Load environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PINTEREST_SESS = os.getenv("PINTEREST_SESSION_COOKIE")
PINTEREST_BOARD_ID = os.getenv("PINTEREST_BOARD_ID")
GREEN_API_INSTANCE_ID = os.getenv("GREEN_API_INSTANCE_ID")
GREEN_API_API_TOKEN = os.getenv("GREEN_API_API_TOKEN")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE")
PRODUCT_LINK = os.getenv(
    "PRODUCT_LINK", "https://aahmedalmno.gumroad.com/l/gmvtlk"
)


def get_trending_pin_ideas(count=2):
  """Dynamic content ideas generation."""
  prompt = f"""Generate a JSON array of {count} completely unique, highly trending Pinterest pin ideas.
Niches: Side Hustles, AI Automation, Digital Marketing, Passive Income, Productivity.
Timestamp seed: {time.time()}

Return ONLY a valid JSON array of objects with this schema:
[
  {{
    "title": "SEO Optimized Catchy Pin Title",
    "description": "Engaging description with 3 hashtags and a CTA",
    "pexels_search": "high quality visual keywords",
    "board_name": "Side Hustles"
  }}
]"""

  payload = {"contents": [{"parts": [{"text": prompt}]}]}
  headers = {"Content-Type": "application/json"}
  candidate_models = ["gemini-flash-latest", "gemini-2.5-flash", "gemini-pro"]

  for model_name in candidate_models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
    try:
      response = requests.post(url, headers=headers, json=payload, timeout=20)
      if response.status_code == 200:
        raw_text = (
            response.json()["candidates"][0]["content"]["parts"][0]["text"]
            .strip()
        )
        if raw_text.startswith("```json"):
          raw_text = raw_text[7:]
        if raw_text.startswith("```"):
          raw_text = raw_text[3:]
        if raw_text.endswith("```"):
          raw_text = raw_text[:-3]
        print(f"✅ Generated ideas using model: {model_name}")
        return json.loads(raw_text.strip())
    except Exception:
      continue

  print("⚠️ Using fallback pin ideas...")
  backup_ideas = [
      {
          "title": "How to Build a $1,000/Month AI Side Hustle",
          "description": (
              "Discover how simple AI tools can help you generate passive"
              " income starting today! #SideHustle #AIAutomation #PassiveIncome"
          ),
          "pexels_search": "laptop coffee aesthetic",
      },
      {
          "title": "Top 5 Digital Products You Can Sell on Gumroad",
          "description": (
              "Create once, sell forever. Here are high-margin digital products"
              " to sell online. #DigitalProducts #Gumroad #MakeMoneyOnline"
          ),
          "pexels_search": "minimalist desk setup",
      },
  ]
  random.shuffle(backup_ideas)
  return backup_ideas[:count]


def get_pexels_image(query):
  """Fetch image asset cleanly from Pexels API."""
  url = "[https://api.pexels.com/v1/search](https://api.pexels.com/v1/search)"
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
  """Publish Pin directly via Web Session Cookie endpoint."""
  if not PINTEREST_SESS:
    print("❌ Error: PINTEREST_SESSION_COOKIE is missing in secrets.")
    return None

  session = requests.Session()
  clean_cookie = PINTEREST_SESS.strip().strip('"').strip("'")
  session.cookies.set("_pinterest_sess", clean_cookie, domain=".pinterest.com")

  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/124.0.0.0 Safari/537.36"
      ),
      "Referer": "[https://www.pinterest.com/pin-builder/](https://www.pinterest.com/pin-builder/)",
      "X-Requested-With": "XMLHttpRequest",
      "Accept": "application/json, text/javascript, */*; q=0.01",
  }

  payload = {
      "source_url": "/pin-builder/",
      "data": json.dumps({
          "options": {
              "board_id": str(PINTEREST_BOARD_ID).strip(),
              "image_url": str(image_url).strip(),
              "title": str(title).strip(),
              "description": str(description).strip(),
              "link": str(link).strip(),
              "scrape_metric": {"source": "pinner_upload"},
          },
          "context": {},
      }),
  }

  endpoint = "[https://www.pinterest.com/resource/PinResource/create/](https://www.pinterest.com/resource/PinResource/create/)"

  try:
    res = session.post(endpoint, data=payload, headers=headers, timeout=25)
    data = res.json()
    if res.status_code == 200 and "resource_response" in data:
      status = data.get("resource_response", {}).get("status")
      if status == "success":
        pin_id = data["resource_response"]["data"]["id"]
        return pin_id
      else:
        print(f"Pinterest error response: {data}")
    else:
      print(f"Session request failed: {res.status_code} - {res.text}")
  except Exception as e:
    print(f"Network error on Pinterest session: {e}")

  return None


def send_whatsapp_notification(title, pin_id):
  """Send status alert via Green-API."""
  if not (GREEN_API_INSTANCE_ID and GREEN_API_API_TOKEN and WHATSAPP_PHONE):
    return

  url = f"[https://api.green-api.com/waInstance](https://api.green-api.com/waInstance){GREEN_API_INSTANCE_ID}/sendMessage/{GREEN_API_API_TOKEN}"
  headers = {"Content-Type": "application/json"}
  chat_id = (
      f"{WHATSAPP_PHONE}@c.us"
      if "@" not in str(WHATSAPP_PHONE)
      else str(WHATSAPP_PHONE)
  )
  pin_link = (
      f"[https://www.pinterest.com/pin/](https://www.pinterest.com/pin/){pin_id}/" if pin_id else "Uploaded"
  )

  msg = (
      f"🚀 *تم نشر دبوس تلقائياً بنجاح!*\n\n📌 *العنوان:* {title}\n🔗 *رابط"
      f" البن:* {pin_link}\n💰 *المنتج:* {PRODUCT_LINK}"
  )

  payload = {"chatId": chat_id, "message": msg}

  try:
    requests.post(url, headers=headers, json=payload, timeout=15)
  except Exception as e:
    print(f"WhatsApp notice failed: {e}")


def main():
  print("Starting Pinterest Session Publisher...")
  pins = get_trending_pin_ideas(count=1)

  for idx, item in enumerate(pins, 1):
    title = item.get("title")
    desc = item.get("description")
    search = item.get("pexels_search", "side hustle ideas")

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
