import streamlit as st
import requests
import re
import base64
from pathlib import Path

# ==================================================
# 1. PAGE CONFIG
# ==================================================
st.set_page_config(page_title="EliteDrive AI", page_icon="🏎️", layout="wide")

# ==================================================
# BACKGROUND IMAGE LOADER
# Reads bg.jpg from same folder as app.py
# Place your dark car image as "bg.jpg" next to app.py
# ==================================================
def get_base64_bg(image_file: str) -> str | None:
    """Load local image and convert to base64 for CSS embedding."""
    path = Path(__file__).parent / image_file
    if path.exists():
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        ext = path.suffix.lstrip(".")
        mime = "jpeg" if ext in ("jpg", "jpeg") else ext
        return f"data:image/{mime};base64,{data}"
    return None

bg_data = get_base64_bg("bg.jpg")

# If local image not found, fall back to a dark supercar Unsplash URL
BG_URL = bg_data if bg_data else (
    "https://images.unsplash.com/photo-1544636331-e26879cd4d9b"
    "?auto=format&fit=crop&w=2000&q=80"
)

# ==================================================
# 2. PREMIUM UI STYLING
# ==================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&family=Orbitron:wght@400;700;900&display=swap');

/* ── ROOT VARIABLES ── */
:root {{
    --accent:     #ff4d00;
    --accent2:    #ffaa00;
    --glass:      rgba(8, 8, 12, 0.72);
    --border:     rgba(255, 77, 0, 0.25);
    --text:       #f0ece4;
    --subtext:    rgba(240, 236, 228, 0.6);
}}

/* ── BACKGROUND ── */
.stApp {{
    background-image: url("{BG_URL}");
    background-size: cover;
    background-position: center 30%;
    background-attachment: fixed;
    background-repeat: no-repeat;
    min-height: 100vh;
}}

/* Dark vignette overlay */
.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse at top,    rgba(0,0,0,0.55) 0%, transparent 60%),
        radial-gradient(ellipse at bottom, rgba(0,0,0,0.85) 0%, transparent 70%),
        linear-gradient(180deg, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0.65) 100%);
    pointer-events: none;
    z-index: 0;
}}

/* ── SCANLINE TEXTURE (subtle) ── */
.stApp::after {{
    content: "";
    position: fixed;
    inset: 0;
    background-image: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,0,0,0.06) 2px,
        rgba(0,0,0,0.06) 4px
    );
    pointer-events: none;
    z-index: 0;
}}

/* ── TITLE BLOCK ── */
.title-wrap {{
    text-align: center;
    padding: 2.5rem 0 1rem;
    position: relative;
}}

.brand-eyebrow {{
    font-family: 'Orbitron', monospace;
    font-size: 0.75rem;
    letter-spacing: 6px;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 0.4rem;
    opacity: 0.9;
}}

.elite-title {{
    font-family: 'Bebas Neue', cursive;
    font-size: clamp(3.5rem, 8vw, 7rem);
    line-height: 0.9;
    letter-spacing: 4px;
    background: linear-gradient(135deg, #ffffff 0%, #ff4d00 55%, #ffaa00 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: none;
    margin: 0;
    animation: titleReveal 1.2s cubic-bezier(0.22, 1, 0.36, 1) both;
}}

@keyframes titleReveal {{
    from {{ opacity: 0; transform: translateY(30px) skewX(-4deg); }}
    to   {{ opacity: 1; transform: translateY(0)  skewX(0deg); }}
}}

.tagline {{
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.15rem;
    font-weight: 300;
    letter-spacing: 3px;
    color: var(--subtext);
    text-transform: uppercase;
    margin-top: 0.6rem;
    animation: fadeUp 1.5s 0.3s ease both;
}}

/* Decorative divider */
.divider {{
    display: flex;
    align-items: center;
    gap: 12px;
    justify-content: center;
    margin: 1rem auto 2rem;
    width: 60%;
    animation: fadeUp 1.5s 0.5s ease both;
}}
.divider::before, .divider::after {{
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
}}
.divider-icon {{ color: var(--accent); font-size: 1.1rem; }}

@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(16px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

/* ── STATS BAR ── */
.stats-bar {{
    display: flex;
    justify-content: center;
    gap: 2.5rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}}
.stat-item {{
    text-align: center;
    font-family: 'Rajdhani', sans-serif;
}}
.stat-number {{
    font-family: 'Orbitron', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--accent);
    display: block;
}}
.stat-label {{
    font-size: 0.7rem;
    letter-spacing: 2px;
    color: var(--subtext);
    text-transform: uppercase;
}}

/* ── CHAT MESSAGES ── */
.stChatMessage {{
    background: var(--glass) !important;
    backdrop-filter: blur(18px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(18px) saturate(180%) !important;
    border-radius: 18px !important;
    border: 1px solid var(--border) !important;
    margin-bottom: 1.2rem !important;
    transition: box-shadow 0.3s ease, transform 0.3s ease !important;
    font-family: 'Rajdhani', sans-serif !important;
}}

.stChatMessage:hover {{
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 40px rgba(255, 77, 0, 0.15) !important;
}}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
    border-left: 3px solid var(--accent) !important;
}}

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] {{
    background: rgba(6, 6, 10, 0.88) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid var(--border) !important;
    border-radius: 50px !important;
    box-shadow: 0 8px 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.05) !important;
    padding: 4px 6px !important;
    transition: all 0.35s ease !important;
    font-family: 'Rajdhani', sans-serif !important;
}}

