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

  # Try to list available models for your API key
  candidate_models = []
  try:
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    list_res = requests.get(list_url, timeout=10)
    if list_res.status_code == 200:
      models_data = list_res.json().get("models", [])
      for m in models_data:
        if "generateContent" in m.get("supportedGenerationMethods", []):
          candidate_models.append(m["name"].replace("models/", ""))
  except Exception as e:
    print(f"Could not fetch model list: {e}")

  # Fallback default models if list empty
  if not candidate_models:
    candidate_models = [
        "gemini-2.5-flash",
        "gemini-1.5-pro",
        "gemini-pro",
        "gemini-1.0-pro",
    ]

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
        print(f"✅ Successfully generated pins using model: {model_name}")
        return json.loads(raw_text.strip())
    except Exception:
      continue

  # Fallback pre-crafted pins if API completely fails
  print("⚠️ Using pre-crafted fallback pin ideas to ensure 24/7 delivery...")
  backup_ideas = [
      {
          "title": "How to Build a $1,000/Month AI Side Hustle",
          "description": (
              "Discover how simple AI tools can help you generate passive"
              " income starting today! Check the link in bio to learn"
              " more. #SideHustle #AIAutomation #PassiveIncome"
          ),
          "pexels_search": "laptop workspace coffee aesthetic",
          "board_name": "Side Hustles",
      },
      {
          "title": "Top 5 Digital Products You Can Sell on Gumroad",
          "description": (
              "Create once, sell forever. Here are the best high-margin digital"
              " products to sell online effortlessly. #DigitalProducts #Gumroad"
              " #MakeMoneyOnline"
          ),
          "pexels_search": "minimalist modern desk",
          "board_name": "Side Hustles",
      },
      {
          "title": "Automate Your Business: No-Code Automation Guide",
          "description": (
              "Save 20+ hours every week using smart automations and GitHub"
              " workflows. Get the full system below! #Productivity #NoCode"
              " #WorkSmart"
          ),
          "pexels_search": "coding developer workstation",
          "board_name": "Side Hustles",
      },
  ]
  random.shuffle(backup_ideas)
  return backup_ideas[:count]


def get_pexels_image(query):
  """Fetch a high-quality vertical image from Pexels API."""
  url = f"[https://api.pexels.com/v1/search?query=](https://api.pexels.com/v1/search?query=){query}&orientation=portrait&per_page=5"
  headers = {"Authorization": PEXELS_API_KEY}

  try:
    response = requests.get(url, headers=headers, timeout=20)
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
  url = "[https://api.pinterest.com/v5/pins](https://api.pinterest.com/v5/pins)"
  headers = {
      "Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}",
      "Content-Type": "application/json",
  }

  payload = {
      "title": title,
      "description": description,
      "board_id": PINTEREST_BOARD_ID,
      "link": link,
      "media_source": {"source_type": "image_url", "url": image_url},
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

  url = f"[https://api.green-api.com/waInstance](https://api.green-api.com/waInstance){GREEN_API_INSTANCE_ID}/sendMessage/{GREEN_API_API_TOKEN}"
  headers = {"Content-Type": "application/json"}

  chat_id = (
      f"{WHATSAPP_PHONE}@c.us"
      if "@" not in WHATSAPP_PHONE
      else WHATSAPP_PHONE
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
