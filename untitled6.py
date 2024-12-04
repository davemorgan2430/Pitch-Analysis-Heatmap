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


# Step 5: Create your own pitcher feature
st.header("Create Your Own Pitcher")

# User inputs for creating a new pitcher
custom_pitch_type = st.selectbox("Select the pitch type for your pitcher", df['pitch_type'].unique())
custom_handedness = st.selectbox("Select handedness for your pitcher", ['L', 'R'])
custom_arm_angle = st.number_input(
    "Enter arm angle for your pitcher",
    min_value=float(df['arm_angle'].min()),
    max_value=float(df['arm_angle'].max()),
    value=float(avg_arm_angle),
)
custom_ivb = st.number_input("Enter induced Vertical Break (iVB)", min_value=-30.0, max_value=30.0, value=0.0)
custom_hb = st.number_input("Enter Horizontal Break (HB)", min_value=-30.0, max_value=30.0, value=0.0)

# Filter the dataset for all pitchers with the selected pitch type, handedness, and arm angle
custom_filtered_df = pitch_filtered_df[
    (pitch_filtered_df['arm_angle'] == custom_arm_angle) &
    (pitch_filtered_df['pitch_type'] == custom_pitch_type) &
    (pitch_filtered_df['p_throws'] == custom_handedness)
]


# Set x and y axis limits
plt.xlim(-30, 30)
plt.ylim(-30, 30)

# Check if there are matches
if custom_filtered_df.empty:
    st.warning(
        f"No pitchers found with an arm angle of {custom_arm_angle:.2f}°, handedness {custom_handedness}, "
        f"and pitch type {custom_pitch_type}. Heatmap won't include other data."
    )
else:
    # Overlay custom pitcher on the heatmap
    plt.figure(figsize=(10, 8))
    sns.kdeplot(
        data=custom_filtered_df,
        x='HB',
        y='iVB',
        fill=True,
        cmap='viridis',
        thresh=0.05,
        levels=10,
        cbar=True,
    )

    # Add custom pitcher data point
    plt.scatter(
        custom_hb,
        custom_ivb,
        color='orange',
        s=100,
        label=f"Custom Pitcher (HB: {custom_hb:.2f}, iVB: {custom_ivb:.2f}, Arm Angle: {custom_arm_angle:.2f}°, "
              f"Pitch Type: {custom_pitch_type}, Handedness: {custom_handedness})"
    )

    # Add lines at x=0 and y=0
    plt.axhline(0, color='black', linestyle='--', linewidth=1, label='y=0')
    plt.axvline(0, color='black', linestyle='--', linewidth=1, label='x=0')

        # Set plot limits for x and y axes
    plt.xlim(-30, 30)
    plt.ylim(-30, 30)

    # Set labels and title
    plt.title(
        f"Heatmap with Custom Pitcher | Pitch Type: {custom_pitch_type} | Arm Angle: {custom_arm_angle:.2f}° | Handedness: {custom_handedness}",
        fontsize=16
    )
    plt.xlabel("Horizontal Break (HB)", fontsize=14)
    plt.ylabel("Induced Vertical Break (iVB)", fontsize=14)


    
    # Show the plot in Streamlit
    st.pyplot(plt)
