#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Streamlit snippet: set a suitable car‑themed background for your app.
Run with:  streamlit run app_bg.py
"""

import base64
import streamlit as st
import requests   # only needed for fetching a remote image; harmless if you use a local file

# ----------------------------------------------------------------------
# 1️⃣ PAGE CONFIG (keep it – it enables the wide layout we need)
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="🚗 AI Car Consultant – Background Demo",
    page_icon="🚗",
    layout="wide",                # gives the background room to stretch
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------
# 2️⃣ BACKGROUND SETTINGS
# ----------------------------------------------------------------------
# Choose **ONE** of the two ways to supply the image:
#
#   A) Public URL – e.g. an Unsplash photo, your own hosted picture, etc.
#   B) Local file – drop an image (e.g. assets/bg.jpg) next to this script.
#
# ----------------------------------------------------------------------
# ──────────────────────────────── Option A: Public URL ────────────────────────────────
BACKGROUND_URL = (
    "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb"
    "?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwyNzY1Nzl8MHwxfHJhbmRvbXx8fHx8fHx8fDE2OTk5NzYwNDg"
    "&ixlib=rb-4.0.3&q=80&w=2000"
)   # Replace with any direct image link you like.
# ──────────────────────────────── Option B: Local file ────────────────────────────────
# UNCOMMENT the next line and put your image (e.g. assets/bg.jpg) in the same folder.
# BACKGROUND_PATH = "assets/bg.jpg"
# ----------------------------------------------------------------------
# Styling knobs – adjust to taste
BACKGROUND_OPACITY = 0.35               # 0 = no overlay, 1 = completely black overlay
BACKGROUND_GRADIENT = "to bottom"
BACKGROUND_GRADIENT_COLORS = ("#0f172a", "#1e293b")   # dark‑blue‑gray gradient (feel free to change)

# ----------------------------------------------------------------------
# 3️⃣ HELPER: turn an image URL (or local file) into a Base64 string
# ----------------------------------------------------------------------
def _img_to_base64(url: str) -> str:
    """Download an image from a URL and return a base64‑encoded string."""
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return base64.b64encode(r.content).decode()
    except Exception as exc:
        st.warning(f"⚠️ Could not fetch background image: {exc}")
        return ""


def set_background(
    img_url: str,
    *,
    opacity: float = BACKGROUND_OPACITY,
    gradient: str = BACKGROUND_GRADIENT,
    gradient_colors: Tuple[str, str] = BACKGROUND_GRADIENT_COLORS,
) -> None:
    """
    Inject CSS that:
      • puts `img_url` as the page background,
      • adds a dark gradient overlay for readability,
      • gives the main container a frosted‑glass look,
      • styles chat bubbles, input box & sidebar.
    """
    b64 = _img_to_base64(img_url)
    if not b64:                               # fallback to a solid colour if we can't load the image
        bg_css = f"background: {gradient_colors[0]};"
    else:
        bg_css = (
            f"background: url('data:image/jpeg;base64,{b64}');"
            f"background-size: cover;"
            f"background-position: center;"
            f"background-attachment: fixed;"
        )

    # Convert hex colours to RGB for the rgba() notation used in the gradient overlay
    def hex_to_rgb(h: str) -> Tuple[int, int, int]:
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    r1, g1, b1 = hex_to_rgb(gradient_colors[0])
    r2, g2, b2 = hex_to_rgb(gradient_colors[1])
    overlay_css = (
        f"background: linear-gradient({gradient}, "
        f"rgba({r1},{g1},{b1},{opacity}), "
        f"rgba({r2},{g2},{b2},{min(opacity+0.15, 1.0)});"
    )

    # ------------------------------------------------------------------
    # Final CSS block – inject it once with st.markdown(..., unsafe_allow_html=True)
    # ------------------------------------------------------------------
    css = f"""
    <style>
        /* ---- PAGE BACKGROUND ---- */
        .stApp {{
            {bg_css}
            {overlay_css}
            color: #f8fafc;               /* light text for contrast */
            font-family: 'Inter', sans-serif;
        }}

        /* ---- Main content container (frosted‑glass feel) ---- */
        .block-container {{
            background: rgba(0,0,0,0.35);
            border-radius: 12px;
            padding: 2rem;
            backdrop-filter: blur(4px);
        }}

        /* ---- CHAT BUBBLES (you can keep or delete if you don't use chat) ---- */
        .stChatMessage {{
            border-radius: 16px;
            padding: 0.9rem 1.2rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .stChatMessage[data-testid="stChatMessage-user"] {{
            background: rgba(30, 64, 175, 0.18);   /* soft blue */
            border-left: 4px solid #1e40af;
        }}
        .stChatMessage[data-testid="stChatMessage-assistant"] {{
            background: rgba(34, 197, 94, 0.15);   /* soft green */
            border-left: 4px solid #16a34a;
        }}

        /* ---- INPUT BOX ---- */
        .stTextInput > div > div > input {{
            background: rgba(255,255,255,0.08);
            color: #f8fafc;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
        }}
        .stTextInput > div > div > input:focus {{
            box-shadow: 0 0 0 2px rgba(30,64,175,0.4);
        }}

        /* ---- SIDEBAR (optional) ---- */
        [data-testid="stSidebar"] {{
            background: rgba(0,0,0,0.4);
            backdrop-filter: blur(6px);
        }}
        [data-testid="stSidebar"] .stSelectbox,
        [data-testid="stSidebar"] .stSlider,
        [data-testid="stSidebar"] .stCheckbox {{
            color: #e2e8f0;
        }}

        /* ---- Headings ---- */
        h1, h2, h3 {{
            color: #f1f5f9;
            text-shadow: 0 1px 2px rgba(0,0,0,0.4);
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ----------------------------------------------------------------------
# 4️⃣ APPLY THE BACKGROUND (choose source)
# ----------------------------------------------------------------------
if "BACKGROUND_URL" in globals() and BACKGROUND_URL:
    set_background(BACKGROUND_URL)                     # uses the public URL above
elif "BACKGROUND_PATH" in globals():
    # Local file – read & base64‑encode it
    try:
        with open(BACKGROUND_PATH, "rb") as f:
            local_b64 = base64.b64encode(f.read()).decode()
        set_background(f"data:image/jpeg;base64,{local_b64}")
    except Exception as e:
        st.error(f"❌ Could not load local background image: {e}")
        st.stop()
else:
    st.error("❌ No background image source defined. Set BACKGROUND_URL or BACKGROUND_PATH.")
    st.stop()


# ----------------------------------------------------------------------
# 5️⃣ DEMO CONTENT (you can replace this with your actual car‑chatbot logic)
# ----------------------------------------------------------------------
st.title("🚗 AI Car Consultant – Background Demo")
st.write(
    """
    This is a minimal Streamlit app that shows how to set a **car‑themed background**.  
    Replace the demo text below with your own chatbot UI (chat_input, messages, etc.).
    """
)

# Example of a simple chat‑like interaction (optional, just to see the styled bubbles)
if "history" not in st.session_state:
    st.session_state.history = []

user_msg = st.text_input("Ask me about a car …", placeholder="e.g. Tell me about the Tesla Model 3")
if st.button("Send") and user_msg.strip():
    # Dummy reply – replace with your LLM call
    bot_reply = f"You asked: *{user_msg}*. Here's a quick car fact: Electric vehicles are gaining market share fast!"
    st.session_state.history.append(("user", user_msg))
    st.session_state.history.append(("assistant", bot_reply))

# Render the chat history with the same bubble styling Streamlit provides
for role, msg in st.session_state.history:
    with st.chat_message(role):
        st.markdown(msg)

# ----------------------------------------------------------------------
# 6️⃣ FOOTER (optional)
# ----------------------------------------------------------------------
st.divider()
st.caption(
    "Background image sourced from Unsplash (replace with your own). "
    "Feel free to tweak colours, opacity, gradient, etc. to match your brand."
)
