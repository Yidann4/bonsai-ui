import sys
import base64
from pathlib import Path

# look at bonsai-ui/src before looking at streamlit hosted mount/src
app_root = Path(__file__).resolve().parent
if str(app_root) not in sys.path:
    sys.path.insert(0, str(app_root))

sys.path.append(".streamlit")

import streamlit as st


from config_parser import postgres_conn
from src.stores.water_levels_store import clear_water_levels_store_cache, load_water_levels_store
from src.components.config_modal import config_modal

from src.stores.user_store import fetch_users, set_signed_in_user
fetch_users()

st.set_page_config(page_title="Bonsai Monitor", layout="wide", page_icon="🌲")

wallpaper_path = app_root / "images" / "wallpaper_v2.png"
wallpaper_b64 = base64.b64encode(wallpaper_path.read_bytes()).decode("utf-8")

page_bg_img = f'''
<style> [data-testid="stAppViewContainer"], .stApp {{ background-image: url("data:image/png;base64,{wallpaper_b64}"); background-size: cover; background-position: center; background-repeat: no-repeat; }} [data-testid="stHeader"], [data-testid="stToolbar"] {{ background: transparent; }} </style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

STORE_SESSION_KEY = "water_levels_store"
st.session_state["postgres_connection_name"] = postgres_conn

st.session_state[STORE_SESSION_KEY] = load_water_levels_store()
store = st.session_state[STORE_SESSION_KEY]

with st.container(horizontal=True, horizontal_alignment="left", vertical_alignment="bottom"):
    if st.button("Refresh data"):
        with st.spinner("Refreshing data..."):
            clear_water_levels_store_cache()
            st.session_state.pop(STORE_SESSION_KEY, None)
        st.rerun()

    open_config_modal = st.button("Open config modal")
    
    st.text_input(
        "username",
        max_chars=20,
        key="username_input",
        on_change=set_signed_in_user,
        type="password",
        width=300,
    )    
    
config_modal(open=open_config_modal)

from src.components.moisture_card import moisture_card
moisture_card(store.latest_water_level, store.latest_battery_level, store.latest_measured_time, store.latest_watered_time, store.latest_bucket_stocked)

from src.components.levels_chart import levels_chart
levels_chart(levels_array=store.recent_levels)

