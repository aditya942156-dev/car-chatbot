import streamlit as st
import requests
from PIL import Image
import base64
from io import BytesIO

# -------------------------------------------------
# 1. PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="AI Car Consultant + Banner", page_icon="🚗", layout="wide")

# -------------------------------------------------
# 2. SECRETS
# -------------------------------------------------
GROQ_KEY     = st.secrets.get("GROQ_KEY", None)
UNSPLASH_KEY = st.secrets.get("UNSPLASH_KEY", None)   # free Unsplash key

if not GROQ_KEY:
    st.error("❌ Missing GROQ_KEY in Secrets!")
    st.stop()
if not UNSPLASH_KEY:
    st.warning("⚠️ UNSPLASH_KEY not set – Unsplash lookup disabled, using only fallback images.")

# -------------------------------------------------
# 3. GENERAL HELPERS
# -------------------------------------------------
def pil_to_base64(img: Image.Image) -> str:
    """Convert PIL image to base64 string (PNG)."""
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

# -------------------------------------------------
# 4. CAR CONTEXT (simulated market data)
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
            {
                "role": "system",
                "content":
                    "You are a professional Car Expert. You know everything about engine specs, "
                    "mileage, EV range, and car comparisons. Be helpful and give pros/cons."
            },
            {"role": "user", "content": f"CONTEXT: {context}\n\nUSER QUESTION: {prompt}"}
        ],
        "temperature": 0.7,
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"Error: {resp.text}"

# -------------------------------------------------
# 6. CAR IMAGE DATA (FALLBACK MAP + SPECS/BACKGROUNDS)
# -------------------------------------------------
CAR_DATA = {
    "tesla model 3": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/"
                     "Tesla_Model_3_%282020%29_front_left.jpg/800px-Tesla_Model_3_%282020%29_front_left.jpg",
        "background": "https://images.unsplash.com/photo-1619405399517-d4aa7cb4d4fe?w=1200&h=400&fit=crop",
        "specs": "🔋 Range: 272–363 mi | ⚡ 0–60 mph: 5.1 s | 🌍 24 kWh/100 mi"
    },
    "tesla model 3 highland": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/"
                     "Tesla_Model_3_%282020%29_front_left.jpg/800px-Tesla_Model_3_%282020%29_front_left.jpg",
        "background": "https://images.unsplash.com/photo-1619405399517-d4aa7cb4d4fe?w=1200&h=400&fit=crop",
        "specs": "🔋 Range: 272–363 mi | ⚡ 0–60 mph: 5.1 s | 🌍 24 kWh/100 mi"
    },
    "hyundai ioniq 6": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/"
                     "2022_Hyundai_Ioniq_6_SEL.jpg/800px-2022_Hyundai_Ioniq_6_SEL.jpg",
        "background": "https://images.unsplash.com/photo-1617469762169-df33d37bd0e4?w=1200&h=400&fit=crop",
        "specs": "🔋 Range: ~303 mi | ⚡ 0–60 mph: 6.2 s | 💰 From ~$32,550"
    },
    "byd seal": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/"
                     "BYD_Seal_%282022%29_front_left.jpg/800px-BYD_Seal_%282022%29_front_left.jpg",
        "background": "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1200&h=400&fit=crop",
        "specs": "🔋 Range: 265–373 mi | ⚡ 0–60 mph: ~5.9 s | 🌍 Popular in Asia/Europe"
    },
    "toyota rav4 hybrid": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/"
                     "2022_Toyota_RAV4_Hybrid_XLE.jpg/800px-2022_Toyota_RAV4_Hybrid_XLE.jpg",
        "background": "https://images.unsplash.com/photo-1500595046891-d8761a96a87f?w=1200&h=400&fit=crop",
        "specs": "⛽ 40–44 MPG | 🚙 Seats: 5 | 💰 From ~$33,050"
    },
    "honda cr-v": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/"
                     "2022_Honda_CR-V_Touring.jpg/800px-2022_Honda_CR-V_Touring.jpg",
        "background": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200&h=400&fit=crop",
        "specs": "⛽ 28–35 MPG | 🚙 Seats: 5 | 🎯 Cargo: 76.5 cu ft"
    },
    "kia sportage": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/"
                     "2022_Kia_Sportage_SX_Prestige.jpg/800px-2022_Kia_Sportage_SX_Prestige.jpg",
        "background": "https://images.unsplash.com/photo-1468276311594-df7cb65d8c50?w=1200&h=400&fit=crop",
        "specs": "⛽ 26–33 MPG | 🚙 Seats: 5 | 💰 From ~$26,610"
    },
    "bmw i7": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/"
                     "2023_BMW_i7_xDrive60.jpg/800px-2023_BMW_i7_xDrive60.jpg",
        "background": "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1200&h=400&fit=crop",
        "specs": "🔋 Range: ~380 mi | ⚡ 0–60 mph: 4.6 s | 💰 From ~$101,550"
    },
    "mercedes eqs": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/"
                     "2022_Mercedes-Benz_EQS_580_4MATIC.jpg/800px-2022_Mercedes-Benz_EQS_580_4MATIC.jpg",
        "background": "https://images.unsplash.com/photo-1482784160316-6c6ee4d5f18e?w=1200&h=400&fit=crop",
        "specs": "🔋 Range: 350–400 mi | ⚡ 0–60 mph: 4.3 s | 💰 From ~$99,650"
    },
    "audi e-tron gt": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/"
                     "2022_Audi_e-tron_GT_quattro.jpg/800px-2022_Audi_e-tron_GT_quattro.jpg",
        "background": "https://images.unsplash.com/photo-1553882900-f2b06423ff84?w=1200&h=400&fit=crop",
        "specs": "🔋 Range: ~249 mi | ⚡ 0–60 mph: 3.4 s | 💰 From ~$99,000"
    },
    "toyota corolla": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/"
                     "2020_Toyota_Corolla_SE.jpg/800px-2020_Toyota_Corolla_SE.jpg",
        "background": "https://images.unsplash.com/photo-1605425836025-e17989c5de11?w=1200&h=400&fit=crop",
        "specs": "⛽ 28–38 MPG | 🚙 Seats: 5 | 💰 From ~$22,050"
    },
    "honda civic": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/"
                     "2022_Honda_Civic_Sport.jpg/800px-2022_Honda_Civic_Sport.jpg",
        "background": "https://images.unsplash.com/photo-1489824904134-891ab64532f1?w=1200&h=400&fit=crop",
        "specs": "⛽ 30–42 MPG | 🚙 Seats: 5 | 💰 From ~$22,000"
    },
    "hyundai elantra": {
        "car_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/"
                     "2021_Hyundai_Elantra_SEL.jpg/800px-2021_Hyundai_Elantra_SEL.jpg",
        "background": "https://images.unsplash.com/photo-1506901925346-21bda4d32df4?w=1200&h=400&fit=crop",
        "specs": "⛽ 32–40 MPG | 🚙 Seats: 5 | 💰 From ~$20,250"
    },
}

