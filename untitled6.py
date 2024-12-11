import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

# Streamlit app title
st.title("Pitch Analysis Heatmap")

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
tab1, tab2, tab3 = st.tabs(["Pitch Analysis Heatmap", "Create a Pitcher", "Pitcher Comparison"])

with tab1:
    st.header("Pitch Analysis Heatmap")
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

with tab2:
    st.header("Create a Pitcher")

# Section: Create a Pitcher with Combined Plot
st.header("Create a Pitcher - Combined Plot for Multiple Pitches")

# Button to reset session state
if st.button("Reset All Data"):
    st.session_state['user_pitches'] = []  # Clear all user pitches
    st.success("All data has been reset!")


with tab3:
    st.header("Pitcher Movement vs. League Average")
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
st.write("### Combined Heatmap")
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
        cmap='viridis',
        alpha=0.5,
        thresh=0.05,
        levels=10,
        label=f"League Avg {pitch_type}"
    )

# Overlay user-defined pitches on the same plot
for pitch in st.session_state['user_pitches']:
    plt.scatter(
        pitch['HB'],
        pitch['iVB'],
        color='orange',
        label=f"{pitch['pitch_type']} (iVB={pitch['iVB']:.2f}, HB={pitch['HB']:.2f})",
        s=100,  # Marker size
        alpha=1.0  # Transparency
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

# Section: Combined Pitcher Movement vs. League Heatmap
st.header("Pitcher Movement vs. League Average Heatmap")

# Input or select pitcher's name
selected_pitcher = st.selectbox(
    "Select a Pitcher:",
    sorted(df['player_name'].unique())
)

if selected_pitcher:
    # Filter data for the selected pitcher
    pitcher_data = df[df['player_name'] == selected_pitcher]

    if pitcher_data.empty:
        st.warning(f"No data found for pitcher {selected_pitcher}.")
    else:
        # Get the handedness of the selected pitcher
        handedness = pitcher_data['p_throws'].iloc[0]

        # Initialize the plot
        plt.figure(figsize=(12, 10))

        for pitch_type in pitcher_data['pitch_type'].unique():
            # Filter pitcher data for the current pitch type
            pitcher_pitch_data = pitcher_data[pitcher_data['pitch_type'] == pitch_type]

            # Get arm angle range
            arm_angle_min = pitcher_pitch_data['arm_angle'].min()
            arm_angle_max = pitcher_pitch_data['arm_angle'].max()

            # Filter league data for the same handedness, pitch type, and arm angle range
            league_pitch_data = df[
                (df['pitch_type'] == pitch_type) &
                (df['p_throws'] == handedness) &
                (df['arm_angle'] >= arm_angle_min) &
                (df['arm_angle'] <= arm_angle_max)
            ]

            # Generate a heatmap for league data (HB vs. iVB)
            sns.kdeplot(
                data=league_pitch_data,
                x='HB',
                y='iVB',
                fill=True,
                cmap='viridis',  # Use distinct color map for league average
                alpha=0.6,
                thresh=0.05,  # Threshold for contours to appear
                levels=10,
                label=f"League Avg: {pitch_type}",
            )

            # Overlay the pitcher's data points for the current pitch type
            avg_hb = pitcher_pitch_data['HB'].mean()
            avg_ivb = pitcher_pitch_data['iVB'].mean()

            plt.scatter(
                avg_hb,
                avg_ivb,
                s=100,
                label=f"{selected_pitcher} ({pitch_type})",
                edgecolor='black'
            )

        # Add grid, lines, and labels
        plt.axhline(0, color='black', linestyle='--', linewidth=1, label='y=0')  # Horizontal line
        plt.axvline(0, color='black', linestyle='--', linewidth=1, label='x=0')  # Vertical line
        plt.title(f"Movement Comparison: {selected_pitcher} vs. League Average", fontsize=16)
        plt.xlabel("Horizontal Break (HB)", fontsize=14)
        plt.ylabel("Induced Vertical Break (iVB)", fontsize=14)
        plt.xlim(-30, 30)
        plt.ylim(-30, 30)
        plt.legend(loc='upper right')
        plt.grid(True)

        # Display the plot in Streamlit
        st.pyplot(plt)
