"""
# My first app
Here's our first attempt at using data to create a table:
"""
import sys
sys.path.append(".streamlit")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


from config_parser import postgres_conn

st.image(image="./images/bonsai_pcb.jpeg", caption="Bonsai PCB")

remoteconn = st.connection(postgres_conn, type="sql")

# Perform query.
query = 'SELECT * FROM public.water_levels ORDER BY id DESC LIMIT 100;'
remote_water_levels = remoteconn.query(query, ttl="0")
remote_water_levels['aest_time'] = pd.to_datetime(remote_water_levels['inserted_at']).dt.tz_localize('UTC').dt.tz_convert('Australia/Brisbane')
latest_water_level = remote_water_levels['level'].iloc[0]
latest_battery_level = remote_water_levels['battery_level'].iloc[0]

col1, col2 = st.columns(2)

with col1:
    # Water level progress plot
    x = latest_water_level
    if x > 1:
        x = x / 100
    fig, ax = plt.subplots(figsize=(0.5, 0.75))
    glass = plt.Rectangle((0.25, 0), 0.5, 1, fill=False, linewidth=2, edgecolor='blue')
    ax.add_patch(glass)
    water = plt.Rectangle((0.25, 0), 0.5, x, color='blue', alpha=0.5)
    ax.add_patch(water)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.text(0.5, 1.02, f"{latest_water_level:.1f}%", ha='center', va='bottom', fontsize=7)
    st.pyplot(fig, use_container_width=False)

with col2:
    # Battery level progress plot
    x = latest_battery_level
    if x > 1:
        x = x / 100
    fig, ax = plt.subplots(figsize=(0.5, 0.75))
    glass = plt.Rectangle((0.25, 0), 0.5, 1, fill=False, linewidth=2, edgecolor='red')
    ax.add_patch(glass)
    water = plt.Rectangle((0.25, 0), 0.5, x, color='red', alpha=0.5)
    ax.add_patch(water)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.text(0.5, 1.02, f"{latest_battery_level:.1f}%", ha='center', va='bottom', fontsize=7)
    st.pyplot(fig, use_container_width=False)



## line chart
last_day = pd.Timestamp.now(tz="UTC").tz_convert(None) - pd.Timedelta(days=1)
recent_water_levels = remote_water_levels[remote_water_levels['inserted_at'] >= last_day]
st.line_chart(x='aest_time', y=['level', 'battery_level'], data=recent_water_levels, x_label="Time (AEST)", y_label="Level / Battery Level", color=['blue', 'red'])

remote_water_levels
