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
   SIDEBAR STYLING - SEARCH ACTIVITY MENU
   ========================================= */
[data-testid="sidebarContent"] {
    background: rgba(20, 20, 20, 0.95) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(255, 107, 53, 0.3) !important;
}

.sidebar-menu-header {
    color: #ffffff;
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(255, 107, 53, 0.3);
    display: flex;
    align-items: center;
    gap: 10px;
}

.search-history-item {
    background: rgba(255, 255, 255, 0.08) !important;
    padding: 12px 15px !important;
    margin-bottom: 8px !important;
    border-radius: 12px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.search-history-item:hover {
    background: rgba(255, 107, 53, 0.2) !important;
    transform: translateX(5px) !important;
    border: 1px solid rgba(255, 107, 53, 0.4) !important;
}

.search-history-item .history-query {
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 200px;
}

.search-history-item .history-date {
    color: rgba(255, 107, 53, 0.8) !important;
    font-size: 0.8rem !important;
    margin-top: 4px !important;
}

.clear-history-btn {
    background: linear-gradient(135deg, #ff4757, #ff6b6b) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    margin-top: 20px !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
}

.clear-history-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(255, 71, 87, 0.4) !important;
}

.no-history-message {
    color: rgba(255, 255, 255, 0.5) !important;
    font-style: italic !important;
    text-align: center !important;
    padding: 20px !important;
    font-size: 0.9rem !important;
}

/* =========================================
   CHAT INPUT BOX STYLING
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

/* Stats Card */
.stats-card {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 107, 53, 0.2) !important;
    border-radius: 12px !important;
    padding: 15px !important;
    margin-top: 20px !important;
}

.stat-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px !important;
    color: rgba(255, 255, 255, 0.8) !important;
    font-size: 0.9rem !important;
}

.stat-value {
    color: #ff6b35 !important;
    font-weight: 700 !important;
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
# 3. INIT SESSION STATE FOR HISTORY
# ==================================================
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

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
    """
    Extract car names specifically from the user's prompt.
    This ensures we only show images for cars the user asked about.
    """
    lowered = prompt.lower()
    found = []
    
    # Check for exact matches with our known models
    for key in FALLBACK_IMAGE_MAP:
        # Use word boundaries to avoid partial matches
        # e.g., "punch" should match "tata punch" but not "punching"
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, lowered) and key not in found:
            found.append(key)
    
    # If no exact matches, try keyword matching for Indian cars
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
            # Use word boundaries for keywords too
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

# ==================================================
# 7. SIDEBAR - SEARCH ACTIVITY MENU
# ==================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-menu-header">
        <span>🔍</span> Search Activity
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.search_history:
        for idx, history_item in enumerate(reversed(st.session_state.search_history[-10:])):
            history_id = history_item["id"]
            query = history_item["query"][:50] + "..." if len(history_item["query"]) > 50 else history_item["query"]
            date = history_item["date"]
            
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(
                    f"""
                    <div class="search-history-item" onclick="location.reload()">
                        <div class="history-query">{query}</div>
                        <div class="history-date">{date}</div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
            # Add a small delete button for each history item
            if st.session_state.search_history[::-1].index(history_item) == idx and col2:
                if st.button("🗑️", key=f"delete_{idx}", help="Delete this search"):
                    st.session_state.search_history.remove(history_item)
                    st.rerun()
    else:
        st.markdown('<div class="no-history-message">No recent searches yet</div>', unsafe_allow_html=True)
    
    # Stats card
    total_searches = len(st.session_state.search_history)
    unique_cars = len(set().union(*[[item for item in h.get("cars", [])] for h in st.session_state.search_history])) if st.session_state.search_history else 0
    
    if total_searches > 0:
        st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="stats-card">
            <div class="stat-item">
                <span>Total Searches</span>
                <span class="stat-value">{total_searches}</span>
            </div>
            <div class="stat-item">
                <span>Cars Explored</span>
                <span class="stat-value">{unique_cars}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Clear History Button
    if total_searches > 0:
        if st.button("🗑️ Clear All History", key="clear_all_history", type="primary"):
            st.session_state.search_history = []
            st.session_state.car_messages = []
            st.rerun()

# ==================================================
# 8. MAIN UI
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
        # Only show images for cars that were in the USER'S original prompt
        if msg.get("role") == "assistant" and msg.get("user_car_keys"):
            show_car_images(msg["user_car_keys"])

# User input
if prompt := st.chat_input("Ask about any car - specs, comparisons, or recommendations..."):
    # Extract car names from the USER'S prompt
    user_car_keys = _extract_car_names_from_prompt(prompt)
    
    # Generate timestamp
    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    # Save to search history
    history_entry = {
        "id": datetime.now().timestamp(),
        "query": prompt,
        "date": current_time,
        "cars": user_car_keys
    }
    st.session_state.search_history.append(history_entry)
    
    st.session_state.car_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing premium vehicle data..."):
            context = get_car_context()
            answer = groq_car_chat(prompt, context)
            st.markdown(answer)
            
            # Show images ONLY for cars the user asked about
            if user_car_keys:
                show_car_images(user_car_keys)
            else:
                st.caption("_No specific car models detected in your question_")
            
            # Store the assistant response along with the user's car keys
            st.session_state.car_messages.append(
                {"role": "assistant", "content": answer, "user_car_keys": user_car_keys}
            )
    
    # Rerun to update sidebar
    st.rerun()