# simple list used for detection
FALLBACK_IMAGE_MAP = {k: v["car_image"] for k, v in CAR_DATA.items()}

# -------------------------------------------------
# 7. IMAGE + CAR DETECTION HELPERS
# -------------------------------------------------
def _extract_car_names(text: str):
    """Return list of unique, lower-case car model names found in text."""
    lowered = text.lower()
    found = []
    for key in CAR_DATA:
        if key in lowered and key not in found:
            found.append(key)
    return found

def get_unsplash_image_url(query: str) -> str | None:
    """Use Unsplash API to get a car photo."""
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
        return None
    return None

def get_image_url_for_model(model_key: str) -> str:
    """Try Unsplash; if it fails use fallback, always returns some URL."""
    unsplash_url = get_unsplash_image_url(f"{model_key} car")
    if unsplash_url:
        return unsplash_url
    return FALLBACK_IMAGE_MAP.get(
        model_key,
        "https://via.placeholder.com/400x225?text=No+Image+Available"
    )

def show_car_cards(model_keys):
    """Display car cards with background + car photo + specs."""
    if not model_keys:
        return

    st.markdown("### 🖼️ Car Models Mentioned")

    cols = st.columns(2)
    for i, key in enumerate(model_keys):
        car_data = CAR_DATA.get(key, {})
        car_img = car_data.get("car_image", get_image_url_for_model(key))
        bg_img = car_data.get("background", "https://via.placeholder.com/800x400")
        specs = car_data.get("specs", "")

        with cols[i % 2]:
            html = f"""
            <style>
            .car-card {{
                position: relative;
                border-radius: 18px;
                overflow: hidden;
                box-shadow: 0 18px 40px rgba(0,0,0,0.45);
                margin: 18px 0;
                background: #111827;
                color: #f9fafb;
                font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }}
            .car-card-inner {{
                position: relative;
                min-height: 260px;
                display: grid;
                grid-template-columns: 1.1fr 1.2fr;
            }}
            .car-bg {{
                position: absolute;
                inset: 0;
                background-image:
                   linear-gradient(135deg, rgba(0,0,0,0.7), rgba(0,0,0,0.85)),
                   url('{bg_img}');
                background-size: cover;
                background-position: center;
                opacity: 0.95;
            }}
            .car-left {{
                position: relative;
                z-index: 2;
                padding: 24px 22px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                gap: 8px;
            }}
            .car-title {{
                font-size: 20px;
                font-weight: 700;
            }}
            .car-specs-small {{
                font-size: 12px;
                color: #d1d5db;
            }}
            .car-right {{
                position: relative;
                z-index: 2;
                display: flex;
                align-items: flex-end;
                justify-content: center;
                padding: 12px 12px 18px;
            }}
            .car-photo {{
                max-height: 200px;
                width: auto;
                filter: drop-shadow(0 20px 35px rgba(0,0,0,0.9));
            }}
            @media (max-width: 900px) {{
                .car-card-inner {{
                    grid-template-columns: 1fr;
                }}
                .car-right {{
                    padding-top: 0;
                }}
            }}
            </style>

            <div class="car-card">
              <div class="car-bg"></div>
              <div class="car-card-inner">
                <div class="car-left">
                    <div class="car-title">{key.title()}</div>
                    <div class="car-specs-small">{specs}</div>
                </div>
                <div class="car-right">
                    <img src="{car_img}" class="car-photo" alt="{key}">
                </div>
              </div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)

# -------------------------------------------------
# 8. BANNER GENERATOR COMPONENT
# -------------------------------------------------
def render_banner_generator():
    st.subheader("Banner Generator (Upload Your Car Image)")
    st.write("Upload a car image, and we’ll place it into a banner with a stylish background.")

    uploaded = st.file_uploader("Upload a car image", type=["png", "jpg", "jpeg"])

    accent = st.color_picker("Accent / highlight color (e.g. yellow)", "#ffc107")
    title_top = st.text_input("Small top text", "Today's Best Offer")
    title_main_1 = st.text_input("Main title line 1", "Best Car For")
    title_main_2 = st.text_input("Main title line 2 (accent)", "Rent Today")
    subtitle = st.text_area(
        "Subtitle text",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
        "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    )
    cta_text = st.text_input("Button text", "Book Now")
    phone = st.text_input("Phone", "+123 456 789 00")
    location = st.text_input("Location", "1234 Sunset Blvd, City")
    website = st.text_input("Website", "www.yourwebsite.com")

    if not uploaded:
        st.info("Upload a car image above to generate the banner.")
        return

    car_img = Image.open(uploaded).convert("RGBA")
    car_b64 = pil_to_base64(car_img)

    html = f"""
    <style>
    .banner-wrapper {{
        width: 100%;
        max-width: 1100px;
        margin: 30px auto;
        border-radius: 18px;
        overflow: hidden;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        box-shadow: 0 18px 45px rgba(0,0,0,0.55);
        position: relative;
        background: #111827;
        color: #f9fafb;
    }}
    .banner-inner {{
        position: relative;
        display: grid;
        grid-template-columns: 1.2fr 1.1fr;  /* text | car */
        min-height: 320px;
    }}
    .banner-right-bg {{
        position: absolute;
        right: -12%;
        top: -10%;
        bottom: -10%;
        width: 60%;
        background: linear-gradient(135deg, {accent}, #f59e0b);
        clip-path: polygon(18% 0, 100% 0, 100% 100%, 0 100%);
        z-index: 1;
    }}
    .banner-right-overlay {{
        position: absolute;
        right: -12%;
        top: -10%;
        bottom: -10%;
        width: 60%;
        background-image:
            linear-gradient(180deg, rgba(0,0,0,0.20), rgba(0,0,0,0.55)),
            url("https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=1200&q=80");
        background-size: cover;
        background-position: center;
        mix-blend-mode: multiply;
        clip-path: polygon(18% 0, 100% 0, 100% 100%, 0 100%);
        z-index: 2;
        opacity: 0.95;
    }}
    .banner-left {{
        padding: 40px 40px 35px 40px;
        position: relative;
        z-index: 3;
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 14px;
    }}
    .title-top {{
        font-size: 14px;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #9ca3af;
    }}
    .title-main {{
        font-size: 34px;
        font-weight: 800;
        line-height: 1.1;
    }}
    .title-main span.accent {{
        color: {accent};
    }}
    .subtitle {{
        margin-top: 8px;
        font-size: 13px;
        color: #d1d5db;
        max-width: 360px;
    }}
    .cta-btn {{
        margin-top: 18px;
        display: inline-block;
        background: {accent};
        color: #111827;
        font-weight: 700;
        padding: 10px 26px;
        border-radius: 999px;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-decoration: none;
        box-shadow: 0 10px 25px rgba(0,0,0,0.45);
    }}
    .footer-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        margin-top: 22px;
        font-size: 11px;
        color: #9ca3af;
    }}
    .footer-item-title {{
        font-weight: 600;
        color: #e5e7eb;
        margin-bottom: 2px;
    }}
    .banner-right {{
        position: relative;
        z-index: 4;
        padding: 30px 40px 25px 0;
        display: flex;
        align-items: flex-end;
        justify-content: center;
    }}
    .car-img {{
        max-height: 260px;
        width: auto;
        filter: drop-shadow(0 25px 40px rgba(0,0,0,0.9));
    }}
    .top-label {{
        position: absolute;
        left: 50%;
        top: -22px;
        transform: translateX(-50%);
        background: #111827;
        color: #e5e7eb;
        font-size: 10px;
        padding: 5px 18px;
        border-radius: 999px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.55);
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    @media (max-width: 900px) {{
        .banner-inner {{
            grid-template-columns: 1fr;
        }}
        .banner-right-bg,
        .banner-right-overlay {{
            right: -35%;
            width: 90%;
            opacity: 0.85;
        }}
        .banner-right {{
            padding-top: 0;
        }}
        .banner-left {{
            padding: 30px 22px 12px 22px;
        }}
    }}
    </style>

    <div class="banner-wrapper">
      <div class="top-label">Image Not Included</div>

      <div class="banner-inner">
        <div class="banner-right-bg"></div>
        <div class="banner-right-overlay"></div>

        <div class="banner-left">
            <div class="title-top">{title_top}</div>
            <div class="title-main">
                {title_main_1}<br>
                <span class="accent">{title_main_2}</span>
            </div>
            <div class="subtitle">{subtitle}</div>
            <a href="#" class="cta-btn">{cta_text}</a>

            <div class="footer-row">
                <div>
                    <div class="footer-item-title">Call Us</div>
                    <div>{phone}</div>
                </div>
                <div>
                    <div class="footer-item-title">Location</div>
                    <div>{location}</div>
                </div>
                <div>
                    <div class="footer-item-title">Website</div>
                    <div>{website}</div>
                </div>
            </div>
        </div>

        <div class="banner-right">
            <img class="car-img" src="data:image/png;base64,{car_b64}" alt="Car">
        </div>
      </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

# -------------------------------------------------
# 9. MAIN CHAT APP
# -------------------------------------------------
def render_car_chat():
    st.subheader("🚗 AI Car Consultant")
    st.markdown("Ask about specs, comparisons, EV range, or which car to buy.")

    if "car_messages" not in st.session_state:
        st.session_state.car_messages = []

    for msg in st.session_state.car_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("role") == "assistant" and msg.get("image_keys"):
                show_car_cards(msg["image_keys"])

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
                    show_car_cards(car_keys)
                else:
                    st.caption(
                        "_No recognisable car model detected – you can extend the detection list in `CAR_DATA`._"
                    )

                st.session_state.car_messages.append(
                    {"role": "assistant", "content": answer, "image_keys": car_keys}
                )

# -------------------------------------------------
# 10. APP LAYOUT – TABS
# -------------------------------------------------
st.title("🚗 Car Tools")

tab1, tab2 = st.tabs(["AI Car Consultant", "Banner Generator"])

with tab1:
    render_car_chat()

with tab2:
    render_banner_generator()
