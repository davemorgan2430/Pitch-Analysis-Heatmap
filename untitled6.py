# Code for my Streamlit App. The app can be found at https://pitch-analysis-heatmap.streamlit.app/

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

st.title("Movement Plot Analysis")

# Example to add a clickable link
st.markdown("[Need Inspiration? Click here to sort and filter through 2024's best pitches via FanGraphs.](https://www.fangraphs.com/leaders/major-league?pos=all&stats=pit&lg=all&type=36&season=2024&month=0&season1=2024&ind=0&sortcol=3&sortdir=default&qual=20&pagenum=1)")

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

# Section: Combined Analysis
st.header("Pitch Analysis and Movement Comparison")

# Dropdown menu for selecting analysis type
analysis_type = st.selectbox(
    "Select Analysis Type",
    ["All Movements vs League Average", "Single Pitch Movement vs League Average"]
)

if analysis_type == "Single Pitch Movement vs League Average":
    st.subheader("Single Pitch Movement vs League Average")
    selected_pitch = st.selectbox("Select the pitch type", df['pitch_type'].unique())
    pitch_filtered_df = df[df['pitch_type'] == selected_pitch]
    selected_handedness = st.selectbox("Select handedness", df['p_throws'].unique())
    available_pitchers = pitch_filtered_df['player_name'].unique()
    selected_pitcher = st.selectbox("Select a pitcher", available_pitchers)
    pitcher_data = pitch_filtered_df[pitch_filtered_df['player_name'] == selected_pitcher]

    if pitcher_data.empty:
        st.warning("No data found for the selected pitcher.")
    else:
        avg_arm_angle = pitcher_data['arm_angle'].mean()
        arm_angle_range = [avg_arm_angle - 3, avg_arm_angle + 3]

        # Button to adjust range
        if st.button("Adjust Arm Angle Range ±3°"):
            arm_angle_range = [avg_arm_angle - 3, avg_arm_angle + 3]
            st.info(f"Arm angle range adjusted to {arm_angle_range[0]:.2f}° to {arm_angle_range[1]:.2f}°.")

        # Filter data based on arm angle range
        filtered_df = pitch_filtered_df[
            (pitch_filtered_df['arm_angle'].between(arm_angle_range[0], arm_angle_range[1])) &
            (pitch_filtered_df['p_throws'] == selected_handedness)
        ]

        if filtered_df.empty:
            st.warning("No data matches the selected criteria. Please adjust your filters.")
        else:
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
            average_hb = pitcher_data['HB'].mean()
            average_ivb = pitcher_data['iVB'].mean()
            plt.scatter(
                average_hb,
                average_ivb,
                color='orange',
                s=100,
                label=f"{selected_pitcher} (Avg HB: {average_hb:.2f}, Avg iVB: {average_ivb:.2f})"
            )
            plt.axhline(0, color='black', linestyle='--', linewidth=1)
            plt.axvline(0, color='black', linestyle='--', linewidth=1)
            plt.title(f"{selected_pitch} Heatmap | Arm Angle: {arm_angle_range[0]:.2f}° to {arm_angle_range[1]:.2f}°", fontsize=16)
            plt.xlabel("Horizontal Break (HB)", fontsize=14)
            plt.ylabel("Induced Vertical Break (iVB)", fontsize=14)
            plt.xlim(-30, 30)
            plt.ylim(-30, 30)
            plt.legend()
            st.pyplot(plt)

elif analysis_type == "All Movements vs League Average":
    st.subheader("All Movements vs League Average")
    pitcher_name = st.selectbox("Select a pitcher for comparison", df['player_name'].unique())
    pitcher_df = df[df['player_name'] == pitcher_name]

    if not pitcher_df.empty:
        avg_arm_angle = pitcher_df['arm_angle'].mean()
        arm_angle_range = [avg_arm_angle - 3, avg_arm_angle + 3]

        # Button to adjust range
        if st.button("Adjust Arm Angle Range ±3°"):
            arm_angle_range = [avg_arm_angle - 3, avg_arm_angle + 3]
            st.info(f"Arm angle range adjusted to {arm_angle_range[0]:.2f}° to {arm_angle_range[1]:.2f}°.")

        league_data = df[
            (df['p_throws'] == pitcher_df['p_throws'].iloc[0]) &
            (df['arm_angle'].between(arm_angle_range[0], arm_angle_range[1]))
        ]

        plt.figure(figsize=(10, 8))
        colormap_dict = {
            'Fastball': 'Reds',
            'Slider': 'Blues',
            'Changeup': 'Greens',
            'Curveball': 'Purples',
        }

        for pitch_type in pitcher_df['pitch_type'].unique():
            pitch_league_data = league_data[league_data['pitch_type'] == pitch_type]
            sns.kdeplot(
                data=pitch_league_data,
                x='HB',
                y='iVB',
                fill=True,
                cmap=colormap_dict.get(pitch_type, 'viridis'),
                thresh=0.05,
                levels=15,
                alpha=0.5,
            )
            pitch_data = pitcher_df[pitcher_df['pitch_type'] == pitch_type]
            avg_hb = pitch_data['HB'].mean()
            avg_ivb = pitch_data['iVB'].mean()
            plt.scatter(avg_hb, avg_ivb, color='black', s=100, edgecolor='white', label=f"{pitch_type} (Player)")
            plt.text(
                avg_hb, avg_ivb, pitch_type,
                fontsize=10, color='black', ha='center', va='center', weight='bold',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3')
            )

        plt.axhline(0, color='black', linestyle='--', linewidth=1)
        plt.axvline(0, color='black', linestyle='--', linewidth=1)
        plt.title(f"{pitcher_name} vs League Average Pitch Movement", fontsize=16)
        plt.xlabel("Horizontal Break (HB)", fontsize=14)
        plt.ylabel("Induced Vertical Break (iVB)", fontsize=14)
        plt.xlim(-30, 30)
        plt.ylim(-30, 30)
        plt.legend()
        st.pyplot(plt)
    else:
        st.warning("No data available for the selected pitcher.")

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

