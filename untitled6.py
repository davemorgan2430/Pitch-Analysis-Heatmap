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
    st.write(df.head())  # Display the first few rows
except Exception as e:
    st.error("Error loading the file. Please check the file ID or format.")
    st.error(e)
    st.stop()

# Streamlit user inputs for filtering
selected_pitch = st.selectbox("Select the pitch type", df['pitch_type'].unique())

# Ask for the arm angle range (manual input for minimum and maximum values)
min_arm_angle = st.number_input("Enter the minimum arm angle", min_value=float(df['arm_angle'].min()), 
                                max_value=float(df['arm_angle'].max()), value=float(df['arm_angle'].min()))
max_arm_angle = st.number_input("Enter the maximum arm angle", min_value=float(df['arm_angle'].min()), 
                                max_value=float(df['arm_angle'].max()), value=float(df['arm_angle'].max()))

# Ask for handedness
selected_handedness = st.selectbox(
    "Select handedness",
    df['p_throws'].unique()
)

# Filter the DataFrame based on user input
filtered_df = df[
    (df['pitch_type'] == selected_pitch) &
    (df['arm_angle'] >= arm_angle_range[0]) &
    (df['arm_angle'] <= arm_angle_range[1]) &
    (df['p_throws'] == selected_handedness)
]

# Check if there are pitchers in the filtered range
if filtered_df.empty:
    st.warning("No data matches the selected criteria. Please adjust your filters.")
    st.stop()

# List pitchers in the filtered range
pitchers_in_range = filtered_df['player_name'].unique()
st.write("Pitchers in the selected arm angle range:")
st.write(", ".join(pitchers_in_range))

# Ask the user to select a pitcher
selected_pitcher = st.selectbox("Select a pitcher to highlight", pitchers_in_range)

# Filter the data for the selected pitcher and calculate average HB and iVB
pitcher_data = filtered_df[filtered_df['player_name'] == selected_pitcher]
average_hb = pitcher_data['HB'].mean()
average_ivb = pitcher_data['iVB'].mean()

# Create a KDE plot with iVB and HB
plt.figure(figsize=(10, 8))

# Kernel Density Estimate plot
sns.kdeplot(
    data=filtered_df,
    x='HB',
    y='iVB',
    fill=True,
    cmap='viridis',  # You can change this to any colormap you prefer
    thresh=0.05,     # Threshold for contours to appear
    levels=10,       # Number of contour levels
    cbar=True,       # Add color bar
)

# Add lines at x=0 and y=0
plt.axhline(0, color='black', linestyle='--', linewidth=1, label='y=0')  # Horizontal line
plt.axvline(0, color='black', linestyle='--', linewidth=1, label='x=0')  # Vertical line

# Highlight the selected pitcher's average data point
plt.scatter(
    average_hb,
    average_ivb,
    color='orange',
    s=100,
    label=f"{selected_pitcher} (Avg HB: {average_hb:.2f}, Avg iVB: {average_ivb:.2f})"
)

# Set labels and title
plt.title(f"{selected_pitch} | {selected_handedness}-handed | Arm Angle: {arm_angle_range[0]:.1f}° - {arm_angle_range[1]:.1f}°", fontsize=16)
plt.xlabel("Horizontal Break (HB)", fontsize=14)
plt.ylabel("Induced Vertical Break (iVB)", fontsize=14)

# Set x and y axis limits
plt.xlim(-30, 30)
plt.ylim(-30, 30)

# Display the plot in Streamlit
st.pyplot(plt)
