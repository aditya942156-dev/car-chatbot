import streamlit as st
import requests
import re
from datetime import datetime

# ==================================================
# 1. PAGE CONFIG
# ==================================================
st.set_page_config(page_title="EliteDrive AI", page_icon="🏎️", layout="wide")

# Hide default streamlit hamburger completely
st.markdown("""
<style>
[data-testid="stSidebar"] {
    display: none;
}
[data-testid="stSidebarCollapseButton"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# 2. FULL UI STYLING
# ==================================================
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

/* Permanent Hamburger Menu Button */
.hamburger-btn {
    position: fixed;
    top: 18px;
    left: 18px;
    z-index: 9999;
    background: linear-gradient(135deg, #ff6b35, #f7931e);
    border: none;
    border-radius: 12px;
    padding: 10px 14px;
    color: white;
    font-size: 20px;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    transition: all 0.3s ease;
}

.hamburger-btn:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(255, 107, 53, 0.4);
}

/* EliteDrive Title */
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

/* Chat Input Box */
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
   SLIDE OUT SIDEBAR MENU
   ========================================= */
.sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: 320px;
    height: 100vh;
    background: rgba(12, 12, 12, 0.96);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255, 107, 53, 0.3);
    z-index: 9998;
    transform: translateX(-100%);
    transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    overflow-y: auto;
    padding: 70px 20px 30px 20px;
    box-shadow: 8px 0 40px rgba(0,0,0,0.6);
}

.sidebar.open {
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
    font-size: 1.4rem;
    font-weight: 700;
    color: white;
}

.close-btn {
    background: rgba(255, 107, 53, 0.2);
    border: 1px solid rgba(255, 107, 53, 0.4);
    color: #ff6b35;
    border-radius: 8px;
    padding: 4px 10px;
    cursor: pointer;
    font-weight: bold;
    font-size: 16px;
}

/* Search History Items */
.history-item {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 10px;
    transition: all 0.3s ease;
}

.history-item:hover {
    background: rgba(255, 107, 53, 0.1);
    border-color: rgba(255, 107, 53, 0.4);
    transform: translateX(5px);
}

.history-time {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.5);
    margin-bottom: 6px;
}

.history-query {
    font-size: 0.9rem;
    color: white;
    line-height: 1.3;
}

.history-cars {
    font-size: 0.8rem;
    color: #ff6b35;
    margin-top: 6px;
}

.clear-history-btn {
    background: rgba(255, 107, 53, 0.2);
    border: 1px solid rgba(255, 107, 53, 0.4);
    color: white;
    border-radius: 10px;
    padding: 12px;
    width: 100%;
    font-weight: 600;
    margin-top: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.clear-history-btn:hover {
    background: rgba(255, 107, 53, 0.3);
}

.empty-history {
    text-align: center;
    color: rgba(255,255,255,0.5);
    padding: 50px 10px;
}

/* Dark overlay when sidebar is open */
.overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.7);
    z-index: 9997;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s ease;
}

.overlay.open {
    opacity: 1;
    pointer-events: all;
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

/* Scrollbar */
.sidebar::-webkit-scrollbar {
    width: 5px;
}
.sidebar::-webkit-scrollbar-thumb {
    background: rgba(255, 107, 53, 0.5);
    border-radius: 3px;
}

</style>

<!-- Hamburger Button -->
<button class="hamburger-btn" onclick="toggleSidebar()">☰</button>

<!-- Overlay -->
<div class="overlay" id="overlay" onclick="toggleSidebar()"></div>

<!-- Sidebar Menu -->
<div class="sidebar" id="sidebar">
    <div class="sidebar-header">
        <div class="sidebar-title">📋 Search History</div>
        <button class="close-btn" onclick="toggleSidebar()">✕</button>
    </div>
    <div id="history-content">
    </div>
</div>

<script>
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
    document.getElementById('overlay').classList.toggle('open');
}
</script>
""", unsafe_allow_html=True)

# ==================================================
# 3. INIT SESSION STATE
# ==================================================
GROQ_KEY = st.secrets.get("GROQ_KEY", None)
UNSPLASH_KEY = st.secrets.get("UNSPLASH_KEY", None)

if not GROQ_KEY:
    st.error("❌ Missing GROQ_KEY in Secrets!")
    st.stop()

if "car_messages" not in st.session_state:
    st.session_state.car_messages = []
if "search_history" not in st.session_state:
    st.session_state.search_history = []