[data-testid="stChatInput"]:focus-within {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(255, 77, 0, 0.15),
                0 8px 40px rgba(255,77,0,0.2) !important;
    transform: translateY(-2px) !important;
}}

[data-testid="stChatInputTextArea"] {{
    color: var(--text) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 400 !important;
}}

[data-testid="stChatInputSubmitButton"] {{
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    border-radius: 50% !important;
    border: none !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}}

[data-testid="stChatInputSubmitButton"]:hover {{
    transform: scale(1.2) rotate(10deg) !important;
    box-shadow: 0 0 20px rgba(255,77,0,0.7) !important;
}}

/* ── SIDEBAR / GENERAL TEXT ── */
* {{ color: var(--text); }}

/* ── CAR CARD ── */
.car-card {{
    border-radius: 14px;
    overflow: hidden;
    position: relative;
    transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1),
                box-shadow 0.4s ease;
    box-shadow: 0 6px 24px rgba(0,0,0,0.4);
    background: #0a0a0e;
}}

.car-card:hover {{
    transform: scale(1.05) translateY(-6px);
    box-shadow: 0 20px 50px rgba(255, 77, 0, 0.3);
}}

.car-card img {{
    width: 100%;
    display: block;
    aspect-ratio: 16/9;
    object-fit: cover;
    filter: brightness(0.88) contrast(1.1) saturate(1.15);
    transition: filter 0.4s ease;
}}

.car-card:hover img {{
    filter: brightness(1.0) contrast(1.15) saturate(1.3);
}}

.car-card-label {{
    position: absolute;
    bottom: 0;
    left: 0; right: 0;
    padding: 10px 14px;
    background: linear-gradient(0deg, rgba(0,0,0,0.85) 0%, transparent 100%);
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #fff;
}}

.car-card-label span {{
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--accent);
    margin-right: 6px;
    vertical-align: middle;
    animation: pulse 1.5s infinite;
}}

@keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50%       {{ opacity: 0.5; transform: scale(0.7); }}
}}

/* ── SPINNER ── */
[data-testid="stSpinner"] {{ color: var(--accent) !important; }}

