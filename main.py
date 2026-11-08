import os
import json
import random
import requests

# ==========================================
# 1. إعدادات المفاتيح
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PINTEREST_ACCESS_TOKEN = os.environ.get("PINTEREST_ACCESS_TOKEN")
PINTEREST_BOARD_ID = os.environ.get("PINTEREST_BOARD_ID")

HISTORY_FILE = "history.txt"

# ==========================================
# 2. إدارة سجل الأفكار (History)
# ==========================================
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines()]
    return []

def save_to_history(idea):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(idea + "\n")

# ==========================================
# 3. ابتكار الفكرة برمجياً (بالاتصال المباشر)
# ==========================================
def generate_unique_idea(history):
    topics = [
        "Arduino projects", "Raspberry Pi DIY", "Home Automation circuits", 
        "LED Matrix displays", "Robotics and motors", "ESP32 IoT", 
        "Vintage electronics repair", "PCB design aesthetic", 
        "Soldering art", "Audio amplifiers DIY"
    ]
    random_topic = random.choice(topics)
    
    recent_history = history[-50:] if history else []
    history_text = "\n".join(recent_history)
    
    prompt = f"""
    You are a creative electronics engineer. Come up with a very specific, unique, and aesthetic DIY electronics project idea in the field of '{random_topic}'.
    The idea must be highly visual and suitable for a Pinterest image.
    Do NOT use any of these previously generated ideas:
    {history_text}
    
    Write the idea in exactly one short English sentence (under 15 words) ready to be used as an image generation prompt.
    """
    
    # استخدام الإصدار الدقيق والمستقر 002
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-002:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    
    if "candidates" in data:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    else:
        raise Exception(f"فشل توليد الفكرة: {data}")

# ==========================================
# 4. توليد المحتوى والسيو (بالاتصال المباشر)
# ==========================================
def generate_seo_content(idea):
    prompt = f"""
    You are a Pinterest SEO expert.
    I have this DIY electronics project idea: "{idea}".
    Please write in English:
    1. A catchy, highly clickable Pin Title.
    2. A strong SEO-optimized description containing relevant keywords that electronics hobbyists search for (under 300 words).
    3. 3 to 5 strong hashtags.
    
    Return ONLY a JSON response in this exact format (no markdown formatting or extra text):
    {{"title": "Your Title Here", "description": "Description and hashtags here"}}
    """
    
    # استخدام الإصدار الدقيق والمستقر 002
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-002:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    
    if "candidates" not in data:
        raise Exception(f"فشل توليد السيو: {data}")
        
    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    text = text.replace('```json', '').replace('```', '').strip()
    parsed_data = json.loads(text)
    
    call_to_action = "\n\n🔌 If you loved this project, make sure to follow our page for daily DIY electronics and tech inspiration!"
    final_description = parsed_data["description"] + call_to_action
    
    return parsed_data["title"], final_description

# ==========================================
# 5. توليد الصورة
# ==========================================
def generate_image(idea, image_path="generated_pin.jpg"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    image_prompt = f"A highly detailed, aesthetic close-up photo of an electronic DIY project: {idea}. Cinematic lighting, cyberpunk vibes, high resolution, Pinterest style."
    
    payload = {
        "instances": [{"prompt": image_prompt}],
        "parameters": {"sampleCount": 1}
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()
    
    if "predictions" in response_data:
        import base64
        image_bytes = base64.b64decode(response_data["predictions"][0]["bytesBase64Encoded"])
        with open(image_path, "wb") as f:
            f.write(image_bytes)
        return image_path
    else:
        raise Exception(f"فشل توليد الصورة: {response_data}")

# ==========================================
# 6. النشر على بنترست
# ==========================================
def upload_to_pinterest(title, description, image_path):
    headers = {
        "Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    media_url = "https://api.pinterest.com/v5/media"
    media_response = requests.post(media_url, headers=headers, json={"media_type": "image"}).json()
    
    with open(image_path, 'rb') as f:
        requests.post(media_response["upload_url"], data=media_response["upload_parameters"], files={'file': f})
    
    import base64
    pin_payload = {
        "board_id": PINTEREST_BOARD_ID,
        "media_source": {
            "source_type": "image_base64",
            "content_type": "image/jpeg",
            "data": base64.b64encode(open(image_path, "rb").read()).decode('utf-8')
        },
        "title": title,
        "description": description
    }
    create_response = requests.post("https://api.pinterest.com/v5/pins", headers=headers, json=pin_payload)
    return create_response.status_code == 201

# ==========================================
# 7. التشغيل
# ==========================================
def main():
    try:
        history = load_history()
        
        print("1. جاري ابتكار فكرة جديدة ومراجعة السجل...")
        idea = generate_unique_idea(history)
        print(f"الفكرة: {idea}")
        
        print("2. جاري كتابة المحتوى والسيو بالإنجليزية...")
        title, description = generate_seo_content(idea)
        
        print("3. جاري توليد الصورة...")
        image_path = generate_image(idea)
        
        print("4. جاري النشر على بنترست...")
        success = upload_to_pinterest(title, description, image_path)
        
        if success:
            save_to_history(idea)
            print(f"✅ تم النشر بنجاح وتم تحديث السجل: {title}")
        else:
            print("❌ حدث خطأ أثناء النشر.")
            
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")

if __name__ == "__main__":
    main()
