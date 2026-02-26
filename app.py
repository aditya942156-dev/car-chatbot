#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Professional AI Car Consultant – with the exact background CSS you supplied.
Features:
  • Full‑screen car background (mobile + desktop friendly)
  • Groq LLM (llama‑3.1‑8b‑instant or mixtral‑8x7b‑32768) with optional streaming
  • Automatic car‑name detection → Unsplash image lookup (cached) → static fallback
  • Sidebar controls for model, temperature, max images, streaming
  • Polished chat bubbles, input box and sidebar styling
  • Chat history (text + images) persists across reruns
"""

# -------------------------------------------------
# 0. IMPORTS
# -------------------------------------------------
import base64
import json
import re
from typing import List, Optional, Tuple

import requests
import streamlit as st

# -------------------------------------------------
# 1. PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="🚗 AI Car Consultant",
    page_icon="🚗",
    layout="wide",                 # gives the background room to stretch
    initial_sidebar_state="expanded",
)

# -------------------------------------------------
# 2. FIXED BACKGROUND CSS – PERFECT FIT ON MOBILE + DESKTOP
# -------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), 
                    url("https://www.pexels.com/photo/photography-of-gray-sports-car-919073/");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        color: white !important;
    }
    h1, h2, h3, p, li {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# 3. LOAD SECRETS
# -------------------------------------------------
GROQ_KEY = st.secrets.get("GROQ_KEY")
UNSPLASH_KEY = st.secrets.get("UNSPLASH_KEY")   # optional – if missing we fall back to static images

if not GROQ_KEY:
    st.error("❌ Missing GROQ_KEY in Secrets!")
    st.stop()

# -------------------------------------------------
# 4. STATIC DATA (car makes, fallback images, market context)
# -------------------------------------------------
KNOWN_MAKES = {
    "tesla", "toyota", "honda", "hyundai", "kia", "bmw",
    "mercedes-benz", "mercedes", "audi", "ford", "chevrolet",
    "nissan", "volkswagen", "volvo", "subaru", "mazda",
    "porsche", "lexus", "jaguar", "land rover", "rivian",
    "lucid", "polestar", "bmw i", "mercedes eq", "audi e-tron"
}

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

# -------------------------------------------------
# 5. HELPERS – MARKET CONTEXT (cached)
# -------------------------------------------------
@st.cache_data(ttl=60 * 60)  # refresh once an hour
def get_car_context() -> str:
    """Simulated live market data – cached so we don’t rebuild on each rerun."""
    return """
    Current Trending Cars (2024‑2025):
    - Electric: Tesla Model 3 Highland, Hyundai Ioniq 6, BYD Seal.
    - SUVs: Toyota RAV4 Hybrid, Honda CR-V, Kia Sportage.
    - Luxury: BMW i7, Mercedes EQS, Audi e-tron GT.
    - Budget: Toyota Corolla, Honda Civic, Hyundai Elantra.
    Market Trend: Heavy shift towards Hybrids and EVs. Prices are stabilizing.
    """

# -------------------------------------------------
# 6. GROQ API CALL (with optional streaming & retry)
# -------------------------------------------------
def groq_car_chat(
    prompt: str,
    context: str,
    *,
    model: str = "llama-3.1-8b-instant",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    max_retries: int = 2,
) -> str:
    """
    Calls Groq's chat completion endpoint.
    If `stream=True` the function returns a generator yielding text chunks.
    On failure it returns a user‑friendly error string.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content":
                "You are a professional Car Expert. You know everything about engine specs, mileage, EV range, and car comparisons. "
                "Be helpful and give pros/cons."},
            {"role": "user", "content": f"CONTEXT: {context}\n\nUSER QUESTION: {prompt}"}
        ],
        "temperature": temperature,
        **({"max_tokens": max_tokens} if max_tokens is not None else {}),
        "stream": stream,
    }

    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                if stream:
                    # Return a generator that yields decoded chunks
                    def _stream():
                        for line in resp.iter_lines():
                            if line:
                                decoded = line.decode("utf-8")
                                if decoded.startswith("data:"):
                                    data = decoded[5:].strip()
                                    if data == "[DONE]":
                                        break
                                    try:
                                        chunk = json.loads(data)
                                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                                        content = delta.get("content")
                                        if content:
                                            yield content
                                    except json.JSONDecodeError:
                                        continue
                    return _stream()
                else:
                    return resp.json()["choices"][0]["message"]["content"]
            err_msg = f"Groq API error {resp.status_code}: {resp.text}"
        except requests.RequestException as exc:
            err_msg = f"Network error while calling Groq: {exc}"

        if attempt < max_retries:
            st.toast(f"⚠️ {err_msg} – retrying…", icon="🔁")
            import time
            time.sleep(1.5 ** attempt)   # simple exponential back‑off
        else:
            # final attempt failed → friendly message
            return (
                "🤖 Sorry, I couldn’t reach the car‑expert service right now. Please try again later.\n\n"
                f"*Technical detail:* {err_msg}"
            )
    return "🤖 Unexpected error while contacting the assistant."

