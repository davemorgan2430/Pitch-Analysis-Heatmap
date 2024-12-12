# Section: Combined Analysis
st.header("Pitch Analysis and Movement Comparison")

# Dropdown menu for selecting analysis type
analysis_type = st.selectbox(
    "Select Analysis Type",
    ["Pitch Analysis Heatmap", "Pitcher Movements vs League Average"]
)

if analysis_type == "Pitch Analysis Heatmap":
    # Pitch Analysis Heatmap Code
    st.subheader("Pitch Analysis Heatmap")
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
        avg_velocity = pitcher_data['release_speed'].mean()
        avg_spin_rate = pitcher_data['release_spin_rate'].mean()
        avg_woba = pitcher_data['estimated_woba_using_speedangle'].mean()
        avg_extension = pitcher_data['release_extension'].mean()
        avg_iVB = pitcher_data['iVB'].mean()
        avg_HB = pitcher_data['HB'].mean()

        st.sidebar.header(f"{selected_pitcher} - Pitch Stats")
        st.sidebar.write(f"**Pitch Type:** {selected_pitch}")
        st.sidebar.write(f"**Average Arm Angle:** {avg_arm_angle:.2f}°")
        st.sidebar.write(f"**Average Velocity:** {avg_velocity:.1f} mph")
        st.sidebar.write(f"**Average Spin Rate:** {avg_spin_rate:.1f} rpm")
        st.sidebar.write(f"**Average wOBA:** {avg_woba:.3f}")
        st.sidebar.write(f"**Average Extension:** {avg_extension:.2f} ft")
        st.sidebar.write(f"**Average iVB:** {avg_iVB:.2f} in")
        st.sidebar.write(f"**Average HB:** {avg_HB:.2f} in")

        input_arm_angle = st.number_input(
            "Enter an arm angle to filter the data (default is the pitcher's average):",
            min_value=float(df['arm_angle'].min()),
            max_value=float(df['arm_angle'].max()),
            value=float(avg_arm_angle),
        )

        filtered_df = pitch_filtered_df[
            (pitch_filtered_df['arm_angle'] == input_arm_angle) &
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
            plt.title(f"{selected_pitch} Heatmap | Arm Angle: {input_arm_angle:.2f}°", fontsize=16)
            plt.xlabel("Horizontal Break (HB)", fontsize=14)
            plt.ylabel("Induced Vertical Break (iVB)", fontsize=14)
            plt.xlim(-30, 30)
            plt.ylim(-30, 30)
            plt.legend()
            st.pyplot(plt)

elif analysis_type == "Pitcher Movements vs League Average":
    # Pitcher Movements vs League Average Code
    st.subheader("Pitcher Movements vs League Average")
    pitcher_name = st.selectbox("Select a pitcher for comparison", df['player_name'].unique())
    pitcher_df = df[df['player_name'] == pitcher_name]

    if not pitcher_df.empty:
        league_data = df[df['p_throws'] == pitcher_df['p_throws'].iloc[0]]
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
                label=f"{pitch_type} (League Avg)",
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
        plt.legend(title="Pitch Types")
        st.pyplot(plt)
    else:
        st.warning("No data available for the selected pitcher.")


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

# Section: Create a Pitcher with Combined Plot
st.header("Create a Pitcher - Combined Plot for Multiple Pitches")

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
