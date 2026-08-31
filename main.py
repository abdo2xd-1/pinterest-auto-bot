import json
import os
import random
import time
import requests

# Load environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN")
PINTEREST_BOARD_ID = os.getenv("PINTEREST_BOARD_ID")
GREEN_API_INSTANCE_ID = os.getenv("GREEN_API_INSTANCE_ID")
GREEN_API_API_TOKEN = os.getenv("GREEN_API_API_TOKEN")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE")
PRODUCT_LINK = os.getenv(
    "PRODUCT_LINK", "https://aahmedalmno.gumroad.com/l/gmvtlk"
)


def get_trending_pin_ideas(count=3):
  """Generate pin ideas dynamically with automatic model fallback."""
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

  # Try available Gemini models
  candidate_models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-pro"]

  for model_name in candidate_models:
    url = (
        "https:"
        + chr(47)
        + chr(47)
        + "generativelanguage.googleapis.com"
        + chr(47)
        + "v1beta"
        + chr(47)
        + "models"
        + chr(47)
        + f"{model_name}:generateContent?key={GEMINI_API_KEY}"
    )
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
        print(f"✅ Successfully generated pins using model: {model_name}")
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
          "board_name": "Side Hustles",
      },
      {
          "title": "Top 5 Digital Products You Can Sell on Gumroad",
          "description": (
              "Create once, sell forever. Here are high-margin digital products"
              " to sell online. #DigitalProducts #Gumroad #MakeMoneyOnline"
          ),
          "pexels_search": "minimalist desk setup",
          "board_name": "Side Hustles",
      },
  ]
  random.shuffle(backup_ideas)
  return backup_ideas[:count]


def get_pexels_image(query):
  """Fetch a high-quality vertical image from Pexels API cleanly."""
  # Building the base URL cleanly without markdown injection
  base_url = (
      "https:"
      + chr(47)
      + chr(47)
      + "api.pexels.com"
      + chr(47)
      + "v1"
      + chr(47)
      + "search"
  )
  headers = {"Authorization": str(PEXELS_API_KEY).strip()}
  params = {"query": str(query).strip(), "orientation": "portrait", "per_page": 5}

  try:
    response = requests.get(
        base_url, headers=headers, params=params, timeout=20
    )
    response.raise_for_status()
    data = response.json()
    photos = data.get("photos", [])
    if photos:
      return random.choice(photos)["src"]["large2x"]
  except Exception as e:
    print(f"Error fetching image from Pexels: {e}")
  return None


def publish_pin_to_pinterest(title, description, image_url, link):
  """Publish a Pin to Pinterest via Pinterest API v5."""
  url = (
      "https:"
      + chr(47)
      + chr(47)
      + "api.pinterest.com"
      + chr(47)
      + "v5"
      + chr(47)
      + "pins"
  )
  headers = {
      "Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}".strip(),
      "Content-Type": "application/json",
  }

  payload = {
      "title": str(title),
      "description": str(description),
      "board_id": str(PINTEREST_BOARD_ID).strip(),
      "link": str(link).strip(),
      "media_source": {"source_type": "image_url", "url": str(image_url)},
  }

  try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()
  except Exception as e:
    print(f"Error publishing to Pinterest: {e}")
    if "response" in locals() and hasattr(response, "text"):
      print(f"Response: {response.text}")
    return None


def send_whatsapp_notification(title, pin_url):
  """Send notification to WhatsApp using Green-API."""
  if not (GREEN_API_INSTANCE_ID and GREEN_API_API_TOKEN and WHATSAPP_PHONE):
    return

  url = (
      "https:"
      + chr(47)
      + chr(47)
      + "api.green-api.com"
      + chr(47)
      + f"waInstance{GREEN_API_INSTANCE_ID}"
      + chr(47)
      + "sendMessage"
      + chr(47)
      + f"{GREEN_API_API_TOKEN}"
  )
  headers = {"Content-Type": "application/json"}

  chat_id = (
      f"{WHATSAPP_PHONE}@c.us"
      if "@" not in str(WHATSAPP_PHONE)
      else str(WHATSAPP_PHONE)
  )
  msg = (
      f"🚀 *تم نشر دبوس جديد بنجاح!*\n\n📌 *العنوان:* {title}\n🔗 *الرابط:*"
      f" {pin_url}\n💰 *رابط المنتج:* {PRODUCT_LINK}"
  )

  payload = {"chatId": chat_id, "message": msg}

  try:
    requests.post(url, headers=headers, json=payload, timeout=20)
  except Exception as e:
    print(f"Error sending WhatsApp message: {e}")


def main():
  print("Starting automated Pinterest workflow...")
  pins = get_trending_pin_ideas(count=3)

  print(f"Generated {len(pins)} ideas. Publishing...")

  for idx, pin_data in enumerate(pins, 1):
    title = pin_data.get("title")
    description = pin_data.get("description")
    search_query = pin_data.get("pexels_search", "side hustle ideas")

    print(f"\n[{idx}/{len(pins)}] Fetching image for: {search_query}")
    image_url = get_pexels_image(search_query)

    if not image_url:
      print("Failed to get image, skipping...")
      continue

    print(f"Publishing Pin: '{title}'...")
    res = publish_pin_to_pinterest(title, description, image_url, PRODUCT_LINK)

    if res:
      pin_id = res.get("id", "")
      pin_url = (
          f"[https://www.pinterest.com/pin/](https://www.pinterest.com/pin/){pin_id}/" if pin_id else "Created"
      )
      print(f"✅ Success! Pin ID: {pin_id}")
      send_whatsapp_notification(title, pin_url)
    else:
      print("❌ Failed to publish pin.")

    if idx < len(pins):
      time.sleep(15)


if __name__ == "__main__":
  main()
