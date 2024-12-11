import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

# App title
st.title("Pitch Analysis Application")

# Load the data
file_id = "1lUKCYNnWi02NA6ICynEGrjsH1uqJeSH7"  # Replace with your file ID
url = f"https://drive.google.com/uc?id={file_id}"

try:
    df = pd.read_csv(url)
    st.success("Data loaded successfully!")
except Exception as e:
    st.error("Error loading the data.")
    st.error(e)
    st.stop()

# Validate required columns
required_columns = ['pitch_type', 'player_name', 'arm_angle', 'HB', 'iVB', 'p_throws', 'release_speed', 
                    'release_spin_rate', 'estimated_woba_using_speedangle', 'release_extension']
if not all(col in df.columns for col in required_columns):
    st.error("The dataset is missing required columns.")
    st.stop()

# Create tabs
tab1, tab2, tab3 = st.tabs(["Pitch Analysis Heatmap", "Create a Pitcher", "Pitcher Movements vs League Average"])

# Tab 1: Pitch Analysis Heatmap
with tab1:
    st.header("Pitch Analysis Heatmap")
    selected_pitch = st.selectbox("Select the pitch type", df['pitch_type'].unique())
    selected_handedness = st.selectbox("Select Handedness", df['p_throws'].unique())
    filtered_df = df[(df['pitch_type'] == selected_pitch) & (df['p_throws'] == selected_handedness)]
    
    if not filtered_df.empty:
        plt.figure(figsize=(10, 8))
        sns.kdeplot(data=filtered_df, x="HB", y="iVB", fill=True, cmap="viridis", levels=10, cbar=True)
        plt.title(f"{selected_pitch} Heatmap | Handedness: {selected_handedness}")
        st.pyplot(plt)
    else:
        st.warning("No data available for the selected pitch type and handedness.")

# Tab 2: Create a Pitcher
with tab2:
    st.header("Create a Pitcher")
    pitch_type = st.selectbox("Select Pitch Type", df['pitch_type'].unique())
    handedness = st.selectbox("Select Handedness", df['p_throws'].unique())
    arm_angle_range = st.slider("Select Arm Angle Range", float(df['arm_angle'].min()), float(df['arm_angle'].max()), (float(df['arm_angle'].min()), float(df['arm_angle'].max())))
    ivb = st.number_input("Enter iVB (Induced Vertical Break)", value=0.0)
    hb = st.number_input("Enter HB (Horizontal Break)", value=0.0)
    
    comparison_df = df[
        (df['pitch_type'] == pitch_type) & 
        (df['p_throws'] == handedness) & 
        (df['arm_angle'] >= arm_angle_range[0]) & 
        (df['arm_angle'] <= arm_angle_range[1])
    ]
    
    if not comparison_df.empty:
        st.write("Heatmap comparing your input pitch against league average.")
        plt.figure(figsize=(10, 8))
        sns.kdeplot(data=comparison_df, x="HB", y="iVB", fill=True, cmap="viridis", levels=10, cbar=True)
        plt.scatter(hb, ivb, color="red", label="Your Pitch", s=100)
        plt.legend()
        plt.title(f"{pitch_type} Comparison | Arm Angle Range: {arm_angle_range}")
        st.pyplot(plt)
    else:
        st.warning("No matching data for the selected criteria.")

# Tab 3: Pitcher Movements vs League Average
with tab3:
    st.header("Pitcher Movements vs League Average")
    pitcher_name = st.selectbox("Select a pitcher for comparison", df['player_name'].unique())
    pitcher_df = df[df['player_name'] == pitcher_name]
    
    if not pitcher_df.empty:
        plt.figure(figsize=(12, 10))
        for pitch in pitcher_df['pitch_type'].unique():
            pitch_data = pitcher_df[pitcher_df['pitch_type'] == pitch]
            league_data = df[(df['pitch_type'] == pitch) & (df['p_throws'] == pitcher_df['p_throws'].iloc[0])]
            
            sns.kdeplot(data=league_data, x="HB", y="iVB", fill=True, cmap="viridis", levels=10, alpha=0.5, label=f"League Avg: {pitch}")
            plt.scatter(pitch_data['HB'].mean(), pitch_data['iVB'].mean(), color="red", s=100, label=f"{pitcher_name}: {pitch}")
        
        plt.axhline(0, color="black", linestyle="--", linewidth=1)
        plt.axvline(0, color="black", linestyle="--", linewidth=1)
        plt.legend()
        plt.title(f"Pitcher Movements: {pitcher_name} vs League Average")
        plt.xlabel("Horizontal Break (HB)")
        plt.ylabel("Induced Vertical Break (iVB)")
        st.pyplot(plt)
    else:
        st.warning("No data available for the selected pitcher.")
