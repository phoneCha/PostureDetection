import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# ----------------- CONFIG -----------------
st.set_page_config(page_title="Hip Angle Analysis", layout="wide")
sns.set_style("whitegrid")

# ----------------- LOAD DATA -----------------
csv_path = os.path.join("..","Detection", "snapshots", "hip_angle_log.csv")
df = pd.read_csv(csv_path)

# Convert the Timestamp column to datetime format with a specified format
df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="%Y-%m-%d_%H-%M-%S")

# ----------------- TITLE -----------------
st.markdown("<h2 style='font-size:22px;'>📊 Hip Angle Analysis Dashboard</h2>", unsafe_allow_html=True)
st.markdown("<p style='font-size:16px;'>Analyze hip angle data and view corresponding snapshots.</p>", unsafe_allow_html=True)

# ----------------- LINE CHART -----------------
st.markdown("<h4 style='font-size:18px;'>1. Hip Angle Over Time</h4>", unsafe_allow_html=True)
st.line_chart(df.set_index("Timestamp")["Hip Angle"])

# ----------------- HISTOGRAM -----------------
st.markdown("<h4 style='font-size:18px;'>2. Distribution of Hip Angles</h4>", unsafe_allow_html=True)

# Reset style and set DPI
sns.reset_orig()
plt.rcParams["figure.dpi"] = 100

fig, ax = plt.subplots(figsize=(2, 1.5))  
sns.histplot(df["Hip Angle"], bins=10, kde=True, ax=ax, color="skyblue")
ax.set_title("Distribution of Hip Angles", fontsize=10)
ax.set_xlabel("Hip Angle (°)", fontsize=8)
ax.set_ylabel("Count", fontsize=8)
ax.tick_params(axis='both', labelsize=7)  # Smaller tick labels
st.pyplot(fig, use_container_width=False)  # Ensure Streamlit respects the size

# ----------------- PIE CHART -----------------
if "Angle Range" in df.columns:
    st.markdown("<h4 style='font-size:18px;'>4. Time Spent in Each Angle Range</h4>", unsafe_allow_html=True)

    # Reset style and set DPI
    sns.reset_orig()
    plt.rcParams["figure.dpi"] = 100

    duration_by_range = df.groupby("Angle Range")["Total Duration (s)"].sum()
    fig2, ax2 = plt.subplots(figsize=(2, 2))  # Reduced size
    ax2.pie(duration_by_range, labels=duration_by_range.index, autopct="%1.1f%%", startangle=90, textprops={'fontsize': 8})
    ax2.axis("equal")  # Equal aspect ratio ensures the pie chart is circular.
    ax2.set_title("Time Spent in Each Angle Range", fontsize=10)
    st.pyplot(fig2, use_container_width=False)  # Ensure Streamlit respects the size

# ----------------- IMAGE PREVIEW -----------------
st.markdown("<h4 style='font-size:18px;'>3. Snapshot Previews</h4>", unsafe_allow_html=True)
img_cols = st.columns(4)
for i, row in df.head(8).iterrows():
    img_path = os.path.join("..", "Detection", "snapshots", row["Image"])
    with img_cols[i % 4]:
        if os.path.exists(img_path):
            st.image(img_path, caption=f"Angle: {row['Hip Angle']}°", width=200)
        else:
            st.write(f"❌ {row['Image']} not found")