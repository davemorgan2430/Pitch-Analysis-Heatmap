import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

# Streamlit app title
st.title("Pitch Analysis Heatmap")

# Example to add a clickable link
st.markdown("[Need Inspiration? Click here to find and sort for MLB's best pitches of 2024](https://www.fangraphs.com/leaders/major-league?pos=all&stats=pit&lg=all&type=36&season=2024&month=0&season1=2024&ind=0&sortcol=3&sortdir=default&qual=20&pagenum=1")

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
    'estimated_woba_using_speedangle', 'release_extension', 'release_pos_z'
]
if not all(col in df.columns for col in required_columns):
    st.error(
        "The uploaded file is missing required columns. Ensure it contains: "
        "pitch_type, player_name, arm_angle, HB, iVB, p_throws, release_speed, "
        "release_spin_rate, estimated_woba_using_speedangle, release_extension, release_pos_z."
    )
    st.stop()

# Step 1: Select pitch type
selected_pitch = st.selectbox("Select the pitch type", df['pitch_type'].unique())

# Filter DataFrame by selected pitch type
pitch_filtered_df = df[df['pitch_type'] == selected_pitch]

# Step 2: Select handedness
selected_handedness = st.selectbox(
    "Select handedness",
    df['p_throws'].unique()
)

# Step 3: Select pitcher
available_pitchers = pitch_filtered_df['player_name'].unique()
selected_pitcher = st.selectbox("Select a pitcher", available_pitchers)

# Filter data for the selected pitcher
pitcher_data = pitch_filtered_df[pitch_filtered_df['player_name'] == selected_pitcher]

if pitcher_data.empty:
    st.warning("No data found for the selected pitcher.")
    st.stop()

# Calculate and display the selected pitcher's average stats
avg_arm_angle = pitcher_data['arm_angle'].mean()
avg_velocity = pitcher_data['release_speed'].mean()
avg_spin_rate = pitcher_data['release_spin_rate'].mean()
avg_woba = pitcher_data['estimated_woba_using_speedangle'].mean()
avg_extension = pitcher_data['release_extension'].mean()
avg_iVB = pitcher_data['iVB'].mean()
avg_HB = pitcher_data['HB'].mean()

# Retrieve all pitch types thrown by the selected pitcher
pitcher_pitch_types = df[df['player_name'] == selected_pitcher]['pitch_type'].unique()

# Sidebar: Display pitcher stats and pitch types
st.sidebar.header(f"{selected_pitcher} - Pitch Stats")
st.sidebar.write(f"**Pitch Type:** {selected_pitch}")
st.sidebar.write(f"**Average Arm Angle:** {avg_arm_angle:.2f}°")
st.sidebar.write(f"**Average Velocity:** {avg_velocity:.1f} mph")
st.sidebar.write(f"**Average Spin Rate:** {avg_spin_rate:.1f} rpm")
st.sidebar.write(f"**Average wOBA:** {avg_woba:.3f}")
st.sidebar.write(f"**Average Extension:** {avg_extension:.2f} ft")
st.sidebar.write(f"**Average iVB:** {avg_iVB:.2f} in")
st.sidebar.write(f"**Average HB:** {avg_HB:.2f} in")

# Display the list of pitches thrown by the pitcher
st.sidebar.write("**Pitches Thrown:**")
for pitch in pitcher_pitch_types:
    st.sidebar.write(f"- {pitch}")

# Step 4: User inputs arm angle
input_arm_angle = st.number_input(
    "Enter an arm angle to filter the data (default is the pitcher's average):",
    min_value=float(df['arm_angle'].min()),
    max_value=float(df['arm_angle'].max()),
    value=float(avg_arm_angle),
)

# Filter data based on user input
filtered_df = pitch_filtered_df[
    (pitch_filtered_df['arm_angle'] == input_arm_angle) &
    (pitch_filtered_df['p_throws'] == selected_handedness)
]

if filtered_df.empty:
    st.warning("No data matches the selected criteria. Please adjust your filters.")
    st.stop()

# Create a KDE heatmap with HB and iVB
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

# Highlight the selected pitcher's average HB and iVB
average_hb = pitcher_data['HB'].mean()
average_ivb = pitcher_data['iVB'].mean()

