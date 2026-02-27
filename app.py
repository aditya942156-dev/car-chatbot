import streamlit as st
import requests
import re

# ==================================================
# 1. PAGE CONFIG & PREMIUM UI STYLING
# ==================================================
st.set_page_config(page_title="EliteDrive AI", page_icon="🏎️", layout="wide")

st.markdown("""
<style>
/* Premium Background */
.stApp {
    background: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)),
    url("https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=2000&q=80");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
    min-height: 100vh;
}

/* EliteDrive Title - Premium Car Theme */
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
    color: #ffffff;
    text-shadow: 0 0 10px rgba(255, 107, 53, 0.7),
                 0 0 20px rgba(255, 107, 53, 0.5);
    letter-spacing: 2px;
    margin-bottom: 0.5rem;
    background: linear-gradient(90deg, #ff6b35, #f7931e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.tagline {
    color: rgba(255, 255, 255, 0.9);
    font-size: 1.2rem;
    font-weight: 300;
    margin-top: -0.5rem;
    margin-bottom: 1.5rem;
    text-shadow: 0 2px 4px rgba(0,0,0,0.5);
}

/* Chat UI Enhancements */
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

.stButton>button {
    background: linear-gradient(135deg, #ff6b35, #f7931e);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(255, 107, 53, 0.4);
}

/* Car Image Cards */
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
if not UNSPLASH_KEY:
    st.warning("⚠️ UNSPLASH_KEY not set - using fallback images")

# ==================================================
# 3. CAR CONTEXT (Global + Indian Market Focus)
# ==================================================
def get_car_context():
    return """
    Current Trending Cars (2024-2025):
    - Global EV: Tesla Model 3, BYD Seal, Lucid Air, Porsche Taycan.
    - Luxury: Rolls-Royce Spectre, Bentley Bentayga, Mercedes-Maybach EQS.
    - SUVs: Range Rover Sport, Volvo EX90, Lexus RX.
    - Indian Market Leaders:
      • Compact SUVs: Tata Punch, Hyundai Creta, Kia Sonet, Mahindra XUV300.
      • Sedans: Honda City, Hyundai Verna, Maruti Suzuki Dzire.
      • SUVs: Mahindra Thar, Tata Safari, Tata Nexon, Toyota Fortuner.
      • Hybrids: Maruti Brezza Hybrid, Toyota Glanza.
    Market Trend: High demand for compact SUVs in India, shifting towards EVs in premium segment, prices stabilizing post-GST adjustments.
    """

# ==================================================
# 4. GROQ API CALL
# ==================================================
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
                "You are EliteDrive AI - a world-class car consultant expert in both global luxury vehicles AND the Indian automotive market. "
                "Provide detailed comparisons, technical specifications (mileage in kmpl/km per litre, engine cc), and advice on value for money. "
                "For Indian users, consider on-road price estimates, maintenance costs in rupees, and availability. "
                "Be professional, objective, and include pros/cons."},
            {"role": "user", "content": f"CONTEXT: {context}\n\nUSER QUESTION: {prompt}"}
        ],
        "temperature": 0.7,
    }

    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"Error: {resp.text}"

# ==================================================
# 5. IMAGE HANDLING (Updated with Indian Cars)
# ==================================================
FALLBACK_IMAGE_MAP = {
    # --- Global / Luxury (Existing) ---
    "tesla model 3": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Tesla_Model_3_%282020%29_front_left.jpg/800px-Tesla_Model_3_%282020%29_front_left.jpg",
    "hyundai ioniq 6": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/2022_Hyundai_Ioniq_6_SEL.jpg/800px-2022_Hyundai_Ioniq_6_SEL.jpg",
    "byd seal": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/BYD_Seal_%282022%29_front_left.jpg/800px-BYD_Seal_%282022%29_front_left.jpg",
    "toyota rav4 hybrid": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/2022_Toyota_RAV4_Hybrid_XLE.jpg/800px-2022_Toyota_RAV4_Hybrid_XLE.jpg",
    "bmw i7": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/2023_BMW_i7_xDrive60.jpg/800px-2023_BMW_i7_xDrive60.jpg",
    "mercedes eqs": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/2022_Mercedes-Benz_EQS_580_4MATIC.jpg/800px-2022_Mercedes-Benz_EQS_580_4MATIC.jpg",
    "audi e-tron gt": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/2022_Audi_e-tron_GT_quattro.jpg/800px-2022_Audi_e-tron_GT_quattro.jpg",
    "porsche taycan": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/2021_Porsche_Taycan_4S.jpg/800px-2021_Porsche_Taycan_4S.jpg",
    "rolls-royce spectre": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Rolls-Royce_Spectre_2023.jpg/800px-Rolls-Royce_Spectre_2023.jpg",
    
    # --- INDIAN MARKET CARS (NEW) ---
    "tata punch": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Tata_Punch_front_view.jpg/800px-Tata_Punch_front_view.jpg",
    "mahindra thar": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Mahindra_Thar_Roof_Off_delhi_auto_expo_2023_img_4445.jpg/800px-Mahindra_Thar_Roof_Off_delhi_auto_expo_2023_img_4445.jpg",
    "tata nexon": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/2020_Tata_Nexon_XZ%2B_Diesel_%28front%29.jpg/800px-2020_Tata_Nexon_XZ%2B_Diesel_%28front%29.jpg",
    "hyundai creta": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/2020_Hyundai_Creta_CRDi_Selekt_1.6_front.jpg/800px-2020_Hyundai_Creta_CRDi_Selekt_1.6_front.jpg",
    "honda city": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Honda_City_2nd_Gen_Front.jpg/800px-Honda_City_2nd_Gen_Front.jpg",
    "maruti swift": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Suzuki_Swift_ZXi_VI_Generation_front_view.jpg/800px-Suzuki_Swift_ZXi_VI_Generation_front_view.jpg",
    "mahindra xuv700": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Mahindra_XUV700_AX7.jpg/800px-Mahindra_XUV700_AX7.jpg",
    "maruti dzire": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Maruti_Suzuki_Dzire_ZXi.jpg/800px-Maruti_Suzuki_Dzire_ZXi.jpg",
    "tata safari": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Tata_Safari_2021.jpg/800px-Tata_Safari_2021.jpg",
    "hyundai verna": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/2020_Hyundai_Verna_SX.jpg/800px-2020_Hyundai_Verna_SX.jpg",
    "kia sonet": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Kia_Sonet_2021_front_view.jpg/800px-Kia_Sonet_2021_front_view.jpg",
    "mahindra bolero": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Mahindra_Bolero_Next_IMG_7895.jpg/800px-Mahindra_Bolero_Next_IMG_7895.jpg",
    "toyotta fortuner": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Toyota_Fortuner_IMG_9875.jpg/800px-Toyota_Fortuner_IMG_9875.jpg", # Fallback name
    "fortuner": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Toyota_Fortuner_IMG_9875.jpg/800px-Toyota_Fortuner_IMG_9875.jpg", # Short alias
}

def _extract_car_names(text: str):
    lowered = text.lower()
    found = []
    for key in FALLBACK_IMAGE_MAP:
        # Simple substring match ensures we catch partial mentions like "tata" or "thar"
        if key in lowered and key not in found:
            found.append(key)
    return found

def get_unsplash_image_url(query: str) -> str | None:
    if not UNSPLASH_KEY:
        return None
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": f"{query} car front view",
        "per_page": 1,
        "client_id": UNSPLASH_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        if r.status_code != 200:
            return None
        data = r.json()
        results = data.get("results", [])
        if results:
            return results[0]["urls"]["regular"]
    except Exception:
        pass
    return None

def get_image_url_for_model(model_key: str) -> str:
    # Try Unsplash first (good for variety)
    unsplash_url = get_unsplash_image_url(f"{model_key} car front view")
    if unsplash_url:
        return unsplash_url
    
    # Fall back to our curated database (Wikipedia Commons)
    return FALLBACK_IMAGE_MAP.get(model_key,
                                 "https://via.placeholder.com/400x225?text=No+Image+Available")

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
# 6. MAIN UI
# ==================================================
st.markdown("""
<div class="title-container">
    <div class="elite-title">ELITEDRIVE AI</div>
    <div class="tagline">Your Premium Car Consultant</div>
</div>
""", unsafe_allow_html=True)

if "car_messages" not in st.session_state:
    st.session_state.car_messages = []

# Render chat history
for msg in st.session_state.car_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("role") == "assistant" and msg.get("image_keys"):
            show_car_images(msg["image_keys"])

# User input
if prompt := st.chat_input("Ask about specs, comparisons (e.g., Tata Punch vs Hyundai Creta)..."):
    st.session_state.car_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing vehicle specs..."):
            context = get_car_context()
            answer = groq_car_chat(prompt, context)
            
            # Detect which cars were mentioned to fetch images
            car_keys = _extract_car_names(answer)
            
            st.markdown(answer)
            
            if car_keys:
                # Show images found in the response
                show_car_images(car_keys)
            else:
                st.caption("_No specific car model detected – try mentioning a car name!_")
                
            st.session_state.car_messages.append(
                {"role": "assistant", "content": answer, "image_keys": car_keys}
            )
