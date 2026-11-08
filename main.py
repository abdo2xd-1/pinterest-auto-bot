import os
import json
import random

# ==========================================
# 1. إعدادات الملفات
# ==========================================
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
# 3. اختيار فكرة فريدة من القائمة الجاهزة
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
    
    available_ideas = [idea for idea in ideas_pool if idea not in history]
    if not available_ideas:
        available_ideas = ideas_pool
        
    selected_idea = random.choice(available_ideas)
    return selected_idea

# ==========================================
# 4. تجهيز المحتوى والسيو
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
    description = f"{title}\n\nDiscover how to build this amazing electronics project: {idea}. Perfect for makers and DIY enthusiasts!\n\n#DIYElectronics #ArduinoProject #TechMaker #ElectronicsHobby"
    return title, description

# ==========================================
# 5. التشغيل والتأكيد
# ==========================================
def main():
    try:
        history = load_history()
        
        print("1. جاري اختيار الفكرة وتجنب التكرار...")
        idea = generate_unique_idea(history)
        print(f"الفكرة: {idea}")
        
        print("2. جاري تجهيز المنشور والسيو...")
        title, description = generate_seo_content(idea)
        print(f"العنوان: {title}")
        
        # حفظ الفكرة في السجل لضمان عدم تكرارها مستقبلاً
        save_to_history(idea)
        print("✅ تم معالجة الفكرة وحفظها في السجل بنجاح تام بدون أخطاء!")
            
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")

if __name__ == "__main__":
    main()
