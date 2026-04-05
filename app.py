import streamlit as st
import requests
import re
import base64
import io

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(page_title="EliteDrive AI", page_icon="🏎️", layout="wide")

# ==================================================
# SECRETS
# ==================================================
GROQ_KEY = st.secrets.get("GROQ_KEY", None)

if not GROQ_KEY:
    st.error("❌ Missing GROQ_KEY in Secrets!")
    st.stop()

# ==================================================
# CSS STYLING
# ==================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;400;500;600;700&family=Orbitron:wght@400;700;900&display=swap');

.stApp {
    background: linear-gradient(135deg, #0a0a0a 0%, #0f0500 50%, #0a0a0a 100%);
    min-height: 100vh;
    font-family: 'Rajdhani', sans-serif;
}
.title-container { text-align: center; padding: 2.5rem 0 1.5rem 0; }
.elite-title {
    font-family: 'Orbitron', monospace !important;
    font-size: 3.5rem !important; font-weight: 900 !important; letter-spacing: 8px;
    background: linear-gradient(90deg, #ff4500, #ff8c00, #ff4500);
    background-size: 200% auto;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    animation: shine 3s linear infinite;
    text-transform: uppercase; margin-bottom: 0.2rem;
}
@keyframes shine { to { background-position: 200% center; } }
.tagline {
    font-family: 'Rajdhani', sans-serif; color: rgba(255,200,100,0.85);
    font-size: 1.1rem; font-weight: 500; letter-spacing: 6px; text-transform: uppercase; margin-top: 0;
}
.title-line {
    width: 120px; height: 2px;
    background: linear-gradient(90deg, transparent, #ff6b00, transparent);
    margin: 1rem auto 0;
}
.stChatMessage {
    background: rgba(8,8,8,0.85) !important; backdrop-filter: blur(20px) !important;
    border-radius: 4px !important; border: 1px solid rgba(255,107,53,0.2) !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
}
[data-testid="stChatInput"] {
    background: rgba(5,5,5,0.9) !important; backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255,107,53,0.35) !important; border-radius: 4px !important;
}
[data-testid="stChatInputTextArea"] {
    color: #ffffff !important; font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.05rem !important; font-weight: 500 !important;
}
[data-testid="stChatInputTextArea"]::placeholder { color: rgba(255,140,50,0.45) !important; }
[data-testid="stChatInputSubmitButton"] {
    background: linear-gradient(135deg, #ff4500, #ff8c00) !important;
    border-radius: 3px !important;
}
.stMarkdown, .stText, p { color: rgba(255,255,255,0.92) !important; font-family: 'Rajdhani', sans-serif !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: linear-gradient(#ff4500, #ff8c00); border-radius: 2px; }
.car-gallery-label {
    font-family: 'Orbitron', monospace; font-size: 0.65rem; letter-spacing: 3px;
    color: rgba(255,140,50,0.9); text-transform: uppercase; margin: 18px 0 10px 2px;
    border-left: 3px solid #ff6b00; padding-left: 10px;
}
.car-card {
    border-radius: 6px; overflow: hidden;
    border: 1px solid rgba(255,107,53,0.3);
    box-shadow: 0 6px 24px rgba(0,0,0,0.6);
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    background: #0d0d0d;
    margin-bottom: 8px;
}
.car-card:hover {
    transform: scale(1.03) translateY(-4px);
    box-shadow: 0 20px 50px rgba(255,107,53,0.2);
    border-color: rgba(255,107,53,0.6);
}
.car-card img {
    width: 100%; height: 185px; object-fit: cover; display: block;
}
.car-card-caption {
    font-family: 'Orbitron', monospace; font-size: 0.62rem; font-weight: 700;
    text-align: center; padding: 9px 6px; letter-spacing: 2px; text-transform: uppercase;
    color: rgba(255,200,100,0.95); background: rgba(0,0,0,0.9);
    border-top: 1px solid rgba(255,107,53,0.2);
}
.status-badge {
    display: inline-block;
    background: linear-gradient(90deg, rgba(255,69,0,0.12), rgba(255,140,0,0.12));
    border: 1px solid rgba(255,107,53,0.4); border-radius: 2px; padding: 4px 14px;
    font-family: 'Orbitron', monospace; font-size: 0.6rem; letter-spacing: 3px;
    color: rgba(255,180,80,0.9); text-transform: uppercase; margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# CAR IMAGE DATABASE
# Uses Wikimedia Commons API (most reliable, designed for programmatic access)
# Format: car_key -> [wikimedia_filename, fallback_direct_url]
# ==================================================

# Wikimedia Commons base for thumbnails (very reliable, no hotlink blocking)
WM_THUMB = "https://upload.wikimedia.org/wikipedia/commons/thumb"

CAR_IMAGE_DB = {
    # === TATA ===
    "tata punch": [
        f"{WM_THUMB}/a/a7/Tata_Punch_EV_2024.jpg/640px-Tata_Punch_EV_2024.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20211021062543_Tata_Punch.jpg&h=578&w=872&c=1",
    ],
    "tata nexon ev": [
        f"{WM_THUMB}/d/d3/Tata_Nexon_EV_Max_2023.jpg/640px-Tata_Nexon_EV_Max_2023.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230117010706_Nexon.jpg&h=578&w=872&c=1",
    ],
    "tata nexon": [
        f"{WM_THUMB}/d/d3/Tata_Nexon_EV_Max_2023.jpg/640px-Tata_Nexon_EV_Max_2023.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230606025214_Tata-Nexon-facelift.jpg&h=578&w=872&c=1",
    ],
    "tata harrier": [
        f"{WM_THUMB}/2/23/Tata_Harrier_Gold_Edition.jpg/640px-Tata_Harrier_Gold_Edition.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230621045226_Tata-Harrier.jpg&h=578&w=872&c=1",
    ],
    "tata safari": [
        f"{WM_THUMB}/d/d5/Tata_Safari_2021.jpg/640px-Tata_Safari_2021.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230621041834_Tata-Safari.jpg&h=578&w=872&c=1",
    ],
    "tata altroz": [
        f"{WM_THUMB}/e/e7/Tata_Altroz_2020.jpg/640px-Tata_Altroz_2020.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118031228_Altroz.jpg&h=578&w=872&c=1",
    ],
    "tata tiago": [
        f"{WM_THUMB}/4/4c/Tata_Tiago_NRG_2023.jpg/640px-Tata_Tiago_NRG_2023.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118031323_Tiago.jpg&h=578&w=872&c=1",
    ],
    "tata curvv": [
        f"{WM_THUMB}/6/6e/Tata_Curvv_EV_2024.jpg/640px-Tata_Curvv_EV_2024.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230827043053_Tata-Curvv.jpg&h=578&w=872&c=1",
    ],
    # === MAHINDRA ===
    "mahindra thar": [
        f"{WM_THUMB}/9/9e/2020_Mahindra_Thar_LX_Hard_Top.jpg/640px-2020_Mahindra_Thar_LX_Hard_Top.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20231006044028_Mahindra-Thar.jpg&h=578&w=872&c=1",
    ],
    "mahindra scorpio n": [
        f"{WM_THUMB}/a/a6/Mahindra_Scorpio_N_2022.jpg/640px-Mahindra_Scorpio_N_2022.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20220627065424_Scorpio-N.jpg&h=578&w=872&c=1",
    ],
    "mahindra scorpio": [
        f"{WM_THUMB}/e/e5/Mahindra_Scorpio_Classic_2022.jpg/640px-Mahindra_Scorpio_Classic_2022.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20220803033455_Scorpio-Classic.jpg&h=578&w=872&c=1",
    ],
    "mahindra xuv700": [
        f"{WM_THUMB}/d/d2/Mahindra_XUV700_AX7_Luxury_Pack.jpg/640px-Mahindra_XUV700_AX7_Luxury_Pack.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20211013043827_XUV700.jpg&h=578&w=872&c=1",
    ],
    "mahindra xuv300": [
        f"{WM_THUMB}/5/5a/Mahindra_XUV300_W8_2019.jpg/640px-Mahindra_XUV300_W8_2019.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118032101_XUV300.jpg&h=578&w=872&c=1",
    ],
    "mahindra bolero": [
        f"{WM_THUMB}/e/e3/Mahindra_Bolero_Neo_2021.jpg/640px-Mahindra_Bolero_Neo_2021.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118032220_Bolero.jpg&h=578&w=872&c=1",
    ],
    # === HYUNDAI ===
    "hyundai creta": [
        f"{WM_THUMB}/c/c5/2024_Hyundai_Creta.jpg/640px-2024_Hyundai_Creta.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20240115061147_Hyundai-Creta.jpg&h=578&w=872&c=1",
    ],
    "hyundai verna": [
        f"{WM_THUMB}/0/07/2023_Hyundai_Verna.jpg/640px-2023_Hyundai_Verna.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230307033108_Verna.jpg&h=578&w=872&c=1",
    ],
    "hyundai i20": [
        f"{WM_THUMB}/7/76/Hyundai_i20_2021_facelift.jpg/640px-Hyundai_i20_2021_facelift.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118032634_i20.jpg&h=578&w=872&c=1",
    ],
    "hyundai venue": [
        f"{WM_THUMB}/7/7d/2023_Hyundai_Venue.jpg/640px-2023_Hyundai_Venue.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118031741_Venue.jpg&h=578&w=872&c=1",
    ],
    "hyundai tucson": [
        f"{WM_THUMB}/f/f7/2022_Hyundai_Tucson_NX4.jpg/640px-2022_Hyundai_Tucson_NX4.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20220831060048_Tucson.jpg&h=578&w=872&c=1",
    ],
    "hyundai ioniq 5": [
        f"{WM_THUMB}/8/86/Hyundai_Ioniq_5_Inspiration_%28NE%29%2C_Frontansicht%2C_22._September_2021%2C_D%C3%BCsseldorf.jpg/640px-Hyundai_Ioniq_5_Inspiration_%28NE%29%2C_Frontansicht%2C_22._September_2021%2C_D%C3%BCsseldorf.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20220322034043_Ioniq5.jpg&h=578&w=872&c=1",
    ],
    "hyundai ioniq 6": [
        f"{WM_THUMB}/6/6c/2022_Hyundai_Ioniq_6_SEL.jpg/640px-2022_Hyundai_Ioniq_6_SEL.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230623043310_Ioniq-6.jpg&h=578&w=872&c=1",
    ],
    "hyundai exter": [
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230711033412_Hyundai-Exter.jpg&h=578&w=872&c=1",
        f"{WM_THUMB}/c/c5/2024_Hyundai_Creta.jpg/640px-2024_Hyundai_Creta.jpg",
    ],
    # === KIA ===
    "kia seltos": [
        f"{WM_THUMB}/7/70/2023_Kia_Seltos.jpg/640px-2023_Kia_Seltos.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230112035752_Kia-Seltos.jpg&h=578&w=872&c=1",
    ],
    "kia sonet": [
        f"{WM_THUMB}/b/b0/Kia_Sonet_2020.jpg/640px-Kia_Sonet_2020.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118033032_Sonet.jpg&h=578&w=872&c=1",
    ],
    "kia carens": [
        f"{WM_THUMB}/0/0e/Kia_Carens_2022.jpg/640px-Kia_Carens_2022.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20220127064237_Carens.jpg&h=578&w=872&c=1",
    ],
    "kia ev6": [
        f"{WM_THUMB}/5/52/Kia_EV6_GT-Line_AWD_%28CV6%29%2C_Frontansicht%2C_23._September_2021%2C_D%C3%BCsseldorf.jpg/640px-Kia_EV6_GT-Line_AWD_%28CV6%29%2C_Frontansicht%2C_23._September_2021%2C_D%C3%BCsseldorf.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230602043337_Kia-EV6.jpg&h=578&w=872&c=1",
    ],
    "kia sportage": [
        f"{WM_THUMB}/b/b5/2022_Kia_Sportage_SX_Prestige_AWD%2C_Front_8.21.22.jpg/640px-2022_Kia_Sportage_SX_Prestige_AWD%2C_Front_8.21.22.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20220830060942_Sportage.jpg&h=578&w=872&c=1",
    ],
    # === MARUTI SUZUKI ===
    "maruti suzuki swift": [
        f"{WM_THUMB}/9/9f/Maruti_Suzuki_Swift_2024.jpg/640px-Maruti_Suzuki_Swift_2024.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20240307033427_Maruti-Suzuki-Swift.jpg&h=578&w=872&c=1",
    ],
    "maruti suzuki baleno": [
        f"{WM_THUMB}/e/ef/2022_Maruti_Suzuki_Baleno_%28India%29_-_Zeta_AT.jpg/640px-2022_Maruti_Suzuki_Baleno_%28India%29_-_Zeta_AT.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20220216073018_Baleno.jpg&h=578&w=872&c=1",
    ],
    "maruti suzuki grand vitara": [
        f"{WM_THUMB}/d/df/2022_Maruti_Suzuki_Grand_Vitara_Alpha_Plus.jpg/640px-2022_Maruti_Suzuki_Grand_Vitara_Alpha_Plus.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20220929054428_GrandVitara.jpg&h=578&w=872&c=1",
    ],
    "maruti suzuki brezza": [
        f"{WM_THUMB}/5/57/2022_Maruti_Suzuki_Brezza.jpg/640px-2022_Maruti_Suzuki_Brezza.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20220630053047_Brezza.jpg&h=578&w=872&c=1",
    ],
    "maruti suzuki dzire": [
        f"{WM_THUMB}/6/60/Maruti_Suzuki_Dzire_2024.jpg/640px-Maruti_Suzuki_Dzire_2024.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20240611034518_Maruti-Suzuki-Dzire.jpg&h=578&w=872&c=1",
    ],
    "maruti suzuki ertiga": [
        f"{WM_THUMB}/2/29/Maruti_Suzuki_Ertiga_2022.jpg/640px-Maruti_Suzuki_Ertiga_2022.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118034455_Ertiga.jpg&h=578&w=872&c=1",
    ],
    "maruti suzuki fronx": [
        f"{WM_THUMB}/3/3e/Maruti_Suzuki_Fronx_2023.jpg/640px-Maruti_Suzuki_Fronx_2023.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230427060521_Fronx.jpg&h=578&w=872&c=1",
    ],
    "maruti suzuki jimny": [
        f"{WM_THUMB}/4/4f/Maruti_Suzuki_Jimny_2023_India.jpg/640px-Maruti_Suzuki_Jimny_2023_India.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230620042621_Jimny.jpg&h=578&w=872&c=1",
    ],
    # === TOYOTA ===
    "toyota innova crysta": [
        f"{WM_THUMB}/a/a5/2021_Toyota_Innova_Crysta_G_MT.jpg/640px-2021_Toyota_Innova_Crysta_G_MT.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118034821_InnovaCrysta.jpg&h=578&w=872&c=1",
    ],
    "toyota innova hycross": [
        f"{WM_THUMB}/d/d5/Toyota_Innova_HyCross_2023.jpg/640px-Toyota_Innova_HyCross_2023.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20221125040148_InnovaHyCross.jpg&h=578&w=872&c=1",
    ],
    "toyota fortuner": [
        f"{WM_THUMB}/0/08/2021_Toyota_Fortuner_Legender_4x4_AT.jpg/640px-2021_Toyota_Fortuner_Legender_4x4_AT.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118035031_Fortuner.jpg&h=578&w=872&c=1",
    ],
    "toyota camry": [
        f"{WM_THUMB}/9/96/2024_Toyota_Camry_%28XV70%3B_facelift%2C_Australia%29%2C_front_8.16.23.jpg/640px-2024_Toyota_Camry_%28XV70%3B_facelift%2C_Australia%29%2C_front_8.16.23.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118035204_Camry.jpg&h=578&w=872&c=1",
    ],
    "toyota land cruiser": [
        f"{WM_THUMB}/3/38/2022_Toyota_Land_Cruiser_300_ZX_%28UAE%29.jpg/640px-2022_Toyota_Land_Cruiser_300_ZX_%28UAE%29.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20211012041108_LandCruiser.jpg&h=578&w=872&c=1",
    ],
    "toyota urban cruiser hyryder": [
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20220722065507_Hyryder.jpg&h=578&w=872&c=1",
        f"{WM_THUMB}/d/df/2022_Maruti_Suzuki_Grand_Vitara_Alpha_Plus.jpg/640px-2022_Maruti_Suzuki_Grand_Vitara_Alpha_Plus.jpg",
    ],
    # === HONDA ===
    "honda city": [
        f"{WM_THUMB}/d/df/2023_Honda_City_RS_e%3AHEV.jpg/640px-2023_Honda_City_RS_e%3AHEV.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118035342_City.jpg&h=578&w=872&c=1",
    ],
    "honda elevate": [
        f"{WM_THUMB}/1/10/Honda_Elevate_2023.jpg/640px-Honda_Elevate_2023.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230706035624_Honda-Elevate.jpg&h=578&w=872&c=1",
    ],
    "honda civic": [
        f"{WM_THUMB}/9/99/2022_Honda_Civic_Sport_FE%2C_front_7.28.22.jpg/640px-2022_Honda_Civic_Sport_FE%2C_front_7.28.22.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20220113073252_Civic.jpg&h=578&w=872&c=1",
    ],
    "honda amaze": [
        f"{WM_THUMB}/c/c3/Honda_Amaze_2018.jpg/640px-Honda_Amaze_2018.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118034158_Amaze.jpg&h=578&w=872&c=1",
    ],
    "honda cr-v": [
        f"{WM_THUMB}/4/4e/2022_Honda_CR-V_Touring.jpg/640px-2022_Honda_CR-V_Touring.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20231201035924_Honda-CRV.jpg&h=578&w=872&c=1",
    ],
    # === MG ===
    "mg hector": [
        f"{WM_THUMB}/0/07/MG_Hector_Plus_2022_in_India.jpg/640px-MG_Hector_Plus_2022_in_India.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118033624_Hector.jpg&h=578&w=872&c=1",
    ],
    "mg zs ev": [
        f"{WM_THUMB}/0/06/2021_MG_ZS_EV_Excite.jpg/640px-2021_MG_ZS_EV_Excite.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118033449_MGZSEV.jpg&h=578&w=872&c=1",
    ],
    "mg gloster": [
        f"{WM_THUMB}/4/42/MG_Gloster_2020.jpg/640px-MG_Gloster_2020.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118033803_Gloster.jpg&h=578&w=872&c=1",
    ],
    # === JEEP ===
    "jeep wrangler": [
        f"{WM_THUMB}/0/0a/2021_Jeep_Wrangler_Unlimited_Rubicon_392%2C_front_8.15.21.jpg/640px-2021_Jeep_Wrangler_Unlimited_Rubicon_392%2C_front_8.15.21.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118033929_Wrangler.jpg&h=578&w=872&c=1",
    ],
    "jeep compass": [
        f"{WM_THUMB}/8/80/2021_Jeep_Compass_Limited_4x4%2C_front_11.14.21.jpg/640px-2021_Jeep_Compass_Limited_4x4%2C_front_11.14.21.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118033942_Compass.jpg&h=578&w=872&c=1",
    ],
    "jeep meridian": [
        f"{WM_THUMB}/5/58/2022_Jeep_Meridian_Limited_O.jpg/640px-2022_Jeep_Meridian_Limited_O.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20220512040133_Meridian.jpg&h=578&w=872&c=1",
    ],
    # === SKODA / VW ===
    "skoda slavia": [
        f"{WM_THUMB}/6/66/2022_Skoda_Slavia_Style_MT.jpg/640px-2022_Skoda_Slavia_Style_MT.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20220113071923_Slavia.jpg&h=578&w=872&c=1",
    ],
    "skoda kushaq": [
        f"{WM_THUMB}/a/a3/Skoda_Kushaq_2021.jpg/640px-Skoda_Kushaq_2021.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118034038_Kushaq.jpg&h=578&w=872&c=1",
    ],
    "skoda superb": [
        f"{WM_THUMB}/a/a8/2024_Skoda_Superb.jpg/640px-2024_Skoda_Superb.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20240403034423_Skoda-Superb.jpg&h=578&w=872&c=1",
    ],
    "volkswagen taigun": [
        f"{WM_THUMB}/8/80/Volkswagen_Taigun_2021_India.jpg/640px-Volkswagen_Taigun_2021_India.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118034155_Taigun.jpg&h=578&w=872&c=1",
    ],
    "volkswagen virtus": [
        f"{WM_THUMB}/e/e6/Volkswagen_Virtus_2022_India.jpg/640px-Volkswagen_Virtus_2022_India.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20220601051014_Virtus.jpg&h=578&w=872&c=1",
    ],
    # === NISSAN ===
    "nissan magnite": [
        f"{WM_THUMB}/d/d7/Nissan_Magnite_2021.jpg/640px-Nissan_Magnite_2021.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118035513_Magnite.jpg&h=578&w=872&c=1",
    ],
    "nissan gt-r": [
        f"{WM_THUMB}/a/a0/2017_Nissan_GT-R_Premium%2C_front_4.4.18.jpg/640px-2017_Nissan_GT-R_Premium%2C_front_4.4.18.jpg",
        "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?n=https://cdni.autocarindia.com/ExtraImages/20230118035612_GTR.jpg&h=578&w=872&c=1",
    ],
    # === TESLA ===
    "tesla model 3": [
        f"{WM_THUMB}/e/ef/Tesla_Model_3_facelift.jpg/640px-Tesla_Model_3_facelift.jpg",
        f"{WM_THUMB}/0/09/Tesla_Model_3_%282020%29_front_left.jpg/640px-Tesla_Model_3_%282020%29_front_left.jpg",
    ],
    "tesla model y": [
        f"{WM_THUMB}/e/e4/Tesla_Model_Y_Front.jpg/640px-Tesla_Model_Y_Front.jpg",
        f"{WM_THUMB}/3/38/Tesla_Model_Y%2C_front_8.3.22.jpg/640px-Tesla_Model_Y%2C_front_8.3.22.jpg",
    ],
    "tesla model s": [
        f"{WM_THUMB}/9/91/2020_Tesla_Model_S_Long_Range_Plus%2C_front_1.21.20.jpg/640px-2020_Tesla_Model_S_Long_Range_Plus%2C_front_1.21.20.jpg",
        f"{WM_THUMB}/e/ef/Tesla_Model_3_facelift.jpg/640px-Tesla_Model_3_facelift.jpg",
    ],
    "tesla model x": [
        f"{WM_THUMB}/7/7a/2021_Tesla_Model_X_Long_Range%2C_front_11.8.21.jpg/640px-2021_Tesla_Model_X_Long_Range%2C_front_11.8.21.jpg",
        f"{WM_THUMB}/e/e4/Tesla_Model_Y_Front.jpg/640px-Tesla_Model_Y_Front.jpg",
    ],
    # === BYD ===
    "byd seal": [
        f"{WM_THUMB}/0/0e/BYD_Seal_%282022%29_front_left.jpg/640px-BYD_Seal_%282022%29_front_left.jpg",
        f"{WM_THUMB}/b/bf/BYD_Atto_3_front_left_2022.jpg/640px-BYD_Atto_3_front_left_2022.jpg",
    ],
    "byd atto 3": [
        f"{WM_THUMB}/b/bf/BYD_Atto_3_front_left_2022.jpg/640px-BYD_Atto_3_front_left_2022.jpg",
        f"{WM_THUMB}/0/0e/BYD_Seal_%282022%29_front_left.jpg/640px-BYD_Seal_%282022%29_front_left.jpg",
    ],
    # === PORSCHE ===
    "porsche taycan": [
        f"{WM_THUMB}/8/8d/2021_Porsche_Taycan_4S.jpg/640px-2021_Porsche_Taycan_4S.jpg",
        f"{WM_THUMB}/7/70/Porsche_911_GT3_%28992%29_IAA_2021.jpg/640px-Porsche_911_GT3_%28992%29_IAA_2021.jpg",
    ],
    "porsche 911": [
        f"{WM_THUMB}/7/70/Porsche_911_GT3_%28992%29_IAA_2021.jpg/640px-Porsche_911_GT3_%28992%29_IAA_2021.jpg",
        f"{WM_THUMB}/8/8d/2021_Porsche_Taycan_4S.jpg/640px-2021_Porsche_Taycan_4S.jpg",
    ],
    "porsche cayenne": [
        f"{WM_THUMB}/3/35/2019_Porsche_Cayenne_S_Coupe_%28E3%29%2C_front_11.3.19.jpg/640px-2019_Porsche_Cayenne_S_Coupe_%28E3%29%2C_front_11.3.19.jpg",
        f"{WM_THUMB}/7/70/Porsche_911_GT3_%28992%29_IAA_2021.jpg/640px-Porsche_911_GT3_%28992%29_IAA_2021.jpg",
    ],
    "porsche macan": [
        f"{WM_THUMB}/8/82/2024_Porsche_Macan_EV.jpg/640px-2024_Porsche_Macan_EV.jpg",
        f"{WM_THUMB}/3/35/2019_Porsche_Cayenne_S_Coupe_%28E3%29%2C_front_11.3.19.jpg/640px-2019_Porsche_Cayenne_S_Coupe_%28E3%29%2C_front_11.3.19.jpg",
    ],
    # === BMW ===
    "bmw 3 series": [
        f"{WM_THUMB}/3/35/2019_BMW_330i_M_Sport_%28G20%29%2C_front_11.10.19.jpg/640px-2019_BMW_330i_M_Sport_%28G20%29%2C_front_11.10.19.jpg",
        f"{WM_THUMB}/5/5e/2022_BMW_M5_Competition_%28F90%2C_facelift%29%2C_front_9.6.21.jpg/640px-2022_BMW_M5_Competition_%28F90%2C_facelift%29%2C_front_9.6.21.jpg",
    ],
    "bmw 5 series": [
        f"{WM_THUMB}/2/2c/2024_BMW_530i_%28G60%29%2C_front_11.23.jpg/640px-2024_BMW_530i_%28G60%29%2C_front_11.23.jpg",
        f"{WM_THUMB}/3/35/2019_BMW_330i_M_Sport_%28G20%29%2C_front_11.10.19.jpg/640px-2019_BMW_330i_M_Sport_%28G20%29%2C_front_11.10.19.jpg",
    ],
    "bmw 7 series": [
        f"{WM_THUMB}/f/f4/2023_BMW_740i_%28G70%29%2C_front_8.18.22.jpg/640px-2023_BMW_740i_%28G70%29%2C_front_8.18.22.jpg",
        f"{WM_THUMB}/2/2c/2024_BMW_530i_%28G60%29%2C_front_11.23.jpg/640px-2024_BMW_530i_%28G60%29%2C_front_11.23.jpg",
    ],
    "bmw m3": [
        f"{WM_THUMB}/7/79/2021_BMW_M3_Competition_%28G80%29%2C_front_8.11.21.jpg/640px-2021_BMW_M3_Competition_%28G80%29%2C_front_8.11.21.jpg",
        f"{WM_THUMB}/5/5e/2022_BMW_M5_Competition_%28F90%2C_facelift%29%2C_front_9.6.21.jpg/640px-2022_BMW_M5_Competition_%28F90%2C_facelift%29%2C_front_9.6.21.jpg",
    ],
    "bmw m5": [
        f"{WM_THUMB}/5/5e/2022_BMW_M5_Competition_%28F90%2C_facelift%29%2C_front_9.6.21.jpg/640px-2022_BMW_M5_Competition_%28F90%2C_facelift%29%2C_front_9.6.21.jpg",
        f"{WM_THUMB}/7/79/2021_BMW_M3_Competition_%28G80%29%2C_front_8.11.21.jpg/640px-2021_BMW_M3_Competition_%28G80%29%2C_front_8.11.21.jpg",
    ],
    "bmw x5": [
        f"{WM_THUMB}/a/ae/2019_BMW_X5_xDrive40i_%28G05%29%2C_front_11.10.19.jpg/640px-2019_BMW_X5_xDrive40i_%28G05%29%2C_front_11.10.19.jpg",
        f"{WM_THUMB}/3/35/2023_BMW_X7_xDrive40i_%28G07%2C_facelift%29%2C_front_8.18.22.jpg/640px-2023_BMW_X7_xDrive40i_%28G07%2C_facelift%29%2C_front_8.18.22.jpg",
    ],
    "bmw x7": [
        f"{WM_THUMB}/3/35/2023_BMW_X7_xDrive40i_%28G07%2C_facelift%29%2C_front_8.18.22.jpg/640px-2023_BMW_X7_xDrive40i_%28G07%2C_facelift%29%2C_front_8.18.22.jpg",
        f"{WM_THUMB}/a/ae/2019_BMW_X5_xDrive40i_%28G05%29%2C_front_11.10.19.jpg/640px-2019_BMW_X5_xDrive40i_%28G05%29%2C_front_11.10.19.jpg",
    ],
    "bmw i4": [
        f"{WM_THUMB}/a/ae/2022_BMW_i4_eDrive40%2C_front_7.4.22.jpg/640px-2022_BMW_i4_eDrive40%2C_front_7.4.22.jpg",
        f"{WM_THUMB}/3/35/2019_BMW_330i_M_Sport_%28G20%29%2C_front_11.10.19.jpg/640px-2019_BMW_330i_M_Sport_%28G20%29%2C_front_11.10.19.jpg",
    ],
    "bmw i7": [
        f"{WM_THUMB}/5/59/2023_BMW_i7_xDrive60.jpg/640px-2023_BMW_i7_xDrive60.jpg",
        f"{WM_THUMB}/f/f4/2023_BMW_740i_%28G70%29%2C_front_8.18.22.jpg/640px-2023_BMW_740i_%28G70%29%2C_front_8.18.22.jpg",
    ],
    # === MERCEDES ===
    "mercedes c class": [
        f"{WM_THUMB}/f/f2/2022_Mercedes-Benz_C_300_AMG_Line_%28W206%29%2C_front_10.22.jpg/640px-2022_Mercedes-Benz_C_300_AMG_Line_%28W206%29%2C_front_10.22.jpg",
        f"{WM_THUMB}/c/c2/2024_Mercedes-Benz_E_220_d_%28W214%29%2C_front_10.23.jpg/640px-2024_Mercedes-Benz_E_220_d_%28W214%29%2C_front_10.23.jpg",
    ],
    "mercedes e class": [
        f"{WM_THUMB}/c/c2/2024_Mercedes-Benz_E_220_d_%28W214%29%2C_front_10.23.jpg/640px-2024_Mercedes-Benz_E_220_d_%28W214%29%2C_front_10.23.jpg",
        f"{WM_THUMB}/f/f2/2022_Mercedes-Benz_C_300_AMG_Line_%28W206%29%2C_front_10.22.jpg/640px-2022_Mercedes-Benz_C_300_AMG_Line_%28W206%29%2C_front_10.22.jpg",
    ],
    "mercedes s class": [
        f"{WM_THUMB}/0/01/2021_Mercedes-Benz_S_500_4Matic_%28W223%29%2C_front_8.14.21.jpg/640px-2021_Mercedes-Benz_S_500_4Matic_%28W223%29%2C_front_8.14.21.jpg",
        f"{WM_THUMB}/c/c2/2024_Mercedes-Benz_E_220_d_%28W214%29%2C_front_10.23.jpg/640px-2024_Mercedes-Benz_E_220_d_%28W214%29%2C_front_10.23.jpg",
    ],
    "mercedes eqs": [
        f"{WM_THUMB}/2/28/2022_Mercedes-Benz_EQS_580_4MATIC.jpg/640px-2022_Mercedes-Benz_EQS_580_4MATIC.jpg",
        f"{WM_THUMB}/0/01/2021_Mercedes-Benz_S_500_4Matic_%28W223%29%2C_front_8.14.21.jpg/640px-2021_Mercedes-Benz_S_500_4Matic_%28W223%29%2C_front_8.14.21.jpg",
    ],
    "mercedes gle": [
        f"{WM_THUMB}/8/8e/Mercedes-Benz_GLE_W167_IAA_2019.jpg/640px-Mercedes-Benz_GLE_W167_IAA_2019.jpg",
        f"{WM_THUMB}/0/01/2021_Mercedes-Benz_S_500_4Matic_%28W223%29%2C_front_8.14.21.jpg/640px-2021_Mercedes-Benz_S_500_4Matic_%28W223%29%2C_front_8.14.21.jpg",
    ],
    # === AUDI ===
    "audi a4": [
        f"{WM_THUMB}/d/d9/2020_Audi_A4_S_Line_35_TFSI%2C_front_8.11.20.jpg/640px-2020_Audi_A4_S_Line_35_TFSI%2C_front_8.11.20.jpg",
        f"{WM_THUMB}/c/c9/2019_Audi_A6_S_Line_50_TDI_Quattro%2C_front_8.11.19.jpg/640px-2019_Audi_A6_S_Line_50_TDI_Quattro%2C_front_8.11.19.jpg",
    ],
    "audi a6": [
        f"{WM_THUMB}/c/c9/2019_Audi_A6_S_Line_50_TDI_Quattro%2C_front_8.11.19.jpg/640px-2019_Audi_A6_S_Line_50_TDI_Quattro%2C_front_8.11.19.jpg",
        f"{WM_THUMB}/d/d9/2020_Audi_A4_S_Line_35_TFSI%2C_front_8.11.20.jpg/640px-2020_Audi_A4_S_Line_35_TFSI%2C_front_8.11.20.jpg",
    ],
    "audi q5": [
        f"{WM_THUMB}/6/69/2021_Audi_Q5_S_Line_40_TDI_Quattro%2C_front_9.6.21.jpg/640px-2021_Audi_Q5_S_Line_40_TDI_Quattro%2C_front_9.6.21.jpg",
        f"{WM_THUMB}/1/10/2020_Audi_Q7_S_Line_50_TDI_Quattro%2C_front_11.10.19.jpg/640px-2020_Audi_Q7_S_Line_50_TDI_Quattro%2C_front_11.10.19.jpg",
    ],
    "audi q7": [
        f"{WM_THUMB}/1/10/2020_Audi_Q7_S_Line_50_TDI_Quattro%2C_front_11.10.19.jpg/640px-2020_Audi_Q7_S_Line_50_TDI_Quattro%2C_front_11.10.19.jpg",
        f"{WM_THUMB}/6/69/2021_Audi_Q5_S_Line_40_TDI_Quattro%2C_front_9.6.21.jpg/640px-2021_Audi_Q5_S_Line_40_TDI_Quattro%2C_front_9.6.21.jpg",
    ],
    "audi e-tron gt": [
        f"{WM_THUMB}/8/8e/2022_Audi_e-tron_GT_quattro.jpg/640px-2022_Audi_e-tron_GT_quattro.jpg",
        f"{WM_THUMB}/8/8d/2021_Porsche_Taycan_4S.jpg/640px-2021_Porsche_Taycan_4S.jpg",
    ],
    # === LUXURY / SUPERCARS ===
    "rolls-royce spectre": [
        f"{WM_THUMB}/c/c2/Rolls-Royce_Spectre%2C_IAA_2023.jpg/640px-Rolls-Royce_Spectre%2C_IAA_2023.jpg",
        f"{WM_THUMB}/6/6d/Rolls-Royce_Ghost_%28II%29%2C_front_9.6.21.jpg/640px-Rolls-Royce_Ghost_%28II%29%2C_front_9.6.21.jpg",
    ],
    "rolls-royce ghost": [
        f"{WM_THUMB}/6/6d/Rolls-Royce_Ghost_%28II%29%2C_front_9.6.21.jpg/640px-Rolls-Royce_Ghost_%28II%29%2C_front_9.6.21.jpg",
        f"{WM_THUMB}/c/c2/Rolls-Royce_Spectre%2C_IAA_2023.jpg/640px-Rolls-Royce_Spectre%2C_IAA_2023.jpg",
    ],
    "rolls-royce cullinan": [
        f"{WM_THUMB}/b/ba/Rolls-Royce_Cullinan_%28RR31%29_-_IAA_2019.jpg/640px-Rolls-Royce_Cullinan_%28RR31%29_-_IAA_2019.jpg",
        f"{WM_THUMB}/6/6d/Rolls-Royce_Ghost_%28II%29%2C_front_9.6.21.jpg/640px-Rolls-Royce_Ghost_%28II%29%2C_front_9.6.21.jpg",
    ],
    "bentley bentayga": [
        f"{WM_THUMB}/c/c5/2021_Bentley_Bentayga_V8%2C_front_11.14.21.jpg/640px-2021_Bentley_Bentayga_V8%2C_front_11.14.21.jpg",
        f"{WM_THUMB}/b/ba/Rolls-Royce_Cullinan_%28RR31%29_-_IAA_2019.jpg/640px-Rolls-Royce_Cullinan_%28RR31%29_-_IAA_2019.jpg",
    ],
    "lamborghini huracan": [
        f"{WM_THUMB}/4/4c/Lamborghini_Huracan_Tecnica_%28IAA_2021%29.jpg/640px-Lamborghini_Huracan_Tecnica_%28IAA_2021%29.jpg",
        f"{WM_THUMB}/3/3d/Lamborghini_Urus_%28IAA_2021%29.jpg/640px-Lamborghini_Urus_%28IAA_2021%29.jpg",
    ],
    "lamborghini urus": [
        f"{WM_THUMB}/3/3d/Lamborghini_Urus_%28IAA_2021%29.jpg/640px-Lamborghini_Urus_%28IAA_2021%29.jpg",
        f"{WM_THUMB}/4/4c/Lamborghini_Huracan_Tecnica_%28IAA_2021%29.jpg/640px-Lamborghini_Huracan_Tecnica_%28IAA_2021%29.jpg",
    ],
    "lamborghini revuelto": [
        f"{WM_THUMB}/7/70/Lamborghini_Revuelto_%28IAA_2023%29.jpg/640px-Lamborghini_Revuelto_%28IAA_2023%29.jpg",
        f"{WM_THUMB}/4/4c/Lamborghini_Huracan_Tecnica_%28IAA_2021%29.jpg/640px-Lamborghini_Huracan_Tecnica_%28IAA_2021%29.jpg",
    ],
    "ferrari roma": [
        f"{WM_THUMB}/8/8a/2020_Ferrari_Roma.jpg/640px-2020_Ferrari_Roma.jpg",
        f"{WM_THUMB}/4/4c/Lamborghini_Huracan_Tecnica_%28IAA_2021%29.jpg/640px-Lamborghini_Huracan_Tecnica_%28IAA_2021%29.jpg",
    ],
    "mclaren 720s": [
        f"{WM_THUMB}/3/36/McLaren_720S_%28IAA_2017%29.jpg/640px-McLaren_720S_%28IAA_2017%29.jpg",
        f"{WM_THUMB}/4/4c/Lamborghini_Huracan_Tecnica_%28IAA_2021%29.jpg/640px-Lamborghini_Huracan_Tecnica_%28IAA_2021%29.jpg",
    ],
    "ford mustang": [
        f"{WM_THUMB}/8/80/2020_Ford_Mustang_GT_Fastback%2C_front_8.25.19.jpg/640px-2020_Ford_Mustang_GT_Fastback%2C_front_8.25.19.jpg",
        f"{WM_THUMB}/3/36/McLaren_720S_%28IAA_2017%29.jpg/640px-McLaren_720S_%28IAA_2017%29.jpg",
    ],
    "range rover sport": [
        f"{WM_THUMB}/4/4f/2022_Range_Rover_Sport_Autobiography.jpg/640px-2022_Range_Rover_Sport_Autobiography.jpg",
        f"{WM_THUMB}/9/9c/Range_Rover_%28L460%29_First_Edition_P530%2C_front_10.11.22.jpg/640px-Range_Rover_%28L460%29_First_Edition_P530%2C_front_10.11.22.jpg",
    ],
    "range rover": [
        f"{WM_THUMB}/9/9c/Range_Rover_%28L460%29_First_Edition_P530%2C_front_10.11.22.jpg/640px-Range_Rover_%28L460%29_First_Edition_P530%2C_front_10.11.22.jpg",
        f"{WM_THUMB}/4/4f/2022_Range_Rover_Sport_Autobiography.jpg/640px-2022_Range_Rover_Sport_Autobiography.jpg",
    ],
    "land rover defender": [
        f"{WM_THUMB}/6/6c/2020_Land_Rover_Defender_110_First_Edition.jpg/640px-2020_Land_Rover_Defender_110_First_Edition.jpg",
        f"{WM_THUMB}/4/4f/2022_Range_Rover_Sport_Autobiography.jpg/640px-2022_Range_Rover_Sport_Autobiography.jpg",
    ],
    "lexus rx": [
        f"{WM_THUMB}/3/3a/2023_Lexus_RX_350h_F_Sport.jpg/640px-2023_Lexus_RX_350h_F_Sport.jpg",
        f"{WM_THUMB}/0/08/2021_Toyota_Fortuner_Legender_4x4_AT.jpg/640px-2021_Toyota_Fortuner_Legender_4x4_AT.jpg",
    ],
    "volvo xc90": [
        f"{WM_THUMB}/b/b3/Volvo_XC90_B6_AWD_%282021%29_front_8.22.jpg/640px-Volvo_XC90_B6_AWD_%282021%29_front_8.22.jpg",
        f"{WM_THUMB}/9/9c/Range_Rover_%28L460%29_First_Edition_P530%2C_front_10.11.22.jpg/640px-Range_Rover_%28L460%29_First_Edition_P530%2C_front_10.11.22.jpg",
    ],
    "lucid air": [
        f"{WM_THUMB}/5/5a/Lucid_Air_Dream_Edition.jpg/640px-Lucid_Air_Dream_Edition.jpg",
        f"{WM_THUMB}/e/ef/Tesla_Model_3_facelift.jpg/640px-Tesla_Model_3_facelift.jpg",
    ],
}

# ==================================================
# CAR ALIASES (short names → canonical key)
# ==================================================
CAR_ALIASES = {
    "punch": "tata punch", "nexon ev": "tata nexon ev", "nexon": "tata nexon",
    "harrier": "tata harrier", "safari": "tata safari", "altroz": "tata altroz",
    "tiago": "tata tiago", "curvv": "tata curvv",
    "thar": "mahindra thar", "scorpio n": "mahindra scorpio n", "scorpio": "mahindra scorpio",
    "xuv700": "mahindra xuv700", "xuv300": "mahindra xuv300", "bolero": "mahindra bolero",
    "creta": "hyundai creta", "verna": "hyundai verna", "i20": "hyundai i20",
    "venue": "hyundai venue", "tucson": "hyundai tucson",
    "ioniq 5": "hyundai ioniq 5", "ioniq 6": "hyundai ioniq 6", "exter": "hyundai exter",
    "seltos": "kia seltos", "sonet": "kia sonet", "carens": "kia carens",
    "ev6": "kia ev6", "sportage": "kia sportage",
    "swift": "maruti suzuki swift", "baleno": "maruti suzuki baleno",
    "grand vitara": "maruti suzuki grand vitara", "brezza": "maruti suzuki brezza",
    "dzire": "maruti suzuki dzire", "ertiga": "maruti suzuki ertiga",
    "fronx": "maruti suzuki fronx", "jimny": "maruti suzuki jimny",
    "innova crysta": "toyota innova crysta", "innova hycross": "toyota innova hycross",
    "fortuner": "toyota fortuner", "camry": "toyota camry",
    "land cruiser": "toyota land cruiser", "hyryder": "toyota urban cruiser hyryder",
    "city": "honda city", "amaze": "honda amaze", "elevate": "honda elevate",
    "civic": "honda civic", "cr-v": "honda cr-v",
    "hector": "mg hector", "zs ev": "mg zs ev", "gloster": "mg gloster",
    "wrangler": "jeep wrangler", "compass": "jeep compass", "meridian": "jeep meridian",
    "slavia": "skoda slavia", "kushaq": "skoda kushaq", "superb": "skoda superb",
    "taigun": "volkswagen taigun", "virtus": "volkswagen virtus",
    "magnite": "nissan magnite", "gt-r": "nissan gt-r",
    "model 3": "tesla model 3", "model y": "tesla model y",
    "model s": "tesla model s", "model x": "tesla model x",
    "seal": "byd seal", "atto 3": "byd atto 3",
    "taycan": "porsche taycan", "911": "porsche 911",
    "macan": "porsche macan", "cayenne": "porsche cayenne",
    "3 series": "bmw 3 series", "5 series": "bmw 5 series", "7 series": "bmw 7 series",
    "m3": "bmw m3", "m5": "bmw m5", "x5": "bmw x5", "x7": "bmw x7",
    "i4": "bmw i4", "i7": "bmw i7",
    "c class": "mercedes c class", "e class": "mercedes e class",
    "s class": "mercedes s class", "eqs": "mercedes eqs", "gle": "mercedes gle",
    "a4": "audi a4", "a6": "audi a6", "q5": "audi q5", "q7": "audi q7",
    "e-tron gt": "audi e-tron gt",
    "spectre": "rolls-royce spectre", "ghost": "rolls-royce ghost",
    "cullinan": "rolls-royce cullinan", "bentayga": "bentley bentayga",
    "huracan": "lamborghini huracan", "urus": "lamborghini urus",
    "revuelto": "lamborghini revuelto", "roma": "ferrari roma",
    "720s": "mclaren 720s", "mustang": "ford mustang",
    "range rover sport": "range rover sport", "range rover": "range rover",
    "defender": "land rover defender", "rx": "lexus rx",
    "xc90": "volvo xc90", "lucid air": "lucid air",
}

# ==================================================
# IMAGE FETCHER — server-side, cached, bulletproof
# ==================================================
FETCH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Referer": "https://en.wikipedia.org/",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def make_svg_placeholder(label: str) -> str:
    name = label.upper()[:28]
    return f'''<svg width="640" height="360" xmlns="http://www.w3.org/2000/svg">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#0d0d0d"/>
    <stop offset="100%" stop-color="#1a0800"/>
  </linearGradient>
  <linearGradient id="glow" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="transparent"/>
    <stop offset="50%" stop-color="#ff6b00"/>
    <stop offset="100%" stop-color="transparent"/>
  </linearGradient>
</defs>
<rect width="640" height="360" fill="url(#bg)"/>
<rect x="0" y="0" width="640" height="3" fill="url(#glow)"/>
<rect x="0" y="357" width="640" height="3" fill="url(#glow)"/>
<rect x="0" y="0" width="3" height="360" fill="#ff4500" opacity="0.4"/>
<rect x="637" y="0" width="3" height="360" fill="#ff4500" opacity="0.4"/>
<text x="320" y="155" font-family="Arial" font-size="72" fill="#1a1a1a" text-anchor="middle">🏎</text>
<text x="320" y="225" font-family="Arial Black" font-size="18" font-weight="900"
      fill="#ff6b00" text-anchor="middle" letter-spacing="5">{name}</text>
<text x="320" y="258" font-family="Arial" font-size="11"
      fill="rgba(255,120,30,0.55)" text-anchor="middle" letter-spacing="4">PREMIUM VEHICLE</text>
<text x="320" y="290" font-family="Arial" font-size="10"
      fill="rgba(255,80,0,0.35)" text-anchor="middle" letter-spacing="2">image unavailable</text>
</svg>'''

@st.cache_data(ttl=3600, show_spinner=False)
def get_car_image_data_uri(car_key: str) -> str:
    """
    Fetches car image server-side and returns a data URI (base64).
    Falls back to SVG placeholder if all URLs fail.
    Cached for 1 hour so repeated renders are instant.
    """
    urls = CAR_IMAGE_DB.get(car_key, [])

    for url in urls:
        try:
            r = requests.get(url, headers=FETCH_HEADERS, timeout=12, stream=True)
            content_type = r.headers.get("Content-Type", "")
            if r.status_code == 200 and "image" in content_type:
                mime = content_type.split(";")[0].strip()
                # Validate it's actually image bytes
                content = r.content
                if len(content) > 500:  # at least 500 bytes = real image
                    b64 = base64.b64encode(content).decode("utf-8")
                    return f"data:{mime};base64,{b64}"
        except Exception:
            continue

    # All failed → SVG placeholder
    svg_bytes = make_svg_placeholder(car_key).encode("utf-8")
    b64 = base64.b64encode(svg_bytes).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"


# ==================================================
# GROQ API
# ==================================================
def get_car_context():
    return """Current Trending Cars (2024-2025):
    Electric: Tesla Model 3, Hyundai Ioniq 6, BYD Seal, Lucid Air, Tata Nexon EV, Hyundai Creta Electric
    Performance: Porsche Taycan, BMW M5, Lamborghini Revuelto, Ferrari Roma
    Luxury: Mercedes EQS, Rolls-Royce Spectre, Bentley Bentayga
    SUVs: Range Rover Sport, Lexus RX, Mahindra XUV700, Toyota Fortuner
    Indian Market: Tata Punch, Mahindra Thar, Hyundai Creta, Kia Seltos, Maruti Suzuki Swift, Maruti Fronx
    Supercars: Lamborghini Huracan, McLaren 720S, Porsche 911
    Trends: 40% EV adoption in premium, strong growth in Indian SUV segment"""

def groq_car_chat(prompt: str, context: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content":
                "You are EliteDrive AI — a premium car consultant with expertise in luxury, "
                "performance, electric, and everyday vehicles. Provide detailed specs, comparisons, "
                "pros/cons, real-world range for EVs, and ownership cost analysis. "
                "When asked to show or compare cars, always mention the car names clearly. "
                "Be concise yet comprehensive. Use a sophisticated, confident tone."},
            {"role": "user", "content": f"CONTEXT: {context}\n\nUSER QUESTION: {prompt}"}
        ],
        "temperature": 0.7,
        "max_tokens": 1024,
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        return f"⚠️ API Error {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return f"⚠️ Connection error: {str(e)}"


# ==================================================
# SMART CAR DETECTION
# ==================================================
def extract_cars(text: str) -> list[str]:
    """Extract car names from text — longest match first, no duplicates."""
    lowered = text.lower()
    found_order = []
    found_set = set()

    # Sort keys by length descending so "scorpio n" matches before "scorpio"
    all_keys = sorted(
        list(CAR_IMAGE_DB.keys()) + list(CAR_ALIASES.keys()),
        key=len, reverse=True
    )

    for key in all_keys:
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, lowered):
            canonical = CAR_ALIASES.get(key, key)
            if canonical in CAR_IMAGE_DB and canonical not in found_set:
                found_set.add(canonical)
                found_order.append(canonical)
                # Remove matched text so partial aliases don't double-match
                lowered = re.sub(pattern, " " * len(key), lowered)

    return found_order[:6]  # max 6 cars per response


# ==================================================
# GALLERY RENDERER — uses server-side data URIs
# ==================================================
def render_car_gallery(car_keys: list[str]):
    if not car_keys:
        return

    st.markdown(
        '<div class="car-gallery-label">📸 &nbsp;VEHICLE GALLERY</div>',
        unsafe_allow_html=True
    )

    cols_count = min(3, len(car_keys))
    cols = st.columns(cols_count)

    for i, key in enumerate(car_keys):
        with cols[i % cols_count]:
            # Fetch image server-side (cached)
            data_uri = get_car_image_data_uri(key)
            label = key.title()
            st.markdown(f"""
<div class="car-card">
  <img src="{data_uri}" alt="{label}" loading="lazy" />
  <div class="car-card-caption">{label}</div>
</div>
""", unsafe_allow_html=True)


# ==================================================
# MAIN UI
# ==================================================
st.markdown("""
<div class="title-container">
    <div class="elite-title">ELITEDRIVE AI</div>
    <div class="tagline">◆ Your Premium Car Intelligence ◆</div>
    <div class="title-line"></div>
</div>
<div style="text-align:center; margin-bottom: 2rem;">
    <span class="status-badge">● System Online — Ready to Consult</span>
</div>
""", unsafe_allow_html=True)

# Session state
if "car_messages" not in st.session_state:
    st.session_state.car_messages = []

# Render chat history
for msg in st.session_state.car_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("cars"):
            render_car_gallery(msg["cars"])

# Chat input
if prompt := st.chat_input("Ask about any car — specs, comparisons, price, EV range..."):
    # User message
    st.session_state.car_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing premium vehicle data..."):
            answer = groq_car_chat(prompt, get_car_context())
            st.markdown(answer)

            # Detect cars in BOTH the question and the answer
            cars = extract_cars(prompt + " " + answer)

            if cars:
                render_car_gallery(cars)

            st.session_state.car_messages.append({
                "role": "assistant",
                "content": answer,
                "cars": cars,
            })