plt.scatter(
    average_hb,
    average_ivb,
    color='orange',
    s=100,
    label=f"{selected_pitcher} (Avg HB: {average_hb:.2f}, Avg iVB: {average_ivb:.2f})"
)

# Add lines at x=0 and y=0
plt.axhline(0, color='black', linestyle='--', linewidth=1, label='y=0')  # Horizontal line
plt.axvline(0, color='black', linestyle='--', linewidth=1, label='x=0')  # Vertical line

# Set labels and title
plt.title(f"{selected_pitch} Heatmap | Arm Angle: {input_arm_angle:.2f}°", fontsize=16)
plt.xlabel("Horizontal Break (HB)", fontsize=14)
plt.ylabel("Induced Vertical Break (iVB)", fontsize=14)
plt.xlim(-30, 30)
plt.ylim(-30, 30)

# Display the plot in Streamlit
st.pyplot(plt)


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

# Section: Create a Pitcher
st.header("Create a Pitcher")

# User inputs for creating a pitcher
create_pitch_type = st.selectbox("Select Pitch Type", df['pitch_type'].unique())
create_handedness = st.selectbox("Select Handedness", df['p_throws'].unique())
create_ivb = st.number_input("Enter iVB (Induced Vertical Break)", value=0.0)
create_hb = st.number_input("Enter HB (Horizontal Break)", value=0.0)

# Toggle for single arm angle or range
arm_angle_mode = st.radio(
    "Select Arm Angle Mode",
    options=["Single Arm Angle", "Range of Arm Angles"]
)

if arm_angle_mode == "Single Arm Angle":
    create_arm_angle = st.number_input(
        "Enter Arm Angle",
        min_value=float(df['arm_angle'].min()),
        max_value=float(df['arm_angle'].max()),
        value=0.0
    )
    filtered_df = df[
        (df['pitch_type'] == create_pitch_type) &
        (df['p_throws'] == create_handedness) &
        (df['arm_angle'] == create_arm_angle)
    ]
else:
    create_min_arm_angle = st.number_input(
        "Enter Minimum Arm Angle",
        min_value=float(df['arm_angle'].min()),
        max_value=float(df['arm_angle'].max()),
        value=float(df['arm_angle'].min())
    )
    create_max_arm_angle = st.number_input(
        "Enter Maximum Arm Angle",
        min_value=float(df['arm_angle'].min()),
        max_value=float(df['arm_angle'].max()),
        value=float(df['arm_angle'].max())
    )
    filtered_df = df[
        (df['pitch_type'] == create_pitch_type) &
        (df['p_throws'] == create_handedness) &
        (df['arm_angle'] >= create_min_arm_angle) &
        (df['arm_angle'] <= create_max_arm_angle)
    ]

# Check if filtered data exists
if filtered_df.empty:
    st.warning("No data matches the selected criteria. Please adjust your inputs.")
    st.stop()

# Plotting the heatmap
plt.figure(figsize=(10, 8))
sns.kdeplot(
    data=filtered_df,
    x='HB',
    y='iVB',
    fill=True,
    cmap='viridis',
    thresh=0.05,
    levels=10,
    cbar=True
)

# Highlight the custom pitcher's data point
plt.scatter(
    create_hb,
    create_ivb,
    color='red',
    s=100,
    label=f"Created Pitcher (HB: {create_hb:.2f}, iVB: {create_ivb:.2f})"
)

# Add lines at x=0 and y=0
plt.axhline(0, color='black', linestyle='--', linewidth=1)
plt.axvline(0, color='black', linestyle='--', linewidth=1)

# Set labels and title
title_suffix = (
    f"Arm Angle: {create_arm_angle:.2f}°" if arm_angle_mode == "Single Arm Angle"
    else f"Arm Angle Range: {create_min_arm_angle:.2f}° - {create_max_arm_angle:.2f}°"
)
plt.title(f"Created Pitcher Heatmap | {create_pitch_type} | {title_suffix}", fontsize=16)
plt.xlabel("Horizontal Break (HB)", fontsize=14)
plt.ylabel("Induced Vertical Break (iVB)", fontsize=14)
plt.xlim(-30, 30)
plt.ylim(-30, 30)
plt.legend()

# Display the heatmap
st.pyplot(plt)
