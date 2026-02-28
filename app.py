import streamlit as st
import requests
import re
from urllib.parse import quote
from datetime import datetime

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

/* Chat Message Bubbles */
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

/* =========================================
   PREMIUM CHAT INPUT BOX STYLING
   ========================================= */
[data-testid="stChatInput"] {
    background-color: rgba(15, 15, 15, 0.85) !important;
    backdrop-filter: blur(15px) !important;
    border: 1px solid rgba(255, 107, 53, 0.3) !important;
    border-radius: 20px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5) !important;
    padding: 2px !important;
    transition: all 0.3s ease-in-out !important;
}

[data-testid="stChatInput"]:focus-within {
    border: 1px solid #ff6b35 !important;
    box-shadow: 0 0 20px rgba(255, 107, 53, 0.4), 0 8px 32px rgba(0,0,0,0.6) !important;
    transform: translateY(-2px);
}

[data-testid="stChatInputTextArea"] {
    color: #ffffff !important;
    font-size: 1.05rem !important;
}

[data-testid="stChatInputSubmitButton"] {
    background: linear-gradient(135deg, #ff6b35, #f7931e) !important;
    border-radius: 50% !important;
    color: white !important;
    border: none !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}

[data-testid="stChatInputSubmitButton"]:hover {
    transform: scale(1.15) !important;
    box-shadow: 0 0 15px rgba(255, 107, 53, 0.6) !important;
}

/* =========================================
   LEFT SIDEBAR STYLING
   ========================================= */
/* Hamburger Menu Button */
.hamburger-menu {
    position: fixed;
    top: 20px;
    left: 20px;
    z-index: 1000;
    background: linear-gradient(135deg, rgba(255, 107, 53, 0.9), rgba(247, 147, 30, 0.9));
    border: none;
    border-radius: 12px;
    padding: 12px 16px;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    transition: all 0.3s ease;
}

.hamburger-menu:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(255, 107, 53, 0.4);
}

.hamburger-icon {
    font-size: 24px;
    color: white;
    font-weight: bold;
}

/* Sidebar Container */
.sidebar-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 320px;
    height: 100vh;
    background: rgba(15, 15, 15, 0.95);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255, 107, 53, 0.3);
    z-index: 999;
    transform: translateX(-100%);
    transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    overflow-y: auto;
    padding: 80px 20px 20px 20px;
    box-shadow: 5px 0 30px rgba(0,0,0,0.5);
}

.sidebar-container.open {
    transform: translateX(0);
}

.sidebar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
    padding-bottom: 15px;
    border-bottom: 1px solid rgba(255, 107, 53, 0.3);
}

.sidebar-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff;
    text-shadow: 0 2px 4px rgba(0,0,0,0.5);
}

.close-btn {
    background: rgba(255, 107, 53, 0.2);
    border: 1px solid rgba(255, 107, 53, 0.3);
    color: #ff6b35;
    border-radius: 8px;
    padding: 6px 12px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
}

.close-btn:hover {
    background: rgba(255, 107, 53, 0.3);
    transform: scale(1.05);
}

/* Search Activity Items */
.search-item {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 12px;
    transition: all 0.3s ease;
    cursor: pointer;
}

.search-item:hover {
    background: rgba(255, 107, 53, 0.1);
    border-color: rgba(255, 107, 53, 0.4);
    transform: translateX(5px);
}

.search-time {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.5);
    margin-bottom: 5px;
}

.search-query {
    font-size: 0.95rem;
    color: #ffffff;
    font-weight: 500;
    line-height: 1.4;
}

.search-cars {
    font-size: 0.8rem;
    color: rgba(255, 107, 53, 0.8);
    margin-top: 8px;
    font-style: italic;
}

/* Clear History Button */
.clear-history {
    background: rgba(255, 107, 53, 0.2);
    border: 1px solid rgba(255, 107, 53, 0.4);
    color: #ffffff;
    border-radius: 10px;
    padding: 12px 20px;
    width: 100%;
    font-weight: 600;
    cursor: pointer;
    margin-top: 20px;
    transition: all 0.3s ease;
}

.clear-history:hover {
    background: rgba(255, 107, 53, 0.3);
    box-shadow: 0 0 15px rgba(255, 107, 53, 0.3);
}

/* Overlay Background */
.overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    z-index: 998;
    display: none;
}

.overlay.active {
    display: block;
}

/* Empty State */
.empty-state {
    text-align: center;
    color: rgba(255, 255, 255, 0.5);
    padding: 40px 20px;
}

.empty-icon {
    font-size: 3rem;
    margin-bottom: 15px;
}

/* Scrollbar Styling */
.sidebar-container::-webkit-scrollbar {
    width: 6px;
}

.sidebar-container::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
}

