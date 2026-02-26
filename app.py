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
# 2. PROFESSIONAL CAR BACKGROUND + UI STYLING
# -------------------------------------------------
st.markdown(
    """
    <style>
    /* 🔹 CAR BACKGROUND (Responsive for Mobile & Desktop) */
    .stApp {
        background: linear-gradient(rgba(10, 12, 15, 0.85), rgba(10, 12, 15, 0.85)),
                    url("https://images.unsplash.com/photo-1617814076367-b759c7d7e739?auto=format&fit=crop&w=1920&q=80");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* 🔹 TEXT COLORS (White for readability) */
    h1, h2, h3, p, .stMarkdown, .stCaption {
        color: #ffffff !important;
        font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
    }

    /* 🔹 CHAT BUBBLES (Glassmorphism effect) */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.07) !important;
        backdrop-filter: blur(12px);
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.12);
        color: white !important;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }

    /* 🔹 CHAT INPUT FIELD */
    .stChatInput {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 16px;
        color: white !important;
        padding: 12px 16px;
    }

    /* 🔹 IMAGE CAPTIONS */
    .stImage > caption {
        color: #e0e0e0 !important;
        font-weight: 600;
        font-size: 0.95rem;
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
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# 3. SECRETS
# -------------------------------------------------
GROQ_KEY   = st.secrets.get("GROQ_KEY", None)
UNSPLASH_KEY = st.secrets.get("UNSPLASH_KEY", None)   # <-- free Unsplash access key

if not GROQ_KEY:
    st.error("❌ Missing GROQ_KEY in Secrets!")
    st.stop()
if not UNSPLASH_KEY:
    st.warning("⚠️ UNSPLASH_KEY not set – image lookup will fall back to static images.")

# -------------------------------------------------
# 4. CAR CONTEXT (simulated live market data)
# -------------------------------------------------
def get_car_context():
    return """
    Current Trending Cars (2024-2025):
    - Electric: Tesla Model 3 Highland, Hyundai Ioniq 6, BYD Seal.
    - SUVs: Toyota RAV4 Hybrid, Honda CR-V, Kia Sportage.
    - Luxury: BMW i7, Mercedes EQS, Audi e-tron GT.
    - Budget: Toyota Corolla, Honda Civic, Hyundai Elantra.
    Market Trend: Heavy shift towards Hybrids and EVs. Prices are stabilizing.
    """

# -------------------------------------------------
# 5. GROQ API CALL
# -------------------------------------------------
def groq_car_chat(prompt: str, context: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content":
                "You are a professional Car Expert. You know everything about engine specs, mileage, EV range, and car comparisons. "
                "Be helpful and give pros/cons. Keep answers concise."},
            {"role": "user", "content": f"CONTEXT: {context}\n\nUSER QUESTION: {prompt}"}
        ],
        "temperature": 0.7,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# -------------------------------------------------
# 6. HELPERS – extract car names & fetch images
# -------------------------------------------------
FALLBACK_IMAGE_MAP = {
    "tesla model 3": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Tesla_Model_3_%282020%29_front_left.jpg/800px-Tesla_Model_3_%282020%29_front_left.jpg",
    "tesla model 3 highland": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Tesla_Model_3_%282020%29_front_left.jpg/800px-Tesla_Model_3_%282020%29_front_left.jpg",
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

def _extract_car_names(text: str):
    lowered = text.lower()
    found = []
    for key in FALLBACK_IMAGE_MAP:
        if key in lowered and key not in found:
            found.append(key)
    return found

def get_unsplash_image_url(query: str) -> str | None:
    if not UNSPLASH_KEY:
        return None

    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "per_page": 1,
        "client_id": UNSPLASH_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
            if results:
                return results[0]["urls"]["regular"]
    except Exception:
        pass
    return None

def get_image_url_for_model(model_key: str) -> str:
    unsplash_url = get_unsplash_image_url(f"{model_key} car 2024")
    if unsplash_url:
        return unsplash_url
    return FALLBACK_IMAGE_MAP.get(model_key, "https://via.placeholder.com/400x225?text=No+Image")

def show_car_images(model_keys):
    if not model_keys:
        return
    cols = st.columns(min(3, len(model_keys)))
    for i, key in enumerate(model_keys):
        with cols[i % 3]:
            img_url = get_image_url_for_model(key)
            st.image(img_url, caption=key.title(), use_column_width=True)

# -------------------------------------------------
# 7. UI SETUP
# -------------------------------------------------
st.title("🚗 AI Car Consultant")
st.markdown("**Ask me about specs, comparisons, buying advice, or market trends!**")

if "car_messages" not in st.session_state:
    st.session_state.car_messages = []

# Render chat history
for msg in st.session_state.car_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("role") == "assistant" and msg.get("image_keys"):
            show_car_images(msg["image_keys"])

# -------------------- USER INPUT --------------------
if prompt := st.chat_input("Ex: Should I buy a Tesla Model 3 or a BMW i4?"):
    st.session_state.car_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing car specs…"):
            context = get_car_context()
            answer = groq_car_chat(prompt, context)
            car_keys = _extract_car_names(answer)

            st.markdown(answer)
            if car_keys:
                show_car_images(car_keys)
            else:
                st.caption("_No recognisable car model detected._")

            st.session_state.car_messages.append(
                {"role": "assistant", "content": answer, "image_keys": car_keys}
            )

# -------------------------------------------------
# 8. FOOTER
# -------------------------------------------------
st.markdown("""
<div class="footer">
    © 2024 AI Car Consultant | Data updated 2024‑Q3 | Powered by Groq & Unsplash
</div>
""", unsafe_allow_html=True)
