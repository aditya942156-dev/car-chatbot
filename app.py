import streamlit as st
import requests
import time
from urllib.parse import quote

# -------------------------------------------------
# 0️⃣  PAGE CONFIG & BASIC SETTINGS
# -------------------------------------------------
st.set_page_config(
    page_title="🚗 AI Car Consultant",
    page_icon="🚗",
    layout="centered",          # feels nicer with a background image
    initial_sidebar_state="auto"
)

# -------------------------------------------------
# 1️⃣  SECRETS
# -------------------------------------------------
GROQ_KEY = st.secrets.get("GROQ_KEY", None)
UNSPLASH_KEY = st.secrets.get("UNSPLASH_ACCESS_KEY", None)

if not GROQ_KEY:
    st.error("❌ Missing GROQ_KEY in Secrets!")
    st.stop()
# Unsplash key is optional for the background; we’ll warn if it's missing.
if not UNSPLASH_KEY:
    st.warning("⚠️ UNSPLASH_ACCESS_KEY not set – background will be a solid colour.")

# -------------------------------------------------
# 2️⃣  HELPERS – Unsplash (with caching) & Groq
# -------------------------------------------------
def unsplash_search(query: str):
    """Return dict with image info or None on failure."""
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
        r.raise_for_status()
        data = r.json()
        results = data.get("results", [])
        if not results:
            return None
        photo = results[0]
        return {
            "url": photo["urls"]["regular"],
            "photographer": photo["user"]["name"],
            "unsplash_link": photo["links"]["html"]
        }
    except Exception as e:
        st.warning(f"Unsplash request error: {e}")
        return None


def get_unsplash_image_cached(query: str, ttl_seconds: int = 43200):
    """Cache Unsplash results (default 12 h) to stay well under the 50‑req/hr limit."""
    cache_key = f"unsplash:{quote(query.lower())}"
    now = time.time()
    if "unsplash_cache" not in st.session_state:
        st.session_state.unsplash_cache = {}

    cached = st.session_state.unsplash_cache.get(cache_key)
    if cached and now - cached["ts"] < ttl_seconds:
        return cached["data"]

    data = unsplash_search(query)
    if data:
        st.session_state.unsplash_cache[cache_key] = {"ts": now, "data": data}
    return data


def get_car_context():
    return """
    Current Trending Cars (2024-2025):
    - Electric: Tesla Model 3 Highland, Hyundai Ioniq 6, BYD Seal.
    - SUVs: Toyota RAV4 Hybrid, Honda CR-V, Kia Sportage.
    - Luxury: BMW i7, Mercedes EQS, Audi e-tron GT.
    - Budget: Toyota Corolla, Honda Civic, Hyundai Elantra.
    Market Trend: Heavy shift towards Hybrids and EVs. Prices are stabilizing.
    """


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
                "Be helpful and give pros/cons."},
            {"role": "user", "content": f"CONTEXT: {context}\n\nUSER QUESTION: {prompt}"}
        ],
        "temperature": 0.7,
    }
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"Error: {resp.text}"


# -------------------------------------------------
# 3️⃣  IMAGE HELPERS (car photos & background)
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


def get_image_url_for_model(model_key: str):
    """Unsplash first, fallback to static map, finally a placeholder."""
    unsplash_res = get_unsplash_image_cached(f"{model_key} car")
    if unsplash_res:
        return unsplash_res["url"]
    return FALLBACK_IMAGE_MAP.get(
        model_key,
        "https://via.placeholder.com/400x225?text=No+Image+Available"
    )


def show_car_images(model_keys):
    if not model_keys:
        return
    cols = st.columns(3)
    for i, key in enumerate(model_keys):
        data = get_unsplash_image_cached(f"{key} car")
        if data:
            with cols[i % 3]:
                st.image(
                    data["url"],
                    caption=f"{key.title()}\nPhoto by {data['photographer']} on Unsplash",
                    use_column_width=True
                )
        else:
            img_url = get_image_url_for_model(key)
            with cols[i % 3]:
                st.image(img_url, caption=key.title(), use_column_width=True)


