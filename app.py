import streamlit as st
import requests
from urllib.parse import quote

# -------------------------------------------------
# 1. PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Pro AI Car Consultant", 
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# 2. PREMIUM UI STYLING WITH AUTOMOTIVE BACKGROUND
# -------------------------------------------------
def apply_professional_styling():
    st.markdown("""
        <style>
        /* Auto Showroom Background with Dark Overlay */
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }

        .stApp::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(10, 10, 15, 0.75);
            z-index: -1;
        }

        /* Premium Chat Bubbles */
        .stChatMessage {
            background-color: rgba(255, 255, 255, 0.92);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            backdrop-filter: blur(8px);
            transition: transform 0.2s ease;
        }
        .stChatMessage:hover {
            transform: translateY(-2px);
        }

        /* Chat Input */
        .stChatInput {
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 12px;
            border: 2px solid rgba(76, 175, 80, 0.2);
        }

        /* Header & Text Styling */
        .pro-header {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid rgba(76, 175, 80, 0.3);
        }
        h1, h2, h3, .stMarkdown p, .stCaption, .stAlert {
            color: white !important;
            font-family: 'Segoe UI', Roboto, sans-serif;
        }

        /* Image Styles */
        .stImage > caption {
            color: white !important;
            font-weight: 700;
            font-size: 1rem;
            margin-top: 8px;
        }

        /* Interactive Elements */
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
            transition: background-color 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #43A047;
        }
        .stWarning {
            background-color: rgba(255, 193, 7, 0.2);
            border-radius: 12px;
        }
        .stError {
            background-color: rgba(244, 67, 54, 0.2);
            border-radius: 12px;
        }

        /* Footer */
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid rgba(255,255,255,0.1);
            color: rgba(255,255,255,0.7);
            font-size: 0.9rem;
        }
        </style>
    """, unsafe_allow_html=True)

apply_professional_styling()

# -------------------------------------------------
# 3. SECRETS MANAGEMENT
# -------------------------------------------------
GROQ_KEY = st.secrets.get("GROQ_KEY", None)
UNSPLASH_KEY = st.secrets.get("UNSPLASH_KEY", None)

if not GROQ_KEY:
    st.error("❌ Missing GROQ API Key! Please add it to your Streamlit Secrets.")
    st.stop()
if not UNSPLASH_KEY:
    st.warning("⚠️ Unsplash API Key not found. Using fallback car images.")

# -------------------------------------------------
# 4. CAR MARKET DATA (2024-2025)
# -------------------------------------------------
def get_latest_car_data():
    return """
    2024-2025 Automotive Market Insights:
    - EV Leaders: Tesla Model 3 Highland (333mi range, $38,990), Hyundai Ioniq 6 (361mi, $41,600), BYD Seal (323mi, $37,490)
    - Top Hybrids: Toyota RAV4 Hybrid (41 MPG, $30,300), Honda CR-V Hybrid (40 MPG, $32,400), Kia Sportage Hybrid (42 MPG, $28,500)
    - Luxury EVs: BMW i7 (321mi, $105,700), Mercedes EQS (350mi, $104,400), Audi e-tron GT (238mi, $106,500)
    - Budget Cars: Toyota Corolla (35 MPG, $21,550), Honda Civic (36 MPG, $23,950), Hyundai Elantra (37 MPG, $22,790)
    Market Trends: EV prices down 12% YoY, hybrid sales up 28%, 80% of new car buyers prioritize fuel efficiency.
    """

# -------------------------------------------------
# 5. GROQ AI CHATBOT
# -------------------------------------------------
def car_expert_chat(prompt: str, market_data: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content":
                "You are a Senior Automotive Consultant with 18 years of experience. Provide detailed, unbiased advice with pros/cons, specs, pricing, and market context. "
                "Structure responses clearly with bullet points for readability. Avoid jargon unless asked. Be friendly and helpful."},
            {"role": "user", "content": f"MARKET DATA: {market_data}\n\nUSER QUESTION: {prompt}"}
        ],
        "temperature": 0.6,
        "max_tokens": 1200,
        "stream": False
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Sorry, I couldn't process your request: {str(e)}"

