import streamlit as st
import requests

# 1. PAGE CONFIG
st.set_page_config(page_title="AI Car Consultant", page_icon="🚗")

# 2. SECRETS (Using the same Groq Key)
GROQ_KEY = st.secrets.get("GROQ_KEY", None)

if not GROQ_KEY:
    st.error("❌ Missing GROQ_KEY in Secrets!")
    st.stop()

# 3. CAR CONTEXT FUNCTION 
# (Simulating live market data for 2024-2025 models)
def get_car_context():
    return """
    Current Trending Cars (2024-2025):
    - Electric: Tesla Model 3 Highland, Hyundai Ioniq 6, BYD Seal.
    - SUVs: Toyota RAV4 Hybrid, Honda CR-V, Kia Sportage.
    - Luxury: BMW i7, Mercedes EQS, Audi e-tron GT.
    - Budget: Toyota Corolla, Honda Civic, Hyundai Elantra.
    Market Trend: Heavy shift towards Hybrids and EVs. Prices are stabilizing.
    """

# 4. GROQ API FUNCTION
def groq_car_chat(prompt, context):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system", 
                "content": "You are a professional Car Expert. You know everything about engine specs, mileage, EV range, and car comparisons. Be helpful and give pros/cons."
            },
            {
                "role": "user", 
                "content": f"CONTEXT: {context}\n\nUSER QUESTION: {prompt}"
            }
        ],
        "temperature": 0.7
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.text}"

# 5. UI SETUP
st.title("🚗 AI Car Consultant")
st.markdown("Ask me about specs, comparisons, or which car to buy!")

if "car_messages" not in st.session_state:
    st.session_state.car_messages = []

# Display Chat History
for msg in st.session_state.car_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("Ex: Should I buy a Tesla Model 3 or a BMW i4?"):
    st.session_state.car_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing car specs..."):
            context = get_car_context()
            answer = groq_car_chat(prompt, context)
            st.markdown(answer)
            st.session_state.car_messages.append({"role": "assistant", "content": answer})