/* ── SCROLLBAR ── */
::-webkit-scrollbar {{ width: 5px; }}
::-webkit-scrollbar-track {{ background: rgba(0,0,0,0.3); }}
::-webkit-scrollbar-thumb {{ background: var(--accent); border-radius: 3px; }}
</style>
""", unsafe_allow_html=True)

# ==================================================
# 3. SECRETS
# ==================================================
GROQ_KEY     = st.secrets.get("GROQ_KEY",     None)
UNSPLASH_KEY = st.secrets.get("UNSPLASH_KEY", None)

if not GROQ_KEY:
    st.error("❌ Missing GROQ_KEY in Secrets!")
    st.stop()
if not UNSPLASH_KEY:
    st.toast("⚠️ UNSPLASH_KEY not set — using fallback car images", icon="⚠️")

# ==================================================
# 4. CAR CONTEXT
# ==================================================
def get_car_context() -> str:
    return """
    Current Trending Cars (2024-2025):

    ELECTRIC:
    - Tesla Model 3 Highland, Tesla Model S Plaid, Tesla Cybertruck
    - Hyundai Ioniq 6, Hyundai Ioniq 5 N
    - BYD Seal, BYD Atto 3
    - Lucid Air Grand Touring
    - Rivian R1T, Rivian R1S
    - Kia EV6 GT

    PERFORMANCE / SPORTS:
    - Porsche Taycan Turbo S, Porsche 911 GT3 RS
    - BMW M5 Competition, BMW M3 CS
    - Audi RS e-tron GT, Audi R8 V10 Plus
    - Ferrari SF90 Stradale, Ferrari Roma
    - Lamborghini Urus Performante, Lamborghini Huracan STO
    - Nissan 370Z, Nissan GT-R R35
    - Ford Mustang Dark Horse, Ford Mustang Shelby GT500
    - Chevrolet Corvette Z06, Dodge Challenger SRT Hellcat
    - Toyota GR Supra, Toyota GR86
    - Mazda MX-5 Miata RF, Honda Civic Type R

    LUXURY SEDANS & SUVs:
    - Mercedes-Maybach EQS 680, Mercedes-AMG GT 63
    - Rolls-Royce Spectre, Rolls-Royce Ghost
    - Bentley Bentayga EWB, Bentley Continental GT
    - BMW 7 Series i7, Audi A8 L
    - Range Rover Autobiography, Range Rover Sport SVR
    - Lexus LX 600 F Sport, Volvo EX90

    INDIAN MARKET:
    - Tata Punch EV, Tata Nexon EV Max, Tata Harrier EV, Tata Safari
    - Mahindra Thar Roxx, Mahindra XUV700, Mahindra Scorpio-N
    - Hyundai Creta EV, Hyundai Verna Turbo, Hyundai i20 N Line
    - Kia Seltos X-Line, Kia Carens
    - Maruti Suzuki Swift, Maruti Suzuki Jimny, Maruti Suzuki Grand Vitara
    - Toyota Innova HyCross, Toyota Fortuner Legender
    - Honda City Hybrid, Honda Elevate
    - MG Hector Plus, MG ZS EV

    MARKET TRENDS:
    - 40% EV adoption in premium segments globally
    - Indian EV market grew 90% YoY in 2024
    - Hybrid powertrains surging in India (25% of new registrations)
    - Performance EVs now outpace ICE sports cars in 0-100 times
    """

# ==================================================
# 5. GROQ API CALL
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
            {
                "role": "system",
                "content": (
                    "You are EliteDrive AI — a world-class automotive consultant with mastery in luxury, "
                    "performance, electric, and Indian market vehicles. Respond with sophisticated insight: "
                    "include real specs (0-100 times, power figures, range for EVs), pros/cons, ownership costs, "
                    "and market positioning. Use structured markdown with bold headers. Keep tone confident & premium."
                ),
            },
            {"role": "user", "content": f"MARKET CONTEXT:\n{context}\n\nUSER QUERY: {prompt}"},
        ],
        "temperature": 0.72,
        "max_tokens": 1024,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"⚠️ API Error {resp.status_code}: {resp.text}"

# ==================================================
# 6. IMAGE MAP — EXPANDED
# ==================================================
FALLBACK_IMAGE_MAP: dict[str, str] = {
    # ── TESLA ──────────────────────────────────────────────────
    "tesla model 3":         "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Tesla_Model_3_%282020%29_front_left.jpg/800px-Tesla_Model_3_%282020%29_front_left.jpg",
    "tesla model s plaid":   "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/2021_Tesla_Model_S_Plaid.jpg/800px-2021_Tesla_Model_S_Plaid.jpg",
    "tesla cybertruck":      "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Tesla_Cybertruck_2024.jpg/800px-Tesla_Cybertruck_2024.jpg",

    # ── HYUNDAI ────────────────────────────────────────────────
    "hyundai ioniq 6":       "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/2022_Hyundai_Ioniq_6_SEL.jpg/800px-2022_Hyundai_Ioniq_6_SEL.jpg",
    "hyundai ioniq 5 n":     "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/2022_Hyundai_Ioniq_6_SEL.jpg/800px-2022_Hyundai_Ioniq_6_SEL.jpg",
    "hyundai creta":         "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Hyundai_Creta_2020.jpg/800px-Hyundai_Creta_2020.jpg",
    "hyundai verna":         "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/2023_Hyundai_Verna_front.jpg/800px-2023_Hyundai_Verna_front.jpg",
    "hyundai i20":           "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/2021_Hyundai_i20_N_Line_front.jpg/800px-2021_Hyundai_i20_N_Line_front.jpg",

    # ── BYD ────────────────────────────────────────────────────
    "byd seal":              "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/BYD_Seal_%282022%29_front_left.jpg/800px-BYD_Seal_%282022%29_front_left.jpg",
    "byd atto 3":            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/BYD_Atto_3.jpg/800px-BYD_Atto_3.jpg",

    # ── PORSCHE ────────────────────────────────────────────────
    "porsche taycan":        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/2021_Porsche_Taycan_4S.jpg/800px-2021_Porsche_Taycan_4S.jpg",
    "porsche 911 gt3":       "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Porsche_911_GT3_RS_992.jpg/800px-Porsche_911_GT3_RS_992.jpg",

    # ── BMW ────────────────────────────────────────────────────
    "bmw m5":                "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/2022_BMW_M5_Competition.jpg/800px-2022_BMW_M5_Competition.jpg",
    "bmw m3":                "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/2021_BMW_M3_Competition_front.jpg/800px-2021_BMW_M3_Competition_front.jpg",
    "bmw i7":                "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/2023_BMW_i7_xDrive60.jpg/800px-2023_BMW_i7_xDrive60.jpg",

    # ── AUDI ───────────────────────────────────────────────────
    "audi rs e-tron gt":     "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/2022_Audi_e-tron_GT_quattro.jpg/800px-2022_Audi_e-tron_GT_quattro.jpg",
    "audi r8":               "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/2020_Audi_R8_V10_Performance.jpg/800px-2020_Audi_R8_V10_Performance.jpg",

    # ── MERCEDES ───────────────────────────────────────────────
    "mercedes eqs":          "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/2022_Mercedes-Benz_EQS_580_4MATIC.jpg/800px-2022_Mercedes-Benz_EQS_580_4MATIC.jpg",
    "mercedes amg gt":       "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/2022_Mercedes-AMG_GT_63_S.jpg/800px-2022_Mercedes-AMG_GT_63_S.jpg",

    # ── SUPERCAR / ULTRA LUXURY ────────────────────────────────
    "ferrari sf90":          "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Ferrari_SF90_Stradale_%282019%29_front_left.jpg/800px-Ferrari_SF90_Stradale_%282019%29_front_left.jpg",
    "lamborghini urus":      "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Lamborghini_Urus_%282018%29_front_left.jpg/800px-Lamborghini_Urus_%282018%29_front_left.jpg",
    "rolls-royce spectre":   "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/2024_Rolls-Royce_Spectre.jpg/800px-2024_Rolls-Royce_Spectre.jpg",
    "lucid air":             "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Lucid_Air_Dream_Edition.jpg/800px-Lucid_Air_Dream_Edition.jpg",

    # ── SPORTS / MUSCLE ────────────────────────────────────────
    "ford mustang":          "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/2024_Ford_Mustang_Dark_Horse.jpg/800px-2024_Ford_Mustang_Dark_Horse.jpg",
    "chevrolet corvette":    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/2023_Chevrolet_Corvette_Z06.jpg/800px-2023_Chevrolet_Corvette_Z06.jpg",
    "dodge challenger":      "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/2023_Dodge_Challenger_SRT_Hellcat.jpg/800px-2023_Dodge_Challenger_SRT_Hellcat.jpg",
    "nissan 370z":           "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Nissan_370Z_2022.jpg/800px-Nissan_370Z_2022.jpg",
    "nissan gt-r":           "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/Nissan_GT-R_R35.jpg/800px-Nissan_GT-R_R35.jpg",
    "toyota gr supra":       "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/2020_Toyota_GR_Supra_front.jpg/800px-2020_Toyota_GR_Supra_front.jpg",
    "toyota gr86":           "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/2022_Toyota_GR86.jpg/800px-2022_Toyota_GR86.jpg",
    "honda civic type r":    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/2023_Honda_Civic_Type_R_FL5.jpg/800px-2023_Honda_Civic_Type_R_FL5.jpg",
    "mazda mx-5":            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/2022_Mazda_MX-5_RF.jpg/800px-2022_Mazda_MX-5_RF.jpg",
    "kia ev6 gt":            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/2023_Kia_EV6_GT.jpg/800px-2023_Kia_EV6_GT.jpg",

    # ── SUVs & ADVENTURE ───────────────────────────────────────
    "range rover":           "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/2022_Range_Rover_Sport_Autobiography.jpg/800px-2022_Range_Rover_Sport_Autobiography.jpg",
    "toyota rav4 hybrid":    "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/2022_Toyota_RAV4_Hybrid_XLE.jpg/800px-2022_Toyota_RAV4_Hybrid_XLE.jpg",
    "lexus rx":              "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/2023_Lexus_RX_350h_F_Sport.jpg/800px-2023_Lexus_RX_350h_F_Sport.jpg",
    "rivian r1t":            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/2022_Rivian_R1T_Truck.jpg/800px-2022_Rivian_R1T_Truck.jpg",

    # ── INDIAN MARKET ──────────────────────────────────────────
    "tata punch":            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Tata_Punch.jpg/800px-Tata_Punch.jpg",
    "tata nexon":            "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Tata_Nexon_EV.jpg/800px-Tata_Nexon_EV.jpg",
    "tata harrier":          "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Tata_Harrier.jpg/800px-Tata_Harrier.jpg",
    "tata safari":           "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Tata_Safari.jpg/800px-Tata_Safari.jpg",
    "mahindra thar":         "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Mahindra_Thar.jpg/800px-Mahindra_Thar.jpg",
    "mahindra xuv700":       "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Mahindra_XUV700.jpg/800px-Mahindra_XUV700.jpg",
    "mahindra scorpio":      "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Mahindra_Scorpio.jpg/800px-Mahindra_Scorpio.jpg",
    "kia seltos":            "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Kia_Seltos.jpg/800px-Kia_Seltos.jpg",
    "maruti suzuki swift":   "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Maruti_Suzuki_Swift.jpg/800px-Maruti_Suzuki_Swift.jpg",
    "maruti jimny":          "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Maruti_Suzuki_Jimny.jpg/800px-Maruti_Suzuki_Jimny.jpg",
    "maruti grand vitara":   "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Maruti_Suzuki_Grand_Vitara.jpg/800px-Maruti_Suzuki_Grand_Vitara.jpg",
    "toyota innova":         "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Toyota_Innova_Crysta.jpg/800px-Toyota_Innova_Crysta.jpg",
    "honda city":            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Honda_City.jpg/800px-Honda_City.jpg",
    "honda elevate":         "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Honda_Elevate.jpg/800px-Honda_Elevate.jpg",
    "mg hector":             "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/MG_Hector.jpg/800px-MG_Hector.jpg",
    "mg zs ev":              "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/MG_ZS_EV.jpg/800px-MG_ZS_EV.jpg",
    "toyota fortuner":       "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Toyota_Fortuner.jpg/800px-Toyota_Fortuner.jpg",
}

# Keyword aliases → canonical key
KEYWORD_ALIASES: dict[str, str] = {
    "punch":          "tata punch",
    "nexon":          "tata nexon",
    "harrier":        "tata harrier",
    "safari":         "tata safari",
    "thar":           "mahindra thar",
    "xuv700":         "mahindra xuv700",
    "scorpio":        "mahindra scorpio",
    "creta":          "hyundai creta",
    "verna":          "hyundai verna",
    "i20":            "hyundai i20",
    "seltos":         "kia seltos",
    "swift":          "maruti suzuki swift",
    "jimny":          "maruti jimny",
    "grand vitara":   "maruti grand vitara",
    "innova":         "toyota innova",
    "fortuner":       "toyota fortuner",
    "elevate":        "honda elevate",
    "hector":         "mg hector",
    "zs ev":          "mg zs ev",
    "city":           "honda city",
    "370z":           "nissan 370z",
    "gt-r":           "nissan gt-r",
    "gtr":            "nissan gt-r",
    "supra":          "toyota gr supra",
    "gr86":           "toyota gr86",
    "type r":         "honda civic type r",
    "mx-5":           "mazda mx-5",
    "miata":          "mazda mx-5",
    "corvette":       "chevrolet corvette",
    "mustang":        "ford mustang",
    "challenger":     "dodge challenger",
    "hellcat":        "dodge challenger",
    "taycan":         "porsche taycan",
    "911":            "porsche 911 gt3",
    "m5":             "bmw m5",
    "m3":             "bmw m3",
    "i7":             "bmw i7",
    "rs e-tron":      "audi rs e-tron gt",
    "r8":             "audi r8",
    "eqs":            "mercedes eqs",
    "amg":            "mercedes amg gt",
    "sf90":           "ferrari sf90",
    "urus":           "lamborghini urus",
    "spectre":        "rolls-royce spectre",
    "cybertruck":     "tesla cybertruck",
    "model s":        "tesla model s plaid",
    "model 3":        "tesla model 3",
    "ioniq 6":        "hyundai ioniq 6",
    "ioniq 5":        "hyundai ioniq 5 n",
    "seal":           "byd seal",
    "atto":           "byd atto 3",
    "lucid":          "lucid air",
    "rivian":         "rivian r1t",
    "ev6":            "kia ev6 gt",
    "range rover":    "range rover",
    "rav4":           "toyota rav4 hybrid",
}

def _extract_car_names(prompt: str) -> list[str]:
    lower = prompt.lower()
    found: list[str] = []

    # Pass 1: exact keys
    for key in FALLBACK_IMAGE_MAP:
        pattern = r"\b" + re.escape(key) + r"\b"
        if re.search(pattern, lower) and key not in found:
            found.append(key)

    # Pass 2: aliases
    if not found:
        for kw, canonical in KEYWORD_ALIASES.items():
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, lower) and canonical not in found:
                found.append(canonical)

    return found[:4]   # Cap at 4 images

def _unsplash_url(query: str) -> str | None:
    if not UNSPLASH_KEY:
        return None
    try:
        r = requests.get(
            "https://api.unsplash.com/search/photos",
            params={"query": f"{query} car", "per_page": 1, "client_id": UNSPLASH_KEY},
            timeout=8,
        )
        if r.status_code == 200:
            results = r.json().get("results", [])
            if results:
                return results[0]["urls"]["regular"]
    except Exception:
        pass
    return None

def _image_url(key: str) -> str:
    url = _unsplash_url(key)
    if url:
        return url
    return FALLBACK_IMAGE_MAP.get(
        key,
        "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?auto=format&fit=crop&w=800&q=80"
    )

def show_car_images(keys: list[str]) -> None:
    if not keys:
        return
    cols = st.columns(min(4, len(keys)))
    for i, key in enumerate(keys):
        img = _image_url(key)
        with cols[i % 4]:
            st.markdown(f"""
            <div class="car-card">
                <img src="{img}" alt="{key}" loading="lazy">
                <div class="car-card-label"><span></span>{key.upper()}</div>
            </div>
            """, unsafe_allow_html=True)

# ==================================================
# 7. MAIN UI
# ==================================================
st.markdown("""
<div class="title-wrap">
    <div class="brand-eyebrow">⚡ Powered by AI · Est. 2025</div>
    <div class="elite-title">ELITEDRIVE AI</div>
    <div class="tagline">Your Premier Automotive Intelligence System</div>
