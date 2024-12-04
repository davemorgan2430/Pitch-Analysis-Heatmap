import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

# Streamlit app title
st.title("Pitch Analysis Heatmap")

# Input the Google Drive file ID
file_id = "1lUKCYNnWi02NA6ICynEGrjsH1uqJeSH7"  # Replace with your Google Drive file ID
url = f"https://drive.google.com/uc?id={file_id}"

# Load the CSV file into a DataFrame
try:
    df = pd.read_csv(url)
    st.write("Data loaded successfully!")
except Exception as e:
    st.error("Error loading the file. Please check the file ID or format.")
    st.error(e)
    st.stop()

# Validate required columns
required_columns = [
    'pitch_type', 'player_name', 'arm_angle', 'HB', 'iVB', 
    'p_throws', 'release_speed', 'release_spin_rate', 
    'estimated_woba_using_speedangle', 'release_extension'
]
if not all(col in df.columns for col in required_columns):
    st.error(
        "The uploaded file is missing required columns. Ensure it contains: "
        "pitch_type, player_name, arm_angle, HB, iVB, p_throws, release_speed, "
        "release_spin_rate, estimated_woba_using_speedangle, release_extension."
    )
    st.stop()

# --- Existing Section: Pitch Analysis Heatmap ---
st.subheader("Pitch Analysis Heatmap")

# Step 1: Select pitch type
selected_pitch = st.selectbox("Select the pitch type", df['pitch_type'].unique())

# Step 2: Select handedness
selected_handedness = st.selectbox(
    "Select handedness", df['p_throws'].unique()
)

# Filter DataFrame by selected pitch type and handedness
filtered_pitch_df = df[
    (df['pitch_type'] == selected_pitch) & 
    (df['p_throws'] == selected_handedness)
]

if filtered_pitch_df.empty:
    st.warning("No data matches the selected pitch type and handedness.")
    st.stop()

# Step 3: Enter iVB, HB, and arm angle for the new pitcher
input_arm_angle = st.number_input(
    "Enter an arm angle to filter the data (default is the pitcher's average):",
    min_value=float(df['arm_angle'].min()),
    max_value=float(df['arm_angle'].max()),
    value=float(df['arm_angle'].mean())
)

# Filter data based on user input
filtered_df = filtered_pitch_df[
    (filtered_pitch_df['arm_angle'] == input_arm_angle)
]

# Step 4: Plot heatmap
plt.figure(figsize=(10, 8))
sns.kdeplot(
    data=filtered_df,
    x='HB',
    y='iVB',
    fill=True,
    cmap='viridis',
    thresh=0.05,
    levels=10,
    cbar=True,
)

# Set labels and title
plt.title(f"Heatmap for {selected_pitch} at Arm Angle {input_arm_angle}°", fontsize=16)
plt.xlabel("Horizontal Break (HB)", fontsize=14)
plt.ylabel("Induced Vertical Break (iVB)", fontsize=14)

# Set x and y axis limits
plt.xlim(-30, 30)
plt.ylim(-30, 30)

# Display the plot
st.pyplot(plt)

# --- New Section: Create Custom Pitcher ---
st.subheader("Create Custom Pitcher")

# Step 1: Select pitch type
new_selected_pitch = st.selectbox("Select the pitch type for your custom pitcher", df['pitch_type'].unique())

# Step 2: Select handedness
new_selected_handedness = st.selectbox("Select handedness for your custom pitcher", df['p_throws'].unique())

# Step 3: Enter iVB, HB, and arm angle for the new pitcher
new_iVB = st.number_input("Enter the induced vertical break (iVB) in inches", min_value=-30.0, max_value=30.0, value=0.0)
new_HB = st.number_input("Enter the horizontal break (HB) in inches", min_value=-30.0, max_value=30.0, value=0.0)
new_arm_angle = st.number_input("Enter the arm angle in degrees", min_value=-90.0, max_value=90.0, value=0.0)

# Filter data for the selected pitch type and handedness to calculate league averages
filtered_custom_df = df[
    (df['pitch_type'] == new_selected_pitch) & 
    (df['p_throws'] == new_selected_handedness)
]

# Calculate league average for arm angle and pitch type
league_avg_arm_angle = filtered_custom_df['arm_angle'].mean()
league_avg_iVB = filtered_custom_df['iVB'].mean()
league_avg_HB = filtered_custom_df['HB'].mean()

# Sidebar: Display stats for the new pitcher and league average
st.sidebar.header("New Pitcher vs League Average")
st.sidebar.write(f"**Pitch Type:** {new_selected_pitch}")
st.sidebar.write(f"**Handedness:** {new_selected_handedness}")
st.sidebar.write(f"**New Pitcher's iVB:** {new_iVB:.2f} in")
st.sidebar.write(f"**New Pitcher's HB:** {new_HB:.2f} in")
st.sidebar.write(f"**New Pitcher's Arm Angle:** {new_arm_angle:.2f}°")

st.sidebar.write(f"**League Average Arm Angle:** {league_avg_arm_angle:.2f}°")
st.sidebar.write(f"**League Average iVB:** {league_avg_iVB:.2f} in")
st.sidebar.write(f"**League Average HB:** {league_avg_HB:.2f} in")

# Step 4: Plot comparison between new pitcher and league average
plt.figure(figsize=(10, 8))

# Plot League Average
sns.scatterplot(
    x=[league_avg_HB], y=[league_avg_iVB], 
    color='blue', s=200, label='League Average', marker='X'
)

# Plot New Pitcher
sns.scatterplot(
    x=[new_HB], y=[new_iVB], 
    color='orange', s=200, label='New Pitcher', marker='o'
)

# Add lines at x=0 and y=0
plt.axhline(0, color='black', linestyle='--', linewidth=1, label='y=0')  # Horizontal line
plt.axvline(0, color='black', linestyle='--', linewidth=1, label='x=0')  # Vertical line

# Set labels and title
plt.title(f"Comparison of {new_selected_pitch} Pitch | {new_selected_handedness}-Handed", fontsize=16)
plt.xlabel("Horizontal Break (HB)", fontsize=14)
plt.ylabel("Induced Vertical Break (iVB)", fontsize=14)

# Set x and y axis limits
plt.xlim(-30, 30)
plt.ylim(-30, 30)

# Display the plot in Streamlit
st.pyplot(plt)
