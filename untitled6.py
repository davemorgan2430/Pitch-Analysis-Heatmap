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
required_columns = ['pitch_type', 'player_name', 'arm_angle', 'HB', 'iVB']
if not all(col in df.columns for col in required_columns):
    st.error(
        "The uploaded file is missing required columns. Ensure it contains: "
        "pitch_type, player_name, arm_angle, HB, iVB."
    )
    st.stop()

# Step 1: Select pitch type
selected_pitch = st.selectbox("Select the pitch type", df['pitch_type'].unique())

# Filter DataFrame based on selected pitch type
pitch_filtered_df = df[df['pitch_type'] == selected_pitch]

# Step 2: Select pitcher
available_pitchers = pitch_filtered_df['player_name'].unique()
selected_pitcher = st.selectbox("Select a pitcher", available_pitchers)

# Filter data for the selected pitcher
pitcher_data = pitch_filtered_df[pitch_filtered_df['player_name'] == selected_pitcher]

if pitcher_data.empty:
    st.write("No data found for the selected combination.")
else:
    # Calculate the selected pitcher's average arm angle
    avg_arm_angle = pitcher_data['arm_angle'].mean()
    st.write(f"Average Arm Angle for {selected_pitcher}: {avg_arm_angle:.2f}°")

    # Step 3: Automatically filter all data for pitchers with the same arm angle
    arm_angle_filtered_df = pitch_filtered_df[
        pitch_filtered_df['arm_angle'] == avg_arm_angle
    ]

    if arm_angle_filtered_df.empty:
        st.write(f"No pitchers found with an arm angle of {avg_arm_angle:.2f}°.")
    else:
        st.write(f"Found {len(arm_angle_filtered_df)} pitches from pitchers with the same arm angle.")

        # Create a KDE heatmap with all filtered data
        plt.figure(figsize=(10, 8))
        sns.kdeplot(
            data=arm_angle_filtered_df,
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
        plt.axhline(0, color='black', linestyle='--', linewidth=1)
        plt.axvline(0, color='black', linestyle='--', linewidth=1)

        # Set labels and title
        plt.title(
            f"{selected_pitch} Heatmap | Arm Angle: {avg_arm_angle:.2f}°",
            fontsize=16
        )
        plt.xlabel("Horizontal Break (HB)", fontsize=14)
        plt.ylabel("Induced Vertical Break (iVB)", fontsize=14)
        plt.legend()

        # Display the plot in Streamlit
        st.pyplot(plt)

