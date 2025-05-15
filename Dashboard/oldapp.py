import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ----------------- CONFIG -----------------
st.set_page_config(page_title="Posture Monitor", layout="wide")
sns.set_style("whitegrid")

# ----------------- LOAD DATA -----------------
df = pd.read_csv("posture_data_sample.csv")  # ตรวจสอบให้ไฟล์นี้อยู่ในโฟลเดอร์เดียวกัน
df["timestamp"] = pd.to_datetime(df["timestamp"])

# ----------------- TITLE -----------------
st.markdown("<h2 style='font-size:22px;'>📊 Posture Behavior Dashboard</h2>", unsafe_allow_html=True)
st.markdown("<p style='font-size:16px;'>แสดงพฤติกรรมการนั่งจากข้อมูลมุมหลัง–สะโพก</p>", unsafe_allow_html=True)

# ----------------- LINE CHART -----------------
st.markdown("<h4 style='font-size:18px;'>1. การเปลี่ยนแปลงของมุมหลัง-สะโพกตามเวลา</h4>", unsafe_allow_html=True)
st.line_chart(df.set_index("timestamp")["Hip Angle"])

# ----------------- HISTOGRAM -----------------
st.markdown("<h4 style='font-size:18px;'>2. การกระจายของมุมที่นั่ง</h4>", unsafe_allow_html=True)
col1, _ = st.columns([1, 2])  # แบ่งพื้นที่ให้กราฟอยู่แค่ 1/3
with col1:
    fig, ax = plt.subplots(figsize=(3, 2.2))  # <-- เล็กลง
    sns.histplot(df["Hip Angle"], bins=10, kde=True, ax=ax, color="skyblue")
    ax.set_title("Distribution", fontsize=9)
    ax.set_xlabel("Hip Angle (°)", fontsize=8)
    ax.set_ylabel("Count", fontsize=8)
    ax.tick_params(axis='both', labelsize=7)
    st.pyplot(fig)

# ----------------- PIE CHART -----------------
if "Angle range" in df.columns:
    st.markdown("<h4 style='font-size:18px;'>3. ระยะเวลาที่ใช้ในแต่ละช่วงมุม</h4>", unsafe_allow_html=True)
    duration_by_range = df.groupby("Angle range")["total Duration"].sum()

    col2, _ = st.columns([1, 2])  # ให้กราฟอยู่แค่ 1/3
    with col2:
        fig2, ax2 = plt.subplots(figsize=(3, 3))  # <-- เล็กลง
        ax2.pie(duration_by_range, labels=duration_by_range.index, autopct="%1.1f%%", startangle=90,
                textprops={'fontsize': 8})
        ax2.axis("equal")
        st.pyplot(fig2)


# ----------------- IMAGE PREVIEW -----------------
st.markdown("<h4 style='font-size:18px;'>4. ตัวอย่างภาพ snapshot</h4>", unsafe_allow_html=True)
img_cols = st.columns(4)
for i, row in df.head(8).iterrows():
    img_path = os.path.join("snapshots", row["snapshot(png)"])
    with img_cols[i % 4]:
        if os.path.exists(img_path):
            st.image(img_path, caption=f"Angle: {row['Hip Angle']}°", width=100)
        else:
            st.write(f"❌ {row['snapshot(png)']} not found")
