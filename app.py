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
# 2. NEW CAR BACKGROUND + UI STYLING  (MOBILE + DESKTOP)
# -------------------------------------------------
st.markdown("""
    <style>
    /* 🔹 NEW BACKGROUND IMAGE (Luxury Car Showroom) */
    .stApp {
        background: linear-gradient(rgba(10,12,15,0.85), rgba(10,12,15,0.85)),
                    url("https://images.unsplash.com/photo-1617814076367-b759c7d7e739?auto=format&fit=crop&q=80&w=2000");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* 🔹 GLASSMORPHISM CHAT BUBBLES */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.07) !important;
        backdrop-filter: blur(12px);
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.12);
        color: #ffffff !important;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }

    /* 🔹 TEXT COLORS */
    h1, h2, h3, p, li, .stMarkdown, .stCaption {
        color: #ffffff !important;
        font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
    }

    /* 🔹 IMAGE CAPTIONS */
    .stImage > caption {
        color: #e0e0e0 !important;
        font-weight: 600;
        font-size: 0.95rem;
    }

    /* 🔹 CHAT INPUT FIELD */
    .stChatInput {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 16px;
        color: white !important;
        padding: 12px 16px;
    }

    /* 🔹 SPINNER COLOR */
    .stSpinner > div > div {
        color: #4CAF50 !important;
    }

    /* 🔹 FOOTER */
    .footer {
        text-align: center;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid rgba(255,255,255,0.1);
        color: rgba(255,255,255,0.7);
        font-size: 0.85rem;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# 3. LOAD SECRETS
# -------------------------------------------------
GROQ_KEY = st.secrets.get("GROQ_KEY")
UNSPLASH_KEY = st.secrets.get("UNSPLASH_KEY")   # Optional but recommended

if not GROQ_KEY:
    st.error("❌ **MISSING GROQ_KEY** in Streamlit Secrets! Add it to continue.")
    st.stop()

# -------------------------------------------------
# 4. CAR MARKET CONTEXT (2024‑2025)
# -------------------------------------------------
def get_car_context():
    return """
    2024‑2025 Automotive Market Snapshot:
    • EVs: Tesla Model 3 Highland (333 mi), Hyundai Ioniq 6 (361 mi), BYD Seal (323 mi)
    • Hybrids: Toyota RAV4 Hybrid (41 MPG), Honda CR‑V Hybrid (40 MPG)
    • Luxury: BMW i7, Mercedes EQS, Audi e‑tron GT
    • Budget: Toyota Corolla, Honda Civic, Hyundai Elantra
    Trend: EV prices ↓12%, Hybrid sales ↑28%. Fuel efficiency is #1 buyer priority.
    """

# -------------------------------------------------
# 5. CAR IMAGE HANDLING
# -------------------------------------------------
FALLBACK_IMAGES = {
    "tesla model 3": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Tesla_Model_3_%282020%29_front_left.jpg/800px-Tesla_Model_3_%282020%29_front_left.jpg",
    "hyundai ioniq 6": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/2022_Hyundai_Ioniq_6_SEL.jpg/800px-2022_Hyundai_Ioniq_6_SEL.jpg",
    "byd seal": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/BYD_Seal_%282022%29_front_left.jpg/800px-BYD_Seal_%282022%29_front_left.jpg",
    "toyota rav4 hybrid": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/2022_Toyota_RAV4_Hybrid_XLE.jpg/800px-2022_Toyota_RAV4_Hybrid_XLE.jpg",
    "bmw i7": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/2023_BMW_i7_xDrive60.jpg/800px-2023_BMW_i7_xDrive60.jpg",
    "toyota corolla": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/2020_Toyota_Corolla_SE.jpg/800px-2020_Toyota_Corolla_SE.jpg"
}

def extract_car_models(text: str) -> list:
    """Find car models mentioned in the AI response"""
    text_lower = text.lower()
    found = []
    for model in FALLBACK_IMAGES.keys():
        if model in text_lower and model not in found:
            found.append(model)
    return found

def get_car_image_url(model: str) -> str:
    """Fetch image from Unsplash (if key exists) OR use fallback"""
    if UNSPLASH_KEY:
        try:
            url = f"https://api.unsplash.com/search/photos?query={quote(f'2024 {model} car')}&per_page=1&client_id={UNSPLASH_KEY}"
            resp = requests.get(url, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("results"):
                    return data["results"][0]["urls"]["regular"]
        except Exception:
            pass
    # Fallback to Wikipedia image
    return FALLBACK_IMAGES.get(model, "https://via.placeholder.com/400x225?text=No+Image")

def show_car_images(models: list):
    """Display images in a responsive grid"""
    if not models:
        return
    cols = st.columns(min(3, len(models)))  # Max 3 columns
    for idx, model in enumerate(models):
        with cols[idx % 3]:
            img_url = get_car_image_url(model)
            st.image(img_url, caption=model.title(), use_column_width=True)

# -------------------------------------------------
# 6. GROQ AI CHATBOT
# -------------------------------------------------
def groq_chat(prompt: str, context: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": 
             "You are a senior automotive consultant (15+ years experience). Provide detailed, unbiased advice with pros/cons, specs, pricing, and market context. Use bullet points for readability."},
            {"role": "user", "content": f"MARKET DATA: {context}\n\nUSER QUESTION: {prompt}"}
        ],
        "temperature": 0.6,
        "max_tokens": 1200
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=12)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ **Error**: {str(e)}"

# -------------------------------------------------
# 7. MAIN UI
# -------------------------------------------------
st.title("🚗 AI Car Consultant")
st.markdown("**Ask me anything about cars!** Specs, comparisons, buying advice, market trends…")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! 👋 I'm your AI Car Consultant. How can I help you today?", "models": []}
    ]

# Display chat history
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🚗"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        show_car_images(msg["models"])

# User input
if prompt := st.chat_input("e.g., 'Compare Tesla Model 3 vs Hyundai Ioniq 6'"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt, "models": []})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant", avatar="🚗"):
        with st.spinner("🔍 Analyzing..."):
            context = get_car_context()
            ai_reply = groq_chat(prompt, context)
            detected_models = extract_car_models(ai_reply)
            
            st.markdown(ai_reply)
            show_car_images(detected_models)
            
            # Save to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": ai_reply,
                "models": detected_models
            })

# -------------------------------------------------
# 8. FOOTER
# -------------------------------------------------
st.markdown("""
<div class="footer">
    © 2024 AI Car Consultant | Data updated Q3‑2024 | Powered by Groq & Unsplash
</div>
""", unsafe_allow_html=True)