# -------------------------------------------------
# 6. CAR IMAGE FETCHING
# -------------------------------------------------
FALLBACK_CAR_IMAGES = {
    "tesla model 3": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Tesla_Model_3_%282020%29_front_left.jpg/800px-Tesla_Model_3_%282020%29_front_left.jpg",
    "hyundai ioniq 6": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/2022_Hyundai_Ioniq_6_SEL.jpg/800px-2022_Hyundai_Ioniq_6_SEL.jpg",
    "byd seal": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/BYD_Seal_%282022%29_front_left.jpg/800px-BYD_Seal_%282022%29_front_left.jpg",
    "toyota rav4 hybrid": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/2022_Toyota_RAV4_Hybrid_XLE.jpg/800px-2022_Toyota_RAV4_Hybrid_XLE.jpg",
    "honda cr-v": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/2022_Honda_CR-V_Touring.jpg/800px-2022_Honda_CR-V_Touring.jpg",
    "kia sportage": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/2022_Kia_Sportage_SX_Prestige.jpg/800px-2022_Kia_Sportage_SX_Prestige.jpg",
    "bmw i7": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/2023_BMW_i7_xDrive60.jpg/800px-2023_BMW_i7_xDrive60.jpg",
    "mercedes eqs": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/2022_Mercedes-Benz_EQS_580_4MATIC.jpg/800px-2022_Mercedes-Benz_EQS_580_4MATIC.jpg",
    "audi e-tron gt": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/2022_Audi_e-tron_GT_quattro.jpg/800px-2022_Audi_e-tron_GT_quattro.jpg",
    "toyota corolla": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/2020_Toyota_Corolla_SE.jpg/800px-2020_Toyota_Corolla_SE.jpg",
    "honda civic": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/2022_Honda_Civic_Sport.jpg/800px-2022_Honda_Civic_Sport.jpg",
    "hyundai elantra": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/2021_Hyundai_Elantra_SEL.jpg/800px-2021_Hyundai_Elantra_SEL.jpg",
}

def extract_car_models(text: str):
    lowered = text.lower()
    models = []
    for model in FALLBACK_CAR_IMAGES.keys():
        if model in lowered and model not in models:
            models.append(model)
    return models

def fetch_car_image(model: str):
    if UNSPLASH_KEY:
        try:
            url = f"https://api.unsplash.com/search/photos?query={quote(f'2024 {model} car')}&per_page=1&client_id={UNSPLASH_KEY}"
            response = requests.get(url, timeout=8)
            if response.status_code == 200:
                data = response.json()
                if data["results"]:
                    return data["results"][0]["urls"]["regular"]
        except Exception:
            pass
    return FALLBACK_CAR_IMAGES.get(model, "https://via.placeholder.com/400x225?text=No+Image+Available")

def show_car_gallery(models):
    if not models:
        return
    cols = st.columns(min(3, len(models)))
    for idx, model in enumerate(models):
        with cols[idx % 3]:
            st.image(fetch_car_image(model), caption=model.title(), use_column_width=True)

# -------------------------------------------------
# 7. MAIN UI INTERFACE
# -------------------------------------------------
# Premium Header
st.markdown("""
    <div class="pro-header">
        <h1 style="margin:0; font-size: 2.5rem;">🚗 Pro AI Car Consultant</h1>
        <span style="color: #4CAF50; font-weight: 700; font-size: 1.2rem;">2024 Edition</span>
    </div>
""", unsafe_allow_html=True)
st.markdown("### Your trusted automotive expert for specs, comparisons, and buying advice.")

# Initialize Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hello! 👋 I'm your professional car consultant. Ask me anything about cars—specs, comparisons, market trends, or buying guides!", "models": []}
    ]

# Render Chat
for msg in st.session_state.chat_history:
    avatar = "👤" if msg["role"] == "user" else "🚗"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg["models"]:
            show_car_gallery(msg["models"])

# User Input
if user_query := st.chat_input("Type your question here... e.g., 'Should I buy a Tesla Model 3 or Hyundai Ioniq 6?'"):
    # Add User Message
    st.session_state.chat_history.append({"role": "user", "content": user_query, "models": []})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_query)

    # Generate Response
    with st.chat_message("assistant", avatar="🚗"):
        with st.spinner("Analyzing your request..."):
            market_data = get_latest_car_data()
            response = car_expert_chat(user_query, market_data)
            detected_models = extract_car_models(response)
            
            st.markdown(response)
            if detected_models:
                show_car_gallery(detected_models)
            
            # Save to History
            st.session_state.chat_history.append({"role": "assistant", "content": response, "models": detected_models})

# Footer
st.markdown("""
    <div class="footer">
        © 2024 Pro AI Car Consultant | Data Updated Q3 2024 | Powered by Groq AI & Unsplash
    </div>
""", unsafe_allow_html=True)