# -------------------------------------------------
# 7. IMAGE HELPERS
# -------------------------------------------------
@st.cache_data(show_spinner=False, ttl=60 * 60)  # cache for an hour
def get_unsplash_image_url(query: str) -> Optional[str]:
    """Query Unsplash and return the `regular` size URL of the first result."""
    if not UNSPLASH_KEY:
        return None
    url = "https://api.unsplash.com/search/photos"
    params = {"query": query, "per_page": 1, "client_id": UNSPLASH_KEY}
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
    """Try Unsplash first; fall back to static map; finally a placeholder."""
    unsplash_url = get_unsplash_image_url(f"{model_key} car")
    if unsplash_url:
        return unsplash_url
    return FALLBACK_IMAGE_MAP.get(
        model_key,
        "https://via.placeholder.com/400x225?text=No+Image+Available"
    )


def _extract_car_names(text: str) -> List[str]:
    """
    Very lightweight NER:
      - Find any known make (case‑insensitive)
      - Grab the next 1‑2 words (heuristic for model).
    Returns a de‑duplicated, lower‑cased list.
    """
    lowered = text.lower()
    found = set()

    pattern = re.compile(
        rf"\b({'|'.join(KNOWN_MAKES)})\b[\s\-]*[a-z0-9]+(?:\s+[a-z0-9\-]+){0,2}"
    )
    for m in pattern.finditer(lowered):
        cand = m.group(0).strip()
        cand = re.sub(r"[\s\-]+", " ", cand)
        found.add(cand)

    # Also check the fallback map – catches models we explicitly listed
    for key in FALLBACK_IMAGE_MAP:
        if key in lowered:
            found.add(key)

    return sorted(found)


def show_car_images(model_keys: List[str], max_imgs: int = 6) -> None:
    """Render images in a responsive grid (de‑duplicated & limited)."""
    if not model_keys:
        return
    keys = list(dict.fromkeys(model_keys))[:max_imgs]   # preserve order, deduplicate

    cols_count = 3
    cols = st.columns(cols_count)
    for idx, key in enumerate(keys):
        img_url = get_image_url_for_model(key)
        with cols[idx % cols_count]:
            st.image(img_url, caption=key.title(), use_column_width=True)

# -------------------------------------------------
# 8. SIDEBAR – USER CONTROLS
# -------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    model_choice = st.selectbox(
        "Groq model",
        options=["llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        index=0,
        help="Larger models are slower but may be more knowledgeable."
    )
    temperature = st.slider(
        "Creativity (temperature)",
        min_value=0.0,
        max_value=1.5,
        value=0.7,
        step=0.1,
        help="Higher → more random/diverse answers."
    )
    max_images = st.slider(
        "Max images to show per answer",
        min_value=0,
        max_value=10,
        value=4,
        step=1,
        help="Set to 0 to suppress image lookup entirely."
    )
    use_streaming = st.checkbox(
        "Stream assistant response",
        value=True,
        help="Shows the answer token‑by‑token (ChatGPT‑style)."
    )
    st.divider()
    st.caption(
        "Tip: Add more makes to `KNOWN_MAKES` or extend `FALLBACK_IMAGE_MAP` if you need better offline coverage."
    )

# -------------------------------------------------
# 9. UI – TITLE & CHAT HISTORY
# -------------------------------------------------
st.title("🚗 AI Car Consultant")
st.markdown("Ask me about specs, comparisons, or which car to buy!")

if "car_messages" not in st.session_state:
    st.session_state.car_messages = []   # each entry: dict(role, content, image_keys?)

# Render past turns
for msg in st.session_state.car_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("role") == "assistant" and msg.get("image_keys"):
            show_car_images(msg["image_keys"], max_imgs=st.session_state.get("max_images", 4))

# -------------------------------------------------
# 10. CHAT INPUT & LOGIC
# -------------------------------------------------
if prompt := st.chat_input("Example: Should I buy a Tesla Model 3 or a BMW i4?"):
    # ---- USER TURN ----
    st.session_state.car_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ---- ASSISTANT TURN ----
    with st.chat_message("assistant"):
        context = get_car_context()

        if use_streaming:
            # Stream into an empty container and collect the full text for storage
            response_placeholder = st.empty()
            collected: List[str] = []

            stream_gen = groq_car_chat(
                prompt,
                context,
                model=model_choice,
                temperature=temperature,
                stream=True,
            )
            for chunk in stream_gen:          # type: ignore[arg-type]
                collected.append(chunk)
                response_placeholder.markdown("".join(collected) + "▌")
            final_answer = "".join(collected)
            response_placeholder.markdown(final_answer)
        else:
            with st.spinner("Analyzing car specs…"):
                final_answer = groq_car_chat(
                    prompt,
                    context,
                    model=model_choice,
                    temperature=temperature,
                    stream=False,
                )
                st.markdown(final_answer)

        # ---- IMAGE LOGIC ----
        car_keys = _extract_car_names(final_answer)
        if car_keys and st.session_state.get("max_images", 0) > 0:
            show_car_images(car_keys, max_imgs=st.session_state.get("max_images", 4))
        elif not car_keys:
            st.caption(
                "_No recognisable car model detected – you can extend the detection list or add more fallback images._"
            )

        # ---- SAVE ASSISTANT TURN ----
        st.session_state.car_messages.append(
            {
                "role": "assistant",
                "content": final_answer,
                "image_keys": car_keys if car_keys else [],
            }
        )

# -------------------------------------------------
# 11. FOOTER (optional)
# -------------------------------------------------
st.divider()
st.caption(
    "Built with Streamlit • Groq • Unsplash • 🚗  "
    "Feel free to fork and customise!"
)