def get_background_url():
    """Fetch a car‑road background from Unsplash and cache it for 12 h."""
    bg = get_unsplash_image_cached("car road highway", ttl_seconds=43200)
    if bg:
        return bg["url"]
    # fallback to a solid colour if Unsplash fails or key missing
    return None


# -------------------------------------------------
# 4️⃣  STYLE – BACKGROUND + BUTTON
# -------------------------------------------------
def inject_custom_css():
    bg_url = get_background_url()
    # If we have an image, use it; otherwise use a dark gradient.
    if bg_url:
        bg_css = f"""
        background-image: url("{bg_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        """
    else:
        bg_css = "background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);"

    # Semi‑transparent dark overlay to keep text readable on both light/dark themes
    overlay = """
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(0,0,0,0.35);
    z-index: -1;
    """

    st.markdown(
        f"""
        <style>
        .stApp {{
            {bg_css}
            {overlay}
        }}
        /* Make the chat input a little taller and give it a rounded look */
        .stTextInput > div > div > input {{
            padding: 12px;
            font-size: 1.05rem;
            border-radius: 8px;
        }}
        /* Primary button – a bit larger and with a car‑like colour */
        .stButton > button {{
            background-color: #ff6f00;          /* automotive orange */
            color: white;
            border-radius: 8px;
            padding: 0.6em 1.2em;
            font-size: 1rem;
            border: none;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            transition: background-color 0.2s ease;
        }}
        .stButton > button:hover {{
            background-color: #e65100;
        }}
        /* Make the assistant messages a tad more readable */
        .stChatMessage {{
            background-color: rgba(255,255,255,0.85);
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------
# 5️⃣  UI – CHAT + BUTTON
# -------------------------------------------------
def main():
    inject_custom_css()

    st.title("🚗 AI Car Consultant")
    st.caption("Ask me about specs, comparisons, or which car to buy!")

    # Initialise chat history
    if "car_messages" not in st.session_state:
        st.session_state.car_messages = []

    # Render existing messages
    for msg in st.session_state.car_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("role") == "assistant" and msg.get("image_keys"):
                show_car_images(msg["image_keys"])

    # -------------------------------------------------
    # 5️⃣ A – Styled button that runs a preset query
    # -------------------------------------------------
    if st.button("💡 Get a quick car suggestion"):
        # You can change this preset query to whatever you like
        preset_prompt = "What is the most fuel‑efficient SUV for 2025, and why?"
        # Treat it as if the user typed it
        st.session_state.car_messages.append({"role": "user", "content": preset_prompt})
        with st.chat_message("user"):
            st.markdown(preset_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                context = get_car_context()
                answer = groq_car_chat(preset_prompt, context)
                st.markdown(answer)
                car_keys = _extract_car_names(answer)
                if car_keys:
                    show_car_images(car_keys)
                else:
                    st.caption("_No recognisable car model detected._")
                st.session_state.car_messages.append(
                    {"role": "assistant", "content": answer, "image_keys": car_keys}
                )

    # -------------------------------------------------
    # 5️⃣ B – Regular chat input
    # -------------------------------------------------
    if prompt := st.chat_input("Ex: Should I buy a Tesla Model 3 or a BMW i4?"):
        # USER
        st.session_state.car_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # ASSISTANT
        with st.chat_message("assistant"):
            with st.spinner("Analyzing car specs…"):
                context = get_car_context()
                answer = groq_car_chat(prompt, context)
                st.markdown(answer)
                car_keys = _extract_car_names(answer)
                if car_keys:
                    show_car_images(car_keys)
                else:
                    st.caption("_No recognisable car model detected._")
                st.session_state.car_messages.append(
                    {"role": "assistant", "content": answer, "image_keys": car_keys}
                )

    # -------------------------------------------------
    # 6️⃣  Footer
    # -------------------------------------------------
    st.markdown(
        "<div style='text-align:center; color:grey; font-size:0.85rem; margin-top:2rem;'>"
        "Made with ❤️ by Streamlit • Powered by Groq & Unsplash"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
