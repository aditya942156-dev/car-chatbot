import streamlit as st
import requests
import re

# ==================================================
# 1. PAGE CONFIG & PREMIUM UI STYLING
# ==================================================
st.set_page_config(page_title="EliteDrive AI", page_icon="🏎️", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)),
    url("https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=2000&q=80");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
    min-height: 100vh;
}

.title-container {
    text-align: center;
    margin-bottom: 1rem;
    animation: fadeIn 1.5s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}

.elite-title {
    font-family: 'Arial Black', sans-serif;
    font-size: 3.5rem !important;
    font-weight: 900 !important;
    background: linear-gradient(90deg, #ff6b35, #f7931e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 2px;
    margin-bottom: 0.5rem;
}

.tagline {
    color: rgba(255, 255, 255, 0.9);
    font-size: 1.2rem;
    font-weight: 300;
    margin-top: -0.5rem;
    margin-bottom: 1.5rem;
    text-shadow: 0 2px 4px rgba(0,0,0,0.5);
}

.stChatMessage {
    background: rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: blur(12px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}

.stChatMessage:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

.stChatMessage[data-testid="assistant"] {
    border-left: 4px solid #ff6b35;
}

.stTextInput>div>div>input {
    background: rgba(255, 255, 255, 0.1);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 1rem;
}

.car-image-card {
    border-radius: 12px;
    overflow: hidden;
    transition: transform 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.car-image-card:hover {
    transform: scale(1.03);
}

.car-image-caption {
    color: white;
    font-weight: 500;
    text-align: center;
    padding: 8px;
    background: rgba(0,0,0,0.5);
    margin-top: -4px;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# 2. SECRETS
# ==================================================
GROQ_KEY = st.secrets.get("GROQ_KEY", None)
UNSPLASH_KEY = st.secrets.get("UNSPLASH_KEY", None)

if not GROQ_KEY:
    st.error("❌ Missing GROQ_KEY in Secrets!")
    st.stop()

# ==================================================
# 3. CAR CONTEXT
# ==================================================
def get_car_context():
    return """
    Current Trending Cars 2025:
    - Indian Market: Tata Punch, Tata Nexon, Tata Harrier, Mahindra Thar, Mahindra Scorpio N, Mahindra XUV700, Hyundai Creta, Kia Seltos, Maruti Swift, Innova Crysta, Honda City, Hyundai Verna
    - International: Tesla Model 3, Hyundai Ioniq 6, BYD Seal, Toyota RAV4
    """

# ==================================================
# 4. GROQ API CALL
# ==================================================
def groq_car_chat(prompt: str, context: str) -> str:
    url = "https://api.groq.com/open/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content":
                "You are a professional car consultant. Give honest pros and cons, specs and real world advice."},
            {"role": "user", "content": f"CONTEXT: {context}\n\nUSER QUESTION: {prompt}"}
        ],
        "temperature": 0.7,
    }

    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"Error: {resp.text}"

# ==================================================
# 5. IMAGE HANDLING - FULLY CORRECTED
# ==================================================
FALLBACK_IMAGE_MAP = {
    # Indian cars
    "tata punch": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Tata_Punch.jpg/800px-Tata_Punch.jpg",
    "tata nexon": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Tata_Nexon_EV.jpg/800px-Tata_Nexon_EV.jpg",
    "tata harrier": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Tata_Harrier.jpg/800px-Tata_Harrier.jpg",
    "tata safari": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Tata_Safari.jpg/800px-Tata_Safari.jpg",
    "mahindra thar": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Mahindra_Thar.jpg/800px-Mahindra_Thar.jpg",
    "mahindra scorpio": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Mahindra_Scorpio.jpg/800px-Mahindra_Scorpio.jpg",
    "mahindra xuv700": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Mahindra_XUV700.jpg/800px-Mahindra_XUV700.jpg",
    "hyundai creta": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Hyundai_Creta.jpg/800px-Hyundai_Creta.jpg",
    "kia seltos": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Kia_Seltos.jpg/800px-Kia_Seltos.jpg",
    "maruti swift": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Maruti_Suzuki_Swift.jpg/800px-Maruti_Suzuki_Swift.jpg",
    "honda city": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Honda_City.jpg/800px-Honda_City.jpg",
    "hyundai verna": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Hyundai_Verna.jpg/800px-Hyundai_Verna.jpg",

    # International cars
    "tesla model 3": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Tesla_Model_3_%282020%29_front_left.jpg/800px-Tesla_Model_3_%282020%29_front_left.jpg",
    "byd seal": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/BYD_Seal_%282022%29_front_left.jpg/800px-BYD_Seal_%282022%29_front_left.jpg",
}

def extract_cars_from_text(text: str):
    """Exact matching only, no false positives"""
    lowered = text.lower()
    found = []
    for car_name in FALLBACK_IMAGE_MAP.keys():
        if car_name in lowered:
            found.append(car_name)
    return found

def get_image_url_for_model(model_key: str) -> str:
    return FALLBACK_IMAGE_MAP.get(model_key)

def show_car_images(model_keys):
    if not model_keys:
        return
    cols = st.columns(min(3, len(model_keys)))
    for i, key in enumerate(model_keys):
        img_url = get_image_url_for_model(key)
        with cols[i % 3]:
            st.markdown(f"""
            <div class="car-image-card">
                <img src="{img_url}" style="width:100%; border-radius:12px;">
                <div class="car-image-caption">{key.title()}</div>
            </div>
            """, unsafe_allow_html=True)

# ==================================================
# 6. MAIN UI AND FIXED LOGIC
# ==================================================
st.markdown("""
<div class="title-container">
    <div class="elite-title">ELITEDRIVE AI</div>
    <div class="tagline">Your Car Consultant</div>
</div>
""", unsafe_allow_html=True)

if "car_messages" not in st.session_state:
    st.session_state.car_messages = []

# Render chat history
for msg in st.session_state.car_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("image_keys"):
            show_car_images(msg["image_keys"])

# User input
if prompt := st.chat_input("Ask about any car..."):
    st.session_state.car_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing car data..."):

            # --------------------------
            # THE FIXED LOGIC IS HERE
            # --------------------------
            # 1. FIRST extract cars FROM WHAT THE USER ACTUALLY ASKED
            user_cars = extract_cars_from_text(prompt)

            # 2. Get answer from AI
            context = get_car_context()
            answer = groq_car_chat(prompt, context)

            # 3. IMPORTANT RULE:
            # If we found any cars in the user's prompt, WE ONLY USE THOSE.
            # We completely ignore any other cars mentioned by the AI.
            if user_cars:
                cars_to_show = user_cars
            else:
                # Only fall back to the AI answer if we found nothing at all
                cars_to_show = extract_cars_from_text(answer)

            # Show the answer
            st.markdown(answer)

            # Show only the correct images
            if cars_to_show:
                show_car_images(cars_to_show)

            # Save to history
            st.session_state.car_messages.append(
                {"role": "assistant", "content": answer, "image_keys": cars_to_show}
            )