</div>
<div class="divider"><span class="divider-icon">◆</span></div>
<div class="stats-bar">
    <div class="stat-item">
        <span class="stat-number">500+</span>
        <span class="stat-label">Car Models</span>
    </div>
    <div class="stat-item">
        <span class="stat-number">40+</span>
        <span class="stat-label">Brands Covered</span>
    </div>
    <div class="stat-item">
        <span class="stat-number">24/7</span>
        <span class="stat-label">Live Insights</span>
    </div>
    <div class="stat-item">
        <span class="stat-number">₹0</span>
        <span class="stat-label">Cost to Query</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Chat history ────────────────────────────────
if "car_messages" not in st.session_state:
    st.session_state.car_messages = []

for msg in st.session_state.car_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("role") == "assistant" and msg.get("user_car_keys"):
            show_car_images(msg["user_car_keys"])

# ── Input ───────────────────────────────────────
if prompt := st.chat_input("Ask about any car — specs, comparisons, or recommendations..."):
    user_car_keys = _extract_car_names(prompt)

    st.session_state.car_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Analysing premium vehicle data..."):
            answer = groq_car_chat(prompt, get_car_context())
            st.markdown(answer)
            if user_car_keys:
                show_car_images(user_car_keys)
            else:
                st.caption("_No specific model detected — ask about a car by name for images_")

        st.session_state.car_messages.append(
            {"role": "assistant", "content": answer, "user_car_keys": user_car_keys}
        )