.sidebar-container::-webkit-scrollbar-thumb {
    background: rgba(255, 107, 53, 0.5);
    border-radius: 3px;
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
# 3. INIT SESSION STATE
# ==================================================
if "car_messages" not in st.session_state:
    st.session_state.car_messages = []

if "search_history" not in st.session_state:
    st.session_state.search_history = []

if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = False

# ==================================================
# 4. CAR CONTEXT
# ==================================================
def get_car_context():
    return """
    Current Trending Cars (2024-2025):
    - Electric: Tesla Model 3 Highland, Hyundai Ioniq 6, BYD Seal, Lucid Air
    - Performance: Porsche Taycan, BMW M5, Audi RS e-tron GT
    - Luxury: Mercedes-Maybach EQS, Rolls-Royce Spectre, Bentley Bentayga
    - SUVs: Range Rover Sport, Lexus RX, Volvo EX90
    - Budget: Toyota Corolla Hybrid, Honda Civic, Hyundai Kona Electric
    - Indian Market: Tata Punch, Mahindra Thar, Hyundai Creta, Kia Seltos, Maruti Suzuki Swift
    Market Trends: 40% EV adoption in premium segments, 25% price premium for performance EVs
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
            {"role": "system", "content":
                "You are EliteDrive AI - a premium car consultant with expertise in luxury, performance, and electric vehicles. "
                "Provide detailed comparisons, technical specifications, and market insights with a sophisticated tone. "
                "Always include pros/cons, real-world range estimates for EVs, and ownership cost analysis."},
            {"role": "user", "content": f"CONTEXT: {context}\n\nUSER QUESTION: {prompt}"}
        ],
        "temperature": 0.7,
    }

    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"Error: {resp.text}"

# ==================================================
# 6. IMAGE HANDLING - ENHANCED WITH INDIAN CARS
# ==================================================
FALLBACK_IMAGE_MAP = {
    # International models
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
    "porsche taycan": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/2021_Porsche_Taycan_4S.jpg/800px-2021_Porsche_Taycan_4S.jpg",
    "lucid air": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Lucid_Air_Dream_Edition.jpg/800px-Lucid_Air_Dream_Edition.jpg",
    "rolls-royce spectre": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Rolls-Royce_Spectre_2023.jpg/800px-Rolls-Royce_Spectre_2023.jpg",
    "range rover sport": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/2022_Range_Rover_Sport_Autobiography.jpg/800px-2022_Range_Rover_Sport_Autobiography.jpg",
    "lexus rx": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/2023_Lexus_RX_350h_F_Sport.jpg/800px-2023_Lexus_RX_350h_F_Sport.jpg",
    "volvo ex90": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Volvo_EX90_2024.jpg/800px-Volvo_EX90_2024.jpg",
    
    # Indian car models
    "tata punch": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Tata_Punch.jpg/800px-Tata_Punch.jpg",
    "tata nexon": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Tata_Nexon_EV.jpg/800px-Tata_Nexon_EV.jpg",
    "tata harrier": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Tata_Harrier.jpg/800px-Tata_Harrier.jpg",
    "tata safari": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Tata_Safari.jpg/800px-Tata_Safari.jpg",
    "mahindra thar": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Mahindra_Thar.jpg/800px-Mahindra_Thar.jpg",
    "mahindra scorpio": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Mahindra_Scorpio.jpg/800px-Mahindra_Scorpio.jpg",
    "mahindra xuv700": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Mahindra_XUV700.jpg/800px-Mahindra_XUV700.jpg",
    "hyundai creta": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Hyundai_Creta.jpg/800px-Hyundai_Creta.jpg",
    "kia seltos": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Kia_Seltos.jpg/800px-Kia_Seltos.jpg",
    "maruti suzuki swift": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Maruti_Suzuki_Swift.jpg/800px-Maruti_Suzuki_Swift.jpg",
    "maruti suzuki baleno": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Maruti_Suzuki_Baleno.jpg/800px-Maruti_Suzuki_Baleno.jpg",
    "maruti suzuki grand vitara": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Maruti_Suzuki_Grand_Vitara.jpg/800px-Maruti_Suzuki_Grand_Vitara.jpg",
    "toyota innova crysta": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Toyota_Innova_Crysta.jpg/800px-Toyota_Innova_Crysta.jpg",
    "honda city": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Honda_City.jpg/800px-Honda_City.jpg",
    "hyundai verna": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Hyundai_Verna.jpg/800px-Hyundai_Verna.jpg",
    "hyundai i20": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Hyundai_i20.jpg/800px-Hyundai_i20.jpg",
}

def _extract_car_names_from_prompt(prompt: str):
    lowered = prompt.lower()
    found = []
    
    for key in FALLBACK_IMAGE_MAP:
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, lowered) and key not in found:
            found.append(key)
    
    if not found:
        indian_car_keywords = {
            "punch": "tata punch",
            "nexon": "tata nexon",
            "harrier": "tata harrier",
            "safari": "tata safari",
            "thar": "mahindra thar",
            "scorpio": "mahindra scorpio",
            "xuv700": "mahindra xuv700",
            "creta": "hyundai creta",
            "seltos": "kia seltos",
            "swift": "maruti suzuki swift",
            "baleno": "maruti suzuki baleno",
            "grand vitara": "maruti suzuki grand vitara",
            "innova crysta": "toyota innova crysta",
            "city": "honda city",
            "verna": "hyundai verna",
            "i20": "hyundai i20",
        }
        
        for keyword, full_name in indian_car_keywords.items():
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, lowered) and full_name not in found:
                found.append(full_name)
    
    return found

def get_unsplash_image_url(query: str) -> str | None:
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
    unsplash_url = get_unsplash_image_url(model_key)
    if unsplash_url:
        return unsplash_url
    return FALLBACK_IMAGE_MAP.get(model_key,
                                 "https://via.placeholder.com/400x225?text=Premium+Car+Image")

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

def format_time(dt):
    """Format datetime to readable string"""
    return dt.strftime("%b %d, %I:%M %p")

# ==================================================
# 7. SIDEBAR HTML/CSS IMPLEMENTATION
# ==================================================
# Toggle sidebar
if st.sidebar.button("☰ Menu", key="toggle_sidebar"):
    st.session_state.sidebar_open = not st.session_state.sidebar_open

# Render sidebar HTML
sidebar_html = f"""
<div class="overlay {'active' if st.session_state.sidebar_open else ''}" 
     onclick="document.querySelector('.sidebar-container').classList.remove('open'); 
              document.querySelector('.overlay').classList.remove('active');"></div>

<div class="sidebar-container {'open' if st.session_state.sidebar_open else ''}" id="sidebarMenu">
    <div class="sidebar-header">
        <div class="sidebar-title">🏎️ Activity History</div>
        <button class="close-btn" onclick="this.closest('.sidebar-container').classList.remove('open'); 
                                           this.parentElement.parentElement.parentElement.classList.remove('active');">×</button>
    </div>
    
    <div class="sidebar-content">
        {generate_search_history_html()}
    </div>
</div>
"""

def generate_search_history_html():
    if not st.session_state.search_history:
        return """
        <div class="empty-state">
            <div class="empty-icon">🔍</div>
            <div>No searches yet</div>
            <div style="font-size: 0.85rem; margin-top: 10px;">Ask about any car to see it here</div>
        </div>
        """
    
    html = ""
    for item in reversed(st.session_state.search_history):
        cars_str = ", ".join(item.get('detected_cars', []))[:50] + ("..." if len(", ".join(item.get('detected_cars', []))) > 50 else "")
        html += f"""
        <div class="search-item" title="{item['query']}">
            <div class="search-time">🕐 {format_time(item['timestamp'])}</div>
            <div class="search-query">{item['query']}</div>
            {f"<div class='search-cars'>🚗 Found: {cars_str}</div>" if item.get('detected_cars') else ""}
        </div>
        """
    
    html += """
    <button class="clear-history" onclick="if(confirm('Clear all search history?')) window.location.reload();">
        🗑️ Clear All History
    </button>
    """
    return html

# Inject sidebar into the page
with st.sidebar:
    st.write("")  # Spacer to hide default sidebar
st.markdown(sidebar_html, unsafe_allow_html=True)

# ==================================================
# 8. MAIN UI
# ==================================================
st.markdown("""
<div class="title-container">
    <div class="elite-title">ELITEDRIVE AI</div>
    <div class="tagline">Your Premium Car Consultant</div>
</div>
""", unsafe_allow_html=True)

# Render chat history
for msg in st.session_state.car_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("role") == "assistant" and msg.get("user_car_keys"):
            show_car_images(msg["user_car_keys"])

# User input
if prompt := st.chat_input("Ask about any car - specs, comparisons, or recommendations..."):
    # Extract car names from the USER'S prompt
    user_car_keys = _extract_car_names_from_prompt(prompt)
    
    # Save to search history
    st.session_state.search_history.append({
        "query": prompt,
        "timestamp": datetime.now(),
        "detected_cars": user_car_keys
    })
    
    st.session_state.car_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing premium vehicle data..."):
            context = get_car_context()
            answer = groq_car_chat(prompt, context)
            st.markdown(answer)
            
            if user_car_keys:
                show_car_images(user_car_keys)
            else:
                st.caption("_No specific car models detected in your question_")
            
            st.session_state.car_messages.append(
                {"role": "assistant", "content": answer, "user_car_keys": user_car_keys}
            )

# Add JavaScript to handle sidebar toggle properly
st.markdown("""
<script>
// Handle hamburger menu click
const toggleBtn = document.querySelector('[data-testid="stSidebarButton"]');
if (toggleBtn) {
    toggleBtn.addEventListener('click', function(e) {
        e.preventDefault();
        const sidebar = document.getElementById('sidebarMenu');
        const overlay = document.querySelector('.overlay');
        if (sidebar) {
            sidebar.classList.toggle('open');
        }
        if (overlay) {
            overlay.classList.toggle('active');
        }
    });
}

// Close sidebar when clicking outside
document.addEventListener('click', function(e) {
    const sidebar = document.getElementById('sidebarMenu');
    const overlay = document.querySelector('.overlay');
    const toggleBtn = document.querySelector('[data-testid="stSidebarButton"]');
    
    if (sidebar && overlay && !sidebar.contains(e.target) && !toggleBtn.contains(e.target) && overlay.style.display !== 'none') {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
    }
});
</script>
""", unsafe_allow_html=True)