# ==================================================
# 4. CAR CONTEXT
# ==================================================
def get_car_context():
    return """
    Current Trending Cars (2024-2025):
    - Indian Market: Tata Punch, Mahindra Thar, Hyundai Creta, Kia Seltos, Maruti Swift
    - Electric: Tesla Model 3 Highland, Hyundai Ioniq 6, BYD Seal
    - SUVs: Toyota RAV4 Hybrid, Honda CR-V, Kia Sportage
    Market Trends: Hybrids are fastest growing segment in India.
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
                "You are EliteDrive AI - a professional car consultant. Give honest pros and cons, real world mileage and ownership advice."},
            {"role": "user", "content": f"CONTEXT: {context}\n\nUSER QUESTION: {prompt}"}
        ],
        "temperature": 0.7,
    }

    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"Error: {resp.text}"

# ==================================================
# 6. IMAGE AND CAR DETECTION
# ==================================================
FALLBACK_IMAGE_MAP = {
    "tata punch": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Tata_Punch.jpg/800px-Tata_Punch.jpg",
    "tata nexon": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Tata_Nexon_EV.jpg/800px-Tata_Nexon_EV.jpg",
    "mahindra thar": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Mahindra_Thar.jpg/800px-Mahindra_Thar.jpg",
    "mahindra xuv700": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Mahindra_XUV700.jpg/800px-Mahindra_XUV700.jpg",
    "hyundai creta": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Hyundai_Creta.jpg/800px-Hyundai_Creta.jpg",
    "kia seltos": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Kia_Seltos.jpg/800px-Kia_Seltos.jpg",
    "maruti swift": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Maruti_Suzuki_Swift.jpg/800px-Maruti_Suzuki_Swift.jpg",
}

def _extract_car_names_from_prompt(prompt: str):
    lowered = prompt.lower()
    found = []
    for key in FALLBACK_IMAGE_MAP:
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, lowered) and key not in found:
            found.append(key)

    indian_car_keywords = {
        "punch": "tata punch",
        "thar": "mahindra thar",
        "nexon": "tata nexon",
        "creta": "hyundai creta",
        "seltos": "kia seltos",
        "swift": "maruti swift",
    }

    for keyword, full_name in indian_car_keywords.items():
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, lowered) and full_name not in found:
            found.append(full_name)

    return found

def get_image_url_for_model(model_key: str) -> str:
    return FALLBACK_IMAGE_MAP.get(model_key,
                                 "https://via.placeholder.com/400x225?text=Car+Image")

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
# 7. RENDER SEARCH HISTORY INTO SIDEBAR
# ==================================================
def render_history():
    if not st.session_state.search_history:
        return """
        <div class="empty-history">
            <div style="font-size: 40px; margin-bottom: 10px;">🔍</div>
            No searches yet<br>
            <small>Ask about any car and it will appear here</small>
        </div>
        """

    html = ""
    for item in reversed(st.session_state.search_history):
        time_str = item['time'].strftime("%b %d, %I:%M %p")
        cars = ", ".join(item['cars'])
        html += f"""
        <div class="history-item">
            <div class="history-time">🕐 {time_str}</div>
            <div class="history-query">{item['query']}</div>
            {f'<div class="history-cars">🚗 {cars}</div>' if cars else ''}
        </div>
        """

    html += """
    <button class="clear-history-btn" onclick="if(confirm('Clear all history?')) window.location.reload()">
        🗑️ Clear All History
    </button>
    """
    return html

# Inject the history into the sidebar
st.markdown(f"""
<script>
document.getElementById('history-content').innerHTML = `{render_history()}`;
</script>
""", unsafe_allow_html=True)

# ==================================================
# 8. MAIN CHAT UI
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
        if msg.get("user_car_keys"):
            show_car_images(msg["user_car_keys"])

# User input
if prompt := st.chat_input("Ask about any car - specs, comparisons, recommendations..."):
    user_car_keys = _extract_car_names_from_prompt(prompt)

    # Save to search history
    st.session_state.search_history.append({
        "query": prompt,
        "time": datetime.now(),
        "cars": user_car_keys
    })

    st.session_state.car_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing car specs…"):
            context = get_car_context()
            answer = groq_car_chat(prompt, context)
            st.markdown(answer)

            if user_car_keys:
                show_car_images(user_car_keys)

            st.session_state.car_messages.append(
                {"role": "assistant", "content": answer, "user_car_keys": user_car_keys}
            )

    st.rerun()
