import streamlit as st
import requests
from urllib.parse import quote

# -------------------------------------------------
# 1. PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="AI Car Consultant", 
    page_icon="🚗",
    layout="wide"
)

# -------------------------------------------------
# 2. FIXED CAR BACKGROUND CSS - MOBILE + DESKTOP OPTIMIZED
# -------------------------------------------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), 
                    url("https://www.pexels.com/photo/photography-of-gray-sports-car-919073/");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        color: white !important;
    }
    h1, h2, h3, p, li {
        color: white !important;
    }
    .stImage > caption {
        color: white !important;
        font-weight: 600;
    }
    .stSpinner > div > div {
        color: #4CAF50 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# 3. LOAD SECRETS
# -------------------------------------------------
GROQ_KEY = st.secrets.get("GROQ_KEY")
UNSPLASH_KEY = st.secrets.get("UNSPLASH_KEY")
if not GROQ_KEY:
    st.error("❌ Missing GROQ_KEY in Secrets!")
    st.stop()

# -------------------------------------------------
# 4. CAR MARKET CONTEXT
# -------------------------------------------------
def get_car_context():
    return """
    2024-2025 Car Market Data:
    - EVs: Tesla Model 3 Highland (333mi), Hyundai Ioniq 6 (361mi), BYD Seal (323mi)
    - Hybrids: Toyota RAV4 Hybrid (41 MPG), Honda CR-V Hybrid (40 MPG)
    - Luxury: BMW i7, Mercedes EQS, Audi e-tron GT
    - Budget: Toyota Corolla, Honda Civic, Hyundai Elantra
    Trend: EV prices down 12%, hybrid sales up 28%
    """

# -------------------------------------------------
# 5. CAR IMAGE INSERTION FUNCTIONS
# -------------------------------------------------
# Fallback car images (if Unsplash fails/no key)
FALLBACK_CAR_IMAGES = {
    "tesla model 3": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Tesla_Model_3_%282020%29_front_left.jpg/800px-Tesla_Model_3_%282020%29_front_left.jpg",
    "hyundai ioniq 6": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/2022_Hyundai_Ioniq_6_SEL.jpg/800px-2022_Hyundai_Ioniq_6_SEL.jpg",
    "byd seal": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/BYD_Seal_%282022%29_front_left.jpg/800px-BYD_Seal_%282022%29_front_left.jpg",
    "toyota rav4 hybrid": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/2022_Toyota_RAV4_Hybrid_XLE.jpg/800px-2022_Toyota_RAV4_Hybrid_XLE.jpg",
    "bmw i7": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/2023_BMW_i7_xDrive60.jpg/800px-2023_BMW_i7_xDrive60.jpg",
    "toyota corolla": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/2020_Toyota_Corolla_SE.jpg/800px-2020_Toyota_Corolla_SE.jpg"
}

def extract_car_models(text: str):
    """Extract car models from AI response"""
    lowered_text = text.lower()
    detected_models = []
    for model in FALLBACK_CAR_IMAGES.keys():
        if model in lowered_text and model not in detected_models:
            detected_models.append(model)
    return detected_models

def get_car_image_url(model: str):
    """Fetch image from Unsplash or use fallback"""
    if UNSPLASH_KEY:
        try:
            # Search for 2024 model car
            url = f"https://api.unsplash.com/search/photos?query={quote(f'2024 {model} car')}&per_page=1&client_id={UNSPLASH_KEY}"
            response = requests.get(url, timeout=8)
            if response.status_code == 200 and response.json()["results"]:
                return response.json()["results"][0]["urls"]["regular"]
        except Exception:
            pass
    # Fallback to Wikipedia image
    return FALLBACK_CAR_IMAGES.get(model, "https://via.placeholder.com/400x225?text=No+Image+Available")

def display_car_images(models):
    """Show car images in responsive grid"""
    if not models:
        return
    cols = st.columns(min(3, len(models)))
    for idx, model in enumerate(models):
        with cols[idx % 3]:
            st.image(get_car_image_url(model), caption=model.title(), use_column_width=True)

# -------------------------------------------------
# 6. GROQ AI CHATBOT
# -------------------------------------------------
def groq_car_chat(prompt: str, context: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are a professional car expert. Provide detailed, helpful advice with pros/cons and specs."},
            {"role": "user", "content": f"CONTEXT: {context}\n\nQUESTION: {prompt}"}
        ],
        "temperature": 0.6
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# -------------------------------------------------
# 7. MAIN CHAT UI
# -------------------------------------------------
st.title("🚗 AI Car Consultant")
st.markdown("### Your trusted automotive expert for specs, comparisons, and buying advice")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "Hi! 👋 Ask me anything about cars.", "models": []}]

# Render chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🚗"):
        st.markdown(msg["content"])
        display_car_images(msg["models"])

# User input
if user_prompt := st.chat_input("Type your question... e.g., 'Should I buy a Tesla Model 3 or Hyundai Ioniq 6?'"):
    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": user_prompt, "models": []})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_prompt)

    # Generate AI response
    with st.chat_message("assistant", avatar="🚗"):
        with st.spinner("Analyzing your request..."):
            context = get_car_context()
            ai_response = groq_car_chat(user_prompt, context)
            detected_models = extract_car_models(ai_response)
            
            # Show response and images
            st.markdown(ai_response)
            display_car_images(detected_models)
            
            # Save to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response, "models": detected_models})

