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
# 3. اختيار فكرة فريدة من القائمة الجاهزة (بدون أخطاء سيرفرات)
# ==========================================
def generate_unique_idea(history):
    ideas_pool = [
        "A cyberpunk glowing Arduino nano custom PCB board with neon LED traces",
        "An aesthetic Raspberry Pi retro gaming console built inside an old cassette tape",
        "A miniature DIY smart home automation hub with an OLED display and sensors",
        "A custom mechanical keyboard switch tester with a digital voltage meter display",
        "A glowing audio music spectrum analyzer VU meter using an ESP32 microchip",
        "A vintage pocket radio circuit board restored with modern glowing components",
        "A handmade portable soldering station with temperature control digital screen",
        "A futuristic RGB LED matrix clock built on a transparent acrylic sheet",
        "An IoT smart plant watering system circuit with moisture sensors and relays",
        "A custom modular breadboard electronics prototype with glowing jumper wires"
    ]
    
    # تصفية الأفكار غير المستخدمة سابقاً لتجنب التكرار
    available_ideas = [idea for idea in ideas_pool if idea not in history]
    
    if not available_ideas:
        available_ideas = ideas_pool # إعادة استخدام القائمة لو نفذت
        
    selected_idea = random.choice(available_ideas)
    return selected_idea

# ==========================================
# 4. توليد المحتوى والسيو (جاهز ومضمون)
# ==========================================
def generate_seo_content(idea):
    titles = [
        "Ultimate DIY Electronics Project You Must Try Today!",
        "Incredible Cyberpunk Arduino Circuit Build & Setup",
        "Amazing DIY Tech & Electronics Ideas for Makers",
        "Build Your Own Smart Home Circuit Easily at Home",
        "Top Aesthetic PCB & Microcontroller Project Inspiration"
    ]
    
    title = random.choice(titles)
    
    description = f"Discover how to build this amazing electronics project: {idea}. Perfect for hobbyists, makers, and DIY enthusiasts looking for cool tech inspiration.\n\n#DIYElectronics #ArduinoProject #TechMaker #SmartHome #ElectronicsHobby"
    
    call_to_action = "\n\n🔌 If you loved this project, make sure to follow our page for daily DIY electronics and tech inspiration!"
    final_description = description + call_to_action
    
    return title, final_description

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
        
        print("1. جاري اختيار فكرة فريدة من القائمة وتجنب التكرار...")
        idea = generate_unique_idea(history)
        print(f"الفكرة: {idea}")
        
        print("2. جاري تجهيز عنوان السيو والوصف بالإنجليزية...")
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
