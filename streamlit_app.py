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


from config_parser import postgres_conn
from src.stores.water_levels_store import clear_water_levels_store_cache, load_water_levels_store

st.set_page_config(page_title="Bonsai Monitor", layout="wide", page_icon="🌲")

STORE_SESSION_KEY = "water_levels_store"

if st.button("Refresh data"):
    clear_water_levels_store_cache()
    st.session_state.pop(STORE_SESSION_KEY, None)

if STORE_SESSION_KEY not in st.session_state:
    st.session_state[STORE_SESSION_KEY] = load_water_levels_store(postgres_conn)

store = st.session_state[STORE_SESSION_KEY]

from src.components.moisture_card import moisture_card
moisture_card(store.latest_water_level, store.latest_battery_level, store.latest_measured_time)

from src.components.levels_chart import levels_chart
levels_chart(levels_array=store.recent_levels)

store.all_levels
