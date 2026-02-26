import streamlit as st
import requests
import re
from urllib.parse import quote

# -------------------------------------------------
# 1. PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="AI Car Consultant", page_icon="🚗", layout="wide")

# Custom CSS for better styling with background images
st.markdown("""
<style>
    /* Car image container styling with background images */
    .car-image-container {
        position: relative;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 350px;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        overflow: hidden;
    }
    
    /* Dark overlay for better text readability */
    .car-image-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.4) 0%, rgba(0, 0, 0, 0.2) 100%);
        z-index: 1;
    }
    
    .car-image-wrapper {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        max-width: 100%;
        position: relative;
        z-index: 2;
        backdrop-filter: blur(10px);
    }
    
    .car-image-wrapper img {
        width: 100%;
        border-radius: 8px;
        object-fit: contain;
        max-height: 280px;
        display: block;
    }
    
    .car-image-caption {
        text-align: center;
        font-weight: bold;
        color: white;
        margin-top: 12px;
        font-size: 20px;
        text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.7);
        position: relative;
        z-index: 3;
    }
    
    .car-specs {
        position: relative;
        z-index: 2;
        background: rgba(255, 255, 255, 0.9);
        padding: 12px;
        border-radius: 8px;
        margin-top: 10px;
        font-size: 12px;
        color: #333;
    }
    
    .car-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 2. SECRETS
# -------------------------------------------------
GROQ_KEY   = st.secrets.get("GROQ_KEY", None)
UNSPLASH_KEY = st.secrets.get("UNSPLASH_KEY", None)

if not GROQ_KEY:
    st.error("❌ Missing GROQ_KEY in Secrets!")
    st.stop()
if not UNSPLASH_KEY:
    st.warning("⚠️ UNSPLASH_KEY not set – using fallback images only.")

# -------------------------------------------------
# 3. CAR CONTEXT
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
# 5. CAR DATA WITH BACKGROUND IMAGES
# -------------------------------------------------

# High-quality car background images (landscape/wide format)
CAR_DATA = {
    "tesla model 3": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Tesla_Model_3_%282020%29_front_left.jpg/800px-Tesla_Model_3_%282020%29_front_left.jpg",
        "background": "https://images.unsplash.com/photo-1619405399517-d4aa7cb4d4fe?w=1200&h=400&fit=crop",  # EV charging station
        "specs": "🔋 Range: 272-363 mi | ⚡ 0-60 mph: 5.1s | 🌍 EPA Efficiency: 24 kWh/100mi"
    },
    "tesla model 3 highland": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Tesla_Model_3_%282020%29_front_left.jpg/800px-Tesla_Model_3_%282020%29_front_left.jpg",
        "background": "https://images.unsplash.com/photo-1619405399517-d4aa7cb4d4fe?w=1200&h=400&fit=crop",
        "specs": "🔋 Range: 272-363 mi | ⚡ 0-60 mph: 5.1s | 🌍 EPA Efficiency: 24 kWh/100mi"
    },
    "hyundai ioniq 6": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/2022_Hyundai_Ioniq_6_SEL.jpg/800px-2022_Hyundai_Ioniq_6_SEL.jpg",
        "background": "https://images.unsplash.com/photo-1617469762169-df33d37bd0e4?w=1200&h=400&fit=crop",  # Modern highway
        "specs": "🔋 Range: 303 mi | ⚡ 0-60 mph: 6.2s | 💰 Starting: $32,550"
    },
    "byd seal": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/BYD_Seal_%282022%29_front_left.jpg/800px-BYD_Seal_%282022%29_front_left.jpg",
        "background": "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1200&h=400&fit=crop",  # Urban road
        "specs": "🔋 Range: 265-373 mi | ⚡ 0-60 mph: 5.9s | 🌍 Popular in China"
    },
    "toyota rav4 hybrid": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/2022_Toyota_RAV4_Hybrid_XLE.jpg/800px-2022_Toyota_RAV4_Hybrid_XLE.jpg",
        "background": "https://images.unsplash.com/photo-1500595046891-d8761a96a87f?w=1200&h=400&fit=crop",  # Scenic mountain road
        "specs": "⛽ MPG: 40-44 city | 🚙 Seats: 5 | 💰 Starting: $33,050"
    },
    "honda cr-v": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/2022_Honda_CR-V_Touring.jpg/800px-2022_Honda_CR-V_Touring.jpg",
        "background": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200&h=400&fit=crop",  # Off-road adventure
        "specs": "⛽ MPG: 28-35 | 🚙 Seats: 5 | 🎯 Cargo: 76.5 cu.ft"
    },
    "kia sportage": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/2022_Kia_Sportage_SX_Prestige.jpg/800px-2022_Kia_Sportage_SX_Prestige.jpg",
        "background": "https://images.unsplash.com/photo-1468276311594-df7cb65d8c50?w=1200&h=400&fit=crop",  # Sunset drive
        "specs": "⛽ MPG: 26-33 | 🚙 Seats: 5 | 💰 Starting: $26,610"
    },
    "bmw i7": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/2023_BMW_i7_xDrive60.jpg/800px-2023_BMW_i7_xDrive60.jpg",
        "background": "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1200&h=400&fit=crop",  # Luxury cityscape
        "specs": "🔋 Range: 380 mi | ⚡ 0-60 mph: 4.6s | 💰 Starting: $101,550"
    },
    "mercedes eqs": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/2022_Mercedes-Benz_EQS_580_4MATIC.jpg/800px-2022_Mercedes-Benz_EQS_580_4MATIC.jpg",
        "background": "https://images.unsplash.com/photo-1482784160316-6c6ee4d5f18e?w=1200&h=400&fit=crop",  # Night city lights
        "specs": "🔋 Range: 350-400 mi | ⚡ 0-60 mph: 4.3s | 💰 Starting: $99,650"
    },
    "audi e-tron gt": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/2022_Audi_e-tron_GT_quattro.jpg/800px-2022_Audi_e-tron_GT_quattro.jpg",
        "background": "https://images.unsplash.com/photo-1553882900-f2b06423ff84?w=1200&h=400&fit=crop",  # Track/performance
        "specs": "🔋 Range: 249 mi | ⚡ 0-60 mph: 3.4s | 💰 Starting: $99,000"
    },
    "toyota corolla": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/2020_Toyota_Corolla_SE.jpg/800px-2020_Toyota_Corolla_SE.jpg",
        "background": "https://images.unsplash.com/photo-1605425836025-e17989c5de11?w=1200&h=400&fit=crop",  # Family road trip
        "specs": "⛽ MPG: 28-38 | 🚙 Seats: 5 | 💰 Starting: $22,050"
    },
    "honda civic": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/2022_Honda_Civic_Sport.jpg/800px-2022_Honda_Civic_Sport.jpg",
        "background": "https://images.unsplash.com/photo-1489824904134-891ab64532f1?w=1200&h=400&fit=crop",  # Urban street
        "specs": "⛽ MPG: 30-42 | 🚙 Seats: 5 | 💰 Starting: $22,000"
    },
    "hyundai elantra": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/2021_Hyundai_Elantra_SEL.jpg/800px-2021_Hyundai_Elantra_SEL.jpg",
        "background": "https://images.unsplash.com/photo-1506901925346-21bda4d32df4?w=1200&h=400&fit=crop",  # Scenic highway
        "specs": "⛽ MPG: 32-40 | 🚙 Seats: 5 | 💰 Starting: $20,250"
    },
}

# -------------------------------------------------
# 6. HELPERS – extract car names & fetch images
# -------------------------------------------------

def _extract_car_names(text: str):
    """Return list of unique, lower-case car model names found in text"""
    lowered = text.lower()
    found = []
    for key in CAR_DATA:
        if key in lowered and key not in found:
            found.append(key)
    return found

def get_unsplash_image_url(query: str) -> str | None:
    """Call Unsplash API to get high-quality car image"""
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
        if r.status_code != 200:
            return None
        data = r.json()
        results = data.get("results", [])
        if results:
            return results[0]["urls"]["regular"]
    except Exception:
        pass
    return None

def show_car_images(model_keys):
    """Display car images with background images and specs"""
    if not model_keys:
        return

    st.markdown("### 🖼️ Car Models")
    
    cols = st.columns(2)  # 2 images per row for better visibility
    
    for i, key in enumerate(model_keys):
        car_data = CAR_DATA.get(key, {})
        car_img = car_data.get("car_image", "")
        bg_img = car_data.get("background", "")
        specs = car_data.get("specs", "")
        
        with cols[i % 2]:
            # Create HTML with background image
            html_content = f"""
            <div class="car-image-container" style="background-image: url('{bg_img}');">
                <div class="car-image-wrapper">
                    <img src="{car_img}" alt="{key}">
                </div>
            </div>
            <div class="car-image-caption">{key.title()}</div>
            """
            
            if specs:
                html_content += f'<div class="car-specs">{specs}</div>'
            
            st.markdown(html_content, unsafe_allow_html=True)

# -------------------------------------------------
# 7. UI SETUP
# -------------------------------------------------
st.title("🚗 AI Car Consultant")
st.markdown("Ask me about specs, comparisons, or which car to buy!")

if "car_messages" not in st.session_state:
    st.session_state.car_messages = []

# Render chat history
for msg in st.session_state.car_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("role") == "assistant" and msg.get("image_keys"):
            show_car_images(msg["image_keys"])

# User input
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