# Section: Create a Pitcher with Combined Plot
st.header("Create a Pitcher")

# Button to reset session state
if st.button("Reset All Data"):
    st.session_state['user_pitches'] = []  # Clear all user pitches
    st.success("All data has been reset!")

# Step 1: Select handedness
selected_handedness = st.selectbox("Select handedness:", df['p_throws'].unique())

# Step 2: Select arm angle range
min_arm_angle = st.number_input("Enter minimum arm angle:", value=-20.0)
max_arm_angle = st.number_input("Enter maximum arm angle:", value=20.0)

# Filter league data based on handedness and arm angle range
league_filtered = df[
    (df['arm_angle'] >= min_arm_angle) &
    (df['arm_angle'] <= max_arm_angle) &
    (df['p_throws'] == selected_handedness)
]

if league_filtered.empty:
    st.warning("No league data found for the specified criteria.")
    st.stop()

# Step 3: Add pitches with type, iVB, and HB
if 'user_pitches' not in st.session_state:
    st.session_state['user_pitches'] = []

st.subheader("Add Pitches")
pitch_type = st.selectbox("Select pitch type:", df['pitch_type'].unique())
iVB = st.number_input(f"Enter {pitch_type} iVB (inches):")
HB = st.number_input(f"Enter {pitch_type} HB (inches):")

# Button to add the pitch
if st.button("Add Pitch"):
    st.session_state['user_pitches'].append({
        'pitch_type': pitch_type,
        'iVB': iVB,
        'HB': HB
    })
    st.success(f"Added {pitch_type} with iVB={iVB:.2f} and HB={HB:.2f}")

# Step 4: Show all added pitches
if st.session_state['user_pitches']:
    st.write("### Added Pitches:")
    for pitch in st.session_state['user_pitches']:
        st.write(f"- {pitch['pitch_type']}: iVB={pitch['iVB']:.2f}, HB={pitch['HB']:.2f}")

# Step 5: Create a combined heatmap
st.write("### Heatmap vs League Average")
plt.figure(figsize=(12, 10))

# Loop through each unique pitch type in the added pitches
for pitch_type in set(pitch['pitch_type'] for pitch in st.session_state['user_pitches']):
    # Filter league data for this pitch type
    league_pitch_filtered = league_filtered[league_filtered['pitch_type'] == pitch_type]
    
    if league_pitch_filtered.empty:
        st.warning(f"No league data found for pitch type {pitch_type}.")
        continue

    # Overlay league average data for this pitch type
    sns.kdeplot(
        data=league_pitch_filtered,
        x='HB',
        y='iVB',
        fill=True,
        alpha=0.5,
        label=f"League Avg {pitch_type}",
        cmap='viridis',
        levels=15,
        linewidths=1.5,
    )

# Overlay user-defined pitches with KDE and labels
user_data = pd.DataFrame(st.session_state['user_pitches'])
if not user_data.empty:
    for pitch_type in user_data['pitch_type'].unique():
        user_pitch_data = user_data[user_data['pitch_type'] == pitch_type]

        # Add KDE for user pitches
        sns.kdeplot(
            data=user_pitch_data,
            x='HB',
            y='iVB',
            fill=True,
            alpha=0.6,
            cmap='viridis',
            label=f"User {pitch_type}",
            levels=15,
            linewidths=1.5,
        )

        # Add pitch type label
        for _, row in user_pitch_data.iterrows():
            plt.text(
                row['HB'], row['iVB'], row['pitch_type'],
                fontsize=10, color='black', fontweight='bold',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3')
            )

# Add lines at x=0 and y=0
plt.axhline(0, color='black', linestyle='--', linewidth=1, label='y=0')
plt.axvline(0, color='black', linestyle='--', linewidth=1, label='x=0')

# Set labels, title, and legend
plt.title(
    f"Movement Heatmap for User-Defined Pitches | Arm Angle: {min_arm_angle}° to {max_arm_angle}°",
    fontsize=16
)
plt.xlabel("Horizontal Break (HB)", fontsize=14)
plt.ylabel("Induced Vertical Break (iVB)", fontsize=14)
plt.xlim(-30, 30)
plt.ylim(-30, 30)
plt.legend()

# Display the plot in Streamlit
st.pyplot(plt)


import pandas as pd
import streamlit as st
import requests
from io import StringIO

# Input the Google Drive file ID
file_id = "1HHUgH9VK484dgUkX0Ryos7bM8pnukCcJ"  # Replace with your Google Drive file ID
url = f"https://drive.google.com/uc?export=download&id={file_id}"

# Request the file from Google Drive
try:
    response = requests.get(url)
    response.raise_for_status()  # Will raise an error if the file isn't found or downloaded correctly

    # Read the content of the file into a pandas DataFrame
    data = StringIO(response.text)
    zone_df = pd.read_csv(data)

    st.write("Zone Data loaded successfully!")
    st.write(zone_df.head())  # Display the first few rows of the DataFrame

except requests.exceptions.RequestException as e:
    st.error("Error loading the file. Please check the file ID or format.")
    st.error(e)
    st.stop()
