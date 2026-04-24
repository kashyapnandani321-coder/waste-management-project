import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import time
import tensorflow as tf  # AI Model ke liye

# --- PAGE CONFIG ---
st.set_page_config(page_title="Neural Bin - AI Waste Segregator", layout="wide")\

# --- LOAD AI MODEL (MobileNetV2) ---
@st.cache_resource
def load_prediction_model():
    # Yeh model images ko identify karne mein madad karega
    return tf.keras.applications.MobileNetV2(weights="imagenet")

model = load_prediction_model()

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f0fdf4; }
    .nav-container {
        display: flex; justify-content: space-between; align-items: center;
        background-color: white; padding: 15px 60px; border-radius: 0px 0px 25px 25px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05); border-bottom: 2px solid #76e8b9;
    }
    .brand-name { font-size: 26px; font-weight: 800; color: #064e3b; }
    .bin-card {
        padding: 40px 20px; border-radius: 25px; text-align: center;
        color: white; font-weight: 800; font-size: 20px; transition: 0.3s;
    }
    .organic-style { background: linear-gradient(135deg, #10b981, #059669); }
    .recycle-style { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
    .landfill-style { background: linear-gradient(135deg, #ef4444, #b91c1c); }
    </style>
    """, unsafe_allow_html=True)

# --- WASTE MAPPING ---
# AI jo keywords pehchanega unhe bins mein map karna
WASTE_MAP = {
    "Organic": ["apple", "banana", "orange", "lemon", "broccoli", "head_cabbage", "mushroom", "cucumber", "Agricultural Waste"],
    "Recycle": ["water_bottle", "pill_bottle", "can", "carton", "envelope", "notebook", "plastic_bag"],
    "Landfill": ["diaper", "styrofoam", "cigarette", "plastic_wrap", "lighter", "Paper", "cardboard", "Wood", "Asphalt"]
}

# --- INITIALIZE SESSION ---
if 'score' not in st.session_state: st.session_state.score = 0
if 'scans' not in st.session_state: st.session_state.scans = 10
if 'leaderboard' not in st.session_state: st.session_state.leaderboard = []

# --- NAVBAR ---
st.markdown(f"""
    <div class="nav-container">
        <div class="brand-name">🍃 neuralbin</div>
        <div style="display:flex; gap:20px; align-items:center;">
            <div style="background:#ecfdf5; padding:8px 15px; border-radius:20px; border:1px solid #76e8b9;">
                ⏱️ {st.session_state.scans} SCANS LEFT
            </div>
            <div style="font-weight:bold;">🏆 Score: {st.session_state.score}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

col_main, col_side = st.columns([2.2, 1])

with col_side:
    st.markdown("### 👤 Registration")
    user_name = st.text_input("Enter name", placeholder="Mahendra")
    st.markdown("---")
    st.markdown("### 🏅 Leaderboard")
    if st.session_state.leaderboard:
        df = pd.DataFrame(st.session_state.leaderboard).sort_values(by="Score", ascending=False)
        st.table(df.head(5))

with col_main:
    b1, b2, b3 = st.columns(3)
    b1.markdown('<div class="bin-card organic-style">ORGANIC</div>', unsafe_allow_html=True)
    b2.markdown('<div class="bin-card recycle-style">RECYCLE</div>', unsafe_allow_html=True)
    b3.markdown('<div class="bin-card landfill-style">LANDFILL</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📸 Live Camera", "📁 Upload"])
    source_img = None
    with tab1: source_img = st.camera_input("Scan")
    with tab2: source_img = st.file_uploader("Choose file", type=["jpg", "png", "jpeg"])

    if source_img and user_name:
        if st.session_state.scans <= 0:
            st.error("Out of scans!")
        else:
            with st.spinner("AI is thinking..."):
                # 1. Image Processing
                img = Image.open(source_img).convert('RGB')
                img_resized = img.resize((224, 224))
                img_array = tf.keras.preprocessing.image.img_to_array(img_resized)
                img_array = tf.expand_dims(img_array, 0)
                img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)

                # 2. Prediction
                predictions = model.predict(img_array)
                decoded = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=3)[0]
                
                # Sabse zyada probability wali cheez
                detected_item = decoded[0][1].lower()
                
                # ... (pichle code jaisa image processing)
                
                # 3. Logic to find bin (Yahan thoda improvement hai)
                matched_category = None
                detected_display_name = ""

                # Hum sirf Top 1 nahi, Top 3 predictions check karenge 
                # taaki accuracy behtar ho sake
                for i in range(3):
                    label = decoded[i][1].lower()
                    for cat, keywords in WASTE_MAP.items():
                        if any(key in label for key in keywords):
                            matched_category = cat
                            detected_display_name = label
                            break
                    if matched_category: break

                if matched_category:
                    st.balloons()
                    st.success(f"✅ AI Match Found!")
                    
                    # Result Display Card
                    st.markdown(f"""
                        <div style="background-color:white; padding:20px; border-radius:15px; border-left:10px solid #76e8b9;">
                            <h2 style="color:#064e3b; margin:0;">Item: {detected_display_name.replace('_', ' ').upper()}</h2>
                            <h3 style="color:#059669; margin:0;">Move to: {matched_category} Bin</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Update State
                    points = 15 if matched_category == "Organic" else 10
                    st.session_state.score += points
                    st.session_state.scans -= 1
                    st.session_state.leaderboard.append({"Name": user_name, "Score": st.session_state.score})
                    
                    # Thoda wait karke refresh karein taaki user result dekh sake
                    time.sleep(2)
                    st.rerun() 
                else:
                    st.error(f"❌ AI couldn't classify the item. Try another angle!")

    elif source_img and not user_name:
        st.error("Please enter your name first!")