import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Neural Bin - Waste Segregation Helper Ai", layout="wide")

# --- CUSTOM CSS FOR NAVBAR & THEME (#76e8b9) ---
st.markdown(f"""
    <style>
    /* Main Background & Fonts */
    .stApp {{
        background-color: #f0fdf4; /* Very light tint of green */
    }}
    
    /* Premium Navbar Styling */
    .nav-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: white;
        padding: 15px 60px;
        border-radius: 0px 0px 25px 25px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        margin-bottom: 40px;
        border-bottom: 2px solid #76e8b9;
    }}
    .logo-section {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .logo-icon {{
        background-color: #059669;
        padding: 10px;
        border-radius: 12px;
        color: white;
        font-size: 20px;
    }}
    .logo-text {{
        line-height: 1;
    }}
    .brand-name {{
        font-size: 26px;
        font-weight: 800;
        color: #064e3b;
        letter-spacing: -1px;
    }}
    .brand-tag {{
        font-size: 10px;
        color: #059669;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .nav-right {{
        display: flex;
        align-items: center;
        gap: 20px;
    }}
    .scan-status {{
        background-color: #ecfdf5;
        color: #065f46;
        padding: 8px 18px;
        border-radius: 30px;
        font-size: 13px;
        font-weight: 700;
        border: 1px solid #76e8b9;
    }}
    .leaderboard-btn {{
        background: white;
        color: #064e3b;
        padding: 8px 22px;
        border-radius: 30px;
        font-size: 13px;
        font-weight: 700;
        border: 1px solid #76e8b9;
        cursor: pointer;
    }}

    /* Bin Cards */
    .bin-grid {{
        display: flex;
        gap: 20px;
        margin-bottom: 30px;
    }}
    .bin-card {{
        flex: 1;
        padding: 40px 20px;
        border-radius: 25px;
        text-align: center;
        color: white;
        font-weight: 800;
        font-size: 20px;
        transition: 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }}
    .bin-card:hover {{ transform: translateY(-10px); }}
    .organic-style {{ background: linear-gradient(135deg, #10b981, #059669); }}
    .recycle-style {{ background: linear-gradient(135deg, #3b82f6, #1d4ed8); }}
    .landfill-style {{ background: linear-gradient(135deg, #ef4444, #b91c1c); }}

    /* Streamlit UI Tweaks */
    .stButton>button {{
        background-color: #76e8b9 !important;
        color: #064e3b !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 15px !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 6px rgba(118, 232, 185, 0.3) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- DEVELOPER DATA STORE ---
DEVELOPER_DB = {
    "Organic Bin": [
        {"name": "Apple Scraps", "url": "https://in.pinterest.com/pin/123637952261536929/"},
        {"name": "Banana Peel", "url": "https://i.pinimg.com/1200x/d3/86/63/d38663e930728764d0f7f4b22d64fc70.jpg"}
    ],
    "Recycle Bin": [
        {"name": "Plastic Bottle", "url": "https://example.com/bottle.jpg"},
        {"name": "News Paper", "url": "https://example.com/paper.jpg"}
    ],
    "Landfill Bin": [
        {"name": "Used Diaper", "url": "https://example.com/diaper.jpg"},
        {"name": "Styrofoam", "url": "https://example.com/foam.jpg"}
    ]
}

# --- INITIALIZE SESSION ---
if 'score' not in st.session_state: st.session_state.score = 0
if 'scans' not in st.session_state: st.session_state.scans = 10
if 'leaderboard' not in st.session_state: st.session_state.leaderboard = []

# --- NAVBAR ---
st.markdown(f"""
    <div class="nav-container">
        <div class="logo-section">
            <div class="logo-icon">🍃</div>
            <div class="logo-text">
                <div class="brand-name">neuralbin</div>
                <div class="brand-tag">AI Waste Intelligence</div>
            </div>
        </div>
        <div class="nav-right">
            <div class="scan-status">⏱️ {st.session_state.scans} SCANS LEFT</div>
            <div class="leaderboard-btn">🏅 LEADERBOARD</div>
            <div style="background:#d1fae5; border-radius:50%; width:40px; height:40px; display:flex; align-items:center; justify-content:center;">👤</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- LAYOUT ---
col_main, col_side = st.columns([2.2, 1])

with col_side:
    st.markdown("### 👤 User Registration")
    user_name = st.text_input("Enter your name to unlock AI", placeholder="e.g. Mahendra")
    
    st.markdown("---")
    st.markdown(f"### 🏆 Global Ranking")
    if st.session_state.leaderboard:
        ld_df = pd.DataFrame(st.session_state.leaderboard).sort_values(by="Score", ascending=False)
        st.table(ld_df.head(5))
    else:
        st.info("No scans yet. Start identifying waste!")

with col_main:
    # Three Bins Display
    b1, b2, b3 = st.columns(3)
    b1.markdown('<div class="bin-card organic-style">ORGANIC<br>BIN</div>', unsafe_allow_html=True)
    b2.markdown('<div class="bin-card recycle-style">RECYCLE<br>BIN</div>', unsafe_allow_html=True)
    b3.markdown('<div class="bin-card landfill-style">LANDFILL<br>BIN</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Input Section
    tab1, tab2 = st.tabs(["📸 AI Live Camera", "📁 Upload Image"])
    
    source_img = None
    with tab1:
        source_img = st.camera_input("Scan Waste")
    with tab2:
        source_img = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

    if source_img and user_name:
        if st.session_state.scans <= 0:
            st.error("No scans remaining!")
        else:
            with st.spinner("Analyzing with Neural Model..."):
                time.sleep(1.5)
                
                # Comparison Logic
                file_name = source_img.name.lower()
                matched_category = None
                
                # --- NAYA CORRECTED CODE ---
                # --- NAYA CORRECTED CODE ---
                for category, items in DEVELOPER_DB.items():
                # 'items' ab dictionaries ki list hai, isliye hum 'item["name"]' use karenge
                    if any(item["name"].lower() in file_name for item in items):
                        matched_category = category
                        found = True
                        break
                
                if matched_category:
                    st.balloons()
                    st.success(f"✅ AI Match Found: {file_name.upper()}")
                    st.markdown(f"### Suggested Bin: **{matched_category}**")
                    
                    # Score Calculation
                    points = 15 if "Organic" in matched_category else 10
                    st.session_state.score += points
                    st.session_state.scans -= 1
                    
                    # Update Leaderboard
                    st.session_state.leaderboard.append({"Name": user_name, "Score": st.session_state.score})
                else:
                    # Top-up message for "Not Found"
                    st.markdown("""
                        <div style="background-color:#fee2e2; border:2px solid #ef4444; padding:15px; border-radius:15px; text-align:center; color:#b91c1c; font-weight:bold;">
                        ⚠️ IMAGE NOT FOUND IN DATABASE
                        </div>
                    """, unsafe_allow_html=True)
    elif not user_name and source_img:
        st.warning("Please enter your name in the sidebar first!")