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

# Step 3: Select a pitcher from the filtered data
available_pitchers = filtered_pitch_df['player_name'].unique()
selected_pitcher = st.selectbox("Select a pitcher", available_pitchers)

# Filter data for the selected pitcher
pitcher_data = filtered_pitch_df[filtered_pitch_df['player_name'] == selected_pitcher]

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

# Sidebar: Display pitcher stats
st.sidebar.header(f"{selected_pitcher} - Pitch Stats")
st.sidebar.write(f"**Pitch Type:** {selected_pitch}")
st.sidebar.write(f"**Average Arm Angle:** {avg_arm_angle:.2f}°")
st.sidebar.write(f"**Average Velocity:** {avg_velocity:.1f} mph")
st.sidebar.write(f"**Average Spin Rate:** {avg_spin_rate:.1f} rpm")
st.sidebar.write(f"**Average wOBA:** {avg_woba:.3f}")
st.sidebar.write(f"**Average Extension:** {avg_extension:.2f} ft")
st.sidebar.write(f"**Average iVB:** {avg_iVB:.2f} in")
st.sidebar.write(f"**Average HB:** {avg_HB:.2f} in")

# Step 4: User inputs arm angle
input_arm_angle = st.number_input(
    "Enter an arm angle to filter the data (default is the pitcher's average):",
    min_value=float(df['arm_angle'].min()),
    max_value=float(df['arm_angle'].max()),
    value=float(avg_arm_angle),
)

# Filter data based on user input
final_filtered_df = filtered_pitch_df[
    filtered_pitch_df['arm_angle'] == input_arm_angle
]

if final_filtered_df.empty:
    st.warning("No data matches the selected arm angle. Please adjust the input.")
    st.stop()

# Create a KDE heatmap with HB and iVB
plt.figure(figsize=(10, 8))
sns.kdeplot(
    data=final_filtered_df,
    x='HB',
    y='iVB',
    fill=True,
    cmap='viridis',
    thresh=0.05,
    levels=10,
    cbar=True,
)

# Highlight the selected pitcher's average HB and iVB
plt.scatter(
    avg_HB,
    avg_iVB,
    color='orange',
    s=100,
    label=f"{selected_pitcher} (Avg HB: {avg_HB:.2f}, Avg iVB: {avg_iVB:.2f})"
)

# Add lines at x=0 and y=0
plt.axhline(0, color='black', linestyle='--', linewidth=1, label='y=0')  # Horizontal line
plt.axvline(0, color='black', linestyle='--', linewidth=1, label='x=0')  # Vertical line

# Set labels and title
plt.title(f"{selected_pitch} Heatmap | Arm Angle: {input_arm_angle:.2f}°", fontsize=16)
plt.xlabel("Horizontal Break (HB)", fontsize=14)
plt.ylabel("Induced Vertical Break (iVB)", fontsize=14)

# Set x and y axis limits
plt.xlim(-30, 30)
plt.ylim(-30, 30)

# Display the plot in Streamlit
st.pyplot(plt)

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

# Streamlit app title
st.title("Create Custom Pitcher")

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


# Step 1: Select pitch type
new_selected_pitch = st.selectbox("Select the pitch type for your custom pitcher", df['pitch_type'].unique())

# Step 2: Select handedness
new_selected_handedness = st.selectbox("Select handedness for your custom pitcher", df['p_throws'].unique())

# Step 3: Enter iVB, HB, and arm angle for the new pitcher
new_iVB = st.number_input("Enter the induced vertical break (iVB) in inches", min_value=-30.0, max_value=30.0, value=0.0)
new_HB = st.number_input("Enter the horizontal break (HB) in inches", min_value=-30.0, max_value=30.0, value=0.0)
new_arm_angle = st.number_input("Enter the arm angle in degrees", min_value=-90.0, max_value=90.0, value=0.0)

# Filter data for the selected pitch type, handedness, and arm angle
filtered_custom_df = df[
    (df['pitch_type'] == new_selected_pitch) & 
    (df['p_throws'] == new_selected_handedness) &
    (df['arm_angle'] == new_arm_angle)
]

# Check if we have enough data for the filtered pitchers
if filtered_custom_df.empty:
    st.warning("No data found for pitchers with this pitch type, handedness, and arm angle.")
    st.stop()

# Step 4: Create a heatmap for the selected arm angle, pitch type, and handedness
plt.figure(figsize=(10, 8))

# Create the heatmap with horizontal break (HB) and induced vertical break (iVB)
sns.kdeplot(
    data=filtered_custom_df,
    x='HB',
    y='iVB',
    fill=True,
    cmap='viridis',  # You can change this to any colormap you prefer
    thresh=0.05,     # Threshold for contours to appear
    levels=10,       # Number of contour levels
    cbar=True,       # Add color bar
)

# Highlight the custom pitcher's iVB and HB as a data point
plt.scatter(
    new_HB,
    new_iVB,
    color='orange',
    s=100,
    label=f"New Pitcher (iVB: {new_iVB:.2f}, HB: {new_HB:.2f})"
)

# Add lines at x=0 and y=0
plt.axhline(0, color='black', linestyle='--', linewidth=1, label='y=0')  # Horizontal line
plt.axvline(0, color='black', linestyle='--', linewidth=1, label='x=0')  # Vertical line

# Set labels and title
plt.title(f"Heatmap for {new_selected_pitch} | Arm Angle: {new_arm_angle}°", fontsize=16)
plt.xlabel("Horizontal Break (HB)", fontsize=14)
plt.ylabel("Induced Vertical Break (iVB)", fontsize=14)

# Set x and y axis limits
plt.xlim(-30, 30)
plt.ylim(-30, 30)

# Display the plot in Streamlit
st.pyplot(plt)

