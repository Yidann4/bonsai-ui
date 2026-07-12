"""
# My first app
Here's our first attempt at using data to create a table:

Run with: streamlit run streamlit_app.py
Note: Only python 3.13 installation has streamlit
Also requires pip installing streamlit-echarts

To activate the conda environment with python 3.13 do conda activate py313. (You can see conda environments with conda env list)


"""


# pip-compile --upgrade requirements.in
# 

import sys
sys.path.append(".streamlit")

import streamlit as st
import pandas as pd


from config_parser import postgres_conn
from src.components.vertical_progress_bar import render_vertical_progress_bar

st.set_page_config(page_title="Bonsai Monitor", layout="wide", page_icon="🌲")





remoteconn = st.connection(postgres_conn, type="sql")

# Perform query.
query = 'SELECT * FROM public.water_levels ORDER BY id DESC LIMIT 100;'
remote_water_levels = remoteconn.query(query, ttl="0")
remote_water_levels['aest_time'] = pd.to_datetime(remote_water_levels['inserted_at']).dt.tz_localize('UTC').dt.tz_convert('Australia/Brisbane')
latest_water_level = remote_water_levels['level'].iloc[0]
latest_battery_level = remote_water_levels['battery_level'].iloc[0]


## line chart
last_day = pd.Timestamp.now(tz="UTC").tz_convert(None) - pd.Timedelta(days=1)
recent_water_levels = remote_water_levels[remote_water_levels['inserted_at'] >= last_day]
st.line_chart(x='aest_time', y=['level', 'battery_level'], data=recent_water_levels, x_label="Time (AEST)", y_label="Level / Battery Level", color=['blue', 'red'])

remote_water_levels

render_vertical_progress_bar(latest_water_level)
