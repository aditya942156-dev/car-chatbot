import streamlit as st
import requests
import re
from urllib.parse import quote

# -------------------------------------------------
# 1. PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="AI Car Consultant",
    page_icon="🚗",
    layout="wide"               # Required for background image
)

# -------------------------------------------------
# 1.5  BACKGROUND IMAGE CSS
# -------------------------------------------------
# ✅ Replace '/static/bg.jpg' with your image path
#    • If image is in /static folder  → "/static/bg.jpg"
#    • If hosted online             → "https://example.com/bg.jpg"
BG_IMAGE_URL = "/static/bg.jpeg"  

st.markdown(
    f"""
    <style>
    /* Full‑page background */
    .stApp {{
        background-image: url("{BG_IMAGE_URL}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Dark overlay for readability */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.45);   /* Overlay opacity */
        z-index: -1;
    }}

    /* Global text color */
    .stApp {{ color: #ffffff !important; }}

    /* Chat message styling */
    div.stChatMessage.user div.stChatMessageContent {{
        background-color: rgba(255, 255, 255, 0.88) !important;
        color: black !important;
        border-radius: 12px;
        padding: 12px;
    }}
    div.stChatMessage.assistant div.stChatMessageContent {{
        background-color: rgba(0, 0, 0, 0.65) !important;
        color: white !important;
        border-radius: 12px;
        padding: 12px;
    }}

    /* Headers & titles */
    h1, h2, h3, .css-10trblm, .css-1avshcd {{ 
        color: #ffffff !important; 
    }}

    /* Input box */
    div.stChatInputContainer input {{
        background-color: rgba(255,255,255,0.92) !important;
        color: black !important;
        border-radius: 8px;
        padding: 8px 12px;
    }}

    /* Hide Streamlit's default menu/footer */
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
    st.error("❌ **Missing GROQ_KEY** in Streamlit Secrets! Please add it to continue.")
    st.stop()
if not UNSPLASH_KEY:
    st.warning("⚠️ UNSPLASH_KEY not set – image lookup will fall back to static map.")

# -------------------------------------------------
# 3. CAR CONTEXT (simulated live market data)
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
# 4. GROQ API CALL
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
                "Be helpful and give pros/cons. Keep answers concise (max 300 words)."},
            {"role": "user", "content": f"CONTEXT: {context}\n\nUSER QUESTION: {prompt}"}
        ],
        "temperature": 0.7,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        return f"🚨 API Error ({resp.status_code}): {resp.text}"
    except Exception as e:
        return f"🚨 Connection Error: {str(e)}"

# -------------------------------------------------
# 5. HELPERS – extract car names & fetch images
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

def _extract_car_names(text: str) -> list:
    """Extract known car model names from text (case‑insensitive)."""
    lowered = text.lower()
    found = []
    for key in FALLBACK_IMAGE_MAP:
        if key in lowered and key not in found:
            found.append(key)
    return found

def get_unsplash_image_url(query: str) -> str | None:
    """Fetch image URL from Unsplash API."""
    if not UNSPLASH_KEY:
        return None

    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": f"{query} car",
        "per_page": 1,
        "client_id": UNSPLASH_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        if r.status_code == 200:
            data = r.json()
            if data.get("results"):
                return data["results"][0]["urls"]["regular"]
    except Exception:
        pass
    return None

def get_image_url_for_model(model_key: str) -> str:
    """Return image URL (Unsplash first → fallback)."""
    unsplash_url = get_unsplash_image_url(model_key)
    if unsplash_url:
        return unsplash_url
    return FALLBACK_IMAGE_MAP.get(model_key, "https://via.placeholder.com/400x225?text=No+Image")

def show_car_images(model_keys):
    """Display images in a 3‑column grid."""
    if not model_keys:
        return

    cols = st.columns(3)
    for i, key in enumerate(model_keys):
        img_url = get_image_url_for_model(key)
        with cols[i % 3]:
            st.image(img_url, caption=key.title(), use_column_width=True)

# -------------------------------------------------
# 6. UI SETUP
# -------------------------------------------------
st.title("🚗 AI Car Consultant")
st.markdown("""
Ask me anything about cars!  
*Examples:*  
- *“Compare Tesla Model 3 vs Hyundai Ioniq 6”*  
- *“What’s the best hybrid SUV under $30k?”*  
- *“Pros and cons of BMW i7”*
""")

# Initialize chat history
if "car_messages" not in st.session_state:
    st.session_state.car_messages = []

# Display chat history
for msg in st.session_state.car_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # Show images for assistant messages
        if msg["role"] == "assistant" and msg.get("image_keys"):
            show_car_images(msg["image_keys"])

# -------------------- USER INPUT --------------------
if prompt := st.chat_input("Ask about cars here…"):
    # Store & display user message
    st.session_state.car_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("🤖 Thinking about cars..."):
            context = get_car_context()
            answer = groq_car_chat(prompt, context)
            
            car_keys = _extract_car_names(answer)
            
            st.markdown(answer)
            
            if car_keys:
                show_car_images(car_keys)
            else:
                st.caption("_No car model detected in the answer._")
                
            # Save assistant message
            st.session_state.car_messages.append({
                "role": "assistant",
                "content": answer,
                "image_keys": car_keys
            })
