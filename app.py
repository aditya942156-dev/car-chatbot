import streamlit as st
import requests
import re
from urllib.parse import quote

# -------------------------------------------------
# 1. PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="AI Car Consultant", page_icon="🚗", layout="wide")

# -------------------------------------------------
# 1.5  BACKGROUND IMAGE SETUP
# -------------------------------------------------
# Uses your local image uploaded to /static folder. NO CHANGES NEEDED IF YOUR FILE STRUCTURE IS CORRECT
BG_IMAGE_URL = "/static/bg.jpg"

# CSS IS FULLY WRAPPED INSIDE STRING, Python will NOT run CSS as code
st.markdown(
    f"""
    <style>
    /* Full page background */
    .stApp {{
        background-image: url("{BG_IMAGE_URL}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Light dark overlay to make text readable over your dark car background */
    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        background-color: rgba(0, 0, 0, 0.15);
        z-index: -1;
    }}

    /* Global white text */
    .stApp {{ color: #ffffff !important; }}

    /* User chat message styling */
    div.stChatMessage.user div.stChatMessageContent {{
        background-color: rgba(255, 255, 255, 0.88) !important;
        color: black !important;
        border-radius: 10px;
        padding: 10px;
    }}

    /* Assistant chat message styling */
    div.stChatMessage.assistant div.stChatMessageContent {{
        background-color: rgba(0, 0, 0, 0.65) !important;
        color: white !important;
        border-radius: 12px;
        padding: 12px;
    }}

    /* Chat input box styling */
    div[data-testid="stChatInput"] textarea {{
        background-color: rgba(255,255,255,0.92) !important;
        color: black !important;
        border-radius: 8px;
    }}

    /* Hide default Streamlit menu and footer */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# 2. SECRETS
# -------------------------------------------------
GROQ_KEY   = st.secrets.get("GROQ_KEY", None)
UNSPLASH_KEY = st.secrets.get("UNSPLASH_KEY", None)

if not GROQ_KEY:
    st.error("❌ Missing GROQ_KEY in Streamlit Secrets!")
    st.stop()
if not UNSPLASH_KEY:
    st.warning("⚠️ UNSPLASH_KEY not set – car images will use fallback static images.")

# -------------------------------------------------
# 3. CAR MARKET DATA CONTEXT
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
# 4. GROQ LLM API CALL
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
                "You are a professional Car Expert. You know everything about engine specs, mileage, EV range, and car comparisons. Be helpful and give pros/cons, keep answers concise."},
            {"role": "user", "content": f"CONTEXT: {context}\n\nUSER QUESTION: {prompt}"}
        ],
        "temperature": 0.7,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        return f"⚠️ API Error: {resp.text}"
    except Exception as e:
        return f"⚠️ Connection Error: {str(e)}"

# -------------------------------------------------
# 5. CAR IMAGE HELPERS
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
    params = {"query": f"{query} car", "per_page": 1, "client_id": UNSPLASH_KEY}
    try:
        r = requests.get(url, params=params, timeout=8)
        if r.status_code == 200 and r.json().get("results"):
            return r.json()["results"][0]["urls"]["regular"]
    except:
        return None

def get_image_url_for_model(model_key: str) -> str:
    unsplash_url = get_unsplash_image_url(model_key)
    if unsplash_url:
        return unsplash_url
    return FALLBACK_IMAGE_MAP.get(model_key, "https://via.placeholder.com/400x225?text=No+Image+Available")

def show_car_images(model_keys):
    if not model_keys:
        return
    cols = st.columns(3)
    for i, key in enumerate(model_keys):
        with cols[i % 3]:
            st.image(get_image_url_for_model(key), caption=key.title(), use_column_width=True)

# -------------------------------------------------
# 6. MAIN UI & CHAT FUNCTIONALITY
# -------------------------------------------------
st.title("🚗 AI Car Consultant")
st.markdown("Ask me about specs, comparisons, or which car to buy!")

# Initialize chat history
if "car_messages" not in st.session_state:
    st.session_state.car_messages = []

# Render saved chat history
for msg in st.session_state.car_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("image_keys"):
            show_car_images(msg["image_keys"])

# User chat input
if prompt := st.chat_input("Ex: Should I buy a Tesla Model 3 or a BMW i4?"):
    st.session_state.car_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing car specs…"):
            answer = groq_car_chat(prompt, get_car_context())
            car_keys = _extract_car_names(answer)
            
            st.markdown(answer)
            if car_keys:
                show_car_images(car_keys)
            else:
                st.caption("_No car model detected in answer._")

            # Save response to chat history
            st.session_state.car_messages.append({"role": "assistant", "content": answer, "image_keys": car_keys})
