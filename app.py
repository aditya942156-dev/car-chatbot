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
# 2. BACKGROUND & UI STYLING (AUTOMOTIVE THEME)
# -------------------------------------------------
def apply_car_theme():
    st.markdown("""
        <style>
        /* Luxury Car Showroom Background with Dark Overlay */
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }

        /* Dark Overlay for Text Readability */
        .stApp::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(15, 20, 25, 0.75);
            z-index: -1;
        }

        /* Modern Chat Bubbles */
        .stChatMessage {
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            backdrop-filter: blur(8px);
        }

        /* Chat Input Field */
        .stChatInput {
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 12px;
            border: 2px solid rgba(76, 175, 80, 0.2);
        }

        /* Text Styling */
        h1, h2, h3, .stMarkdown p, .stCaption, .stAlert {
            color: white !important;
            font-family: 'Segoe UI', Roboto, sans-serif;
        }

        /* Image Captions */
        .stImage > caption {
            color: white !important;
            font-weight: 700;
            font-size: 1rem;
        }

        /* Buttons & Spinners */
        .stSpinner > div > div {
            color: #4CAF50 !important;
        }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border-radius: 16px;
            border: none;
            padding: 10px 20px;
            font-weight: 600;
        }

        /* Footer */
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid rgba(255,255,255,0.1);
            color: rgba(255,255,255,0.7);
        }
        </style>
    """, unsafe_allow_html=True)

apply_car_theme()

# -------------------------------------------------
# 3. SECRETS MANAGEMENT
# -------------------------------------------------
GROQ_KEY = st.secrets.get("GROQ_KEY", None)
UNSPLASH_KEY = st.secrets.get("UNSPLASH_KEY", None)

if not GROQ_KEY:
    st.error("❌ Missing GROQ API Key! Add it to Streamlit Secrets.")
    st.stop()

# -------------------------------------------------
# 4. CAR MARKET DATA
# -------------------------------------------------
def get_car_context():
    return """
    2024 Car Market:
    - EVs: Tesla Model 3 (333mi), Hyundai Ioniq 6 (361mi), BYD Seal (323mi)
    - Hybrids: Toyota RAV4 Hybrid (41 MPG), Honda CR-V Hybrid (40 MPG)
    - Luxury: BMW i7, Mercedes EQS, Audi e-tron GT
    - Budget: Toyota Corolla, Honda Civic, Hyundai Elantra
    Trend: EV prices down 12%, hybrid sales up 28%
    """

# -------------------------------------------------
# 5. AI CHATBOT FUNCTION
# -------------------------------------------------
def car_chatbot(prompt: str, context: str) -> str:
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
# 6. CAR IMAGE FETCHING
# -------------------------------------------------
FALLBACK_IMAGES = {
    "tesla model 3": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Tesla_Model_3_%282020%29_front_left.jpg/800px-Tesla_Model_3_%282020%29_front_left.jpg",
    "hyundai ioniq 6": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/2022_Hyundai_Ioniq_6_SEL.jpg/800px-2022_Hyundai_Ioniq_6_SEL.jpg",
    "toyota rav4 hybrid": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/2022_Toyota_RAV4_Hybrid_XLE.jpg/800px-2022_Toyota_RAV4_Hybrid_XLE.jpg",
    "bmw i7": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/2023_BMW_i7_xDrive60.jpg/800px-2023_BMW_i7_xDrive60.jpg",
    "toyota corolla": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/2020_Toyota_Corolla_SE.jpg/800px-2020_Toyota_Corolla_SE.jpg"
}

def get_car_image(model: str):
    if UNSPLASH_KEY:
        try:
            url = f"https://api.unsplash.com/search/photos?query={quote(f'2024 {model} car')}&per_page=1&client_id={UNSPLASH_KEY}"
            resp = requests.get(url, timeout=8)
            if resp.status_code == 200 and resp.json()["results"]:
                return resp.json()["results"][0]["urls"]["regular"]
        except Exception:
            pass
    return FALLBACK_IMAGES.get(model.lower(), "https://via.placeholder.com/400x225?text=No+Image")

def extract_car_models(text: str):
    models = []
    for model in FALLBACK_IMAGES.keys():
        if model.lower() in text.lower():
            models.append(model)
    return list(set(models))

def show_images(models):
    if not models:
        return
    cols = st.columns(min(3, len(models)))
    for idx, model in enumerate(models):
        with cols[idx % 3]:
            st.image(get_car_image(model), caption=model.title(), use_column_width=True)

# -------------------------------------------------
# 7. MAIN UI
# -------------------------------------------------
st.title("🚗 AI Car Consultant")
st.markdown("### Your trusted automotive expert for specs, comparisons, and buying advice")

# Chat History
if "chat" not in st.session_state:
    st.session_state.chat = [{"role": "assistant", "content": "Hi! 👋 Ask me anything about cars.", "models": []}]

# Render Chat
for msg in st.session_state.chat:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🚗"):
        st.markdown(msg["content"])
        show_images(msg["models"])

# User Input
if prompt := st.chat_input("Type your question... e.g., 'Should I buy a Tesla Model 3 or Hyundai Ioniq 6?'"):
    st.session_state.chat.append({"role": "user", "content": prompt, "models": []})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🚗"):
        with st.spinner("Analyzing..."):
            context = get_car_context()
            response = car_chatbot(prompt, context)
            models = extract_car_models(response)
            
            st.markdown(response)
            show_images(models)
            st.session_state.chat.append({"role": "assistant", "content": response, "models": models})

# Footer
st.markdown("""
    <div class="footer">
        © 2024 AI Car Consultant | Powered by Groq & Unsplash
    </div>
""", unsafe_allow_html=True)
