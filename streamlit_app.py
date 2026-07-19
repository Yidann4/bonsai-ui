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

st.set_page_config(page_title="Bonsai Monitor", layout="wide", page_icon="🌲")

wallpaper_path = app_root / "images" / "wallpaper_v2.png"
wallpaper_b64 = base64.b64encode(wallpaper_path.read_bytes()).decode("utf-8")

page_bg_img = f'''
<style> [data-testid="stAppViewContainer"], .stApp {{ background-image: url("data:image/png;base64,{wallpaper_b64}"); background-size: cover; background-position: center; background-repeat: no-repeat; }} [data-testid="stHeader"], [data-testid="stToolbar"] {{ background: transparent; }} </style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)


STORE_SESSION_KEY = "water_levels_store"

if st.button("Refresh data"):
    clear_water_levels_store_cache()
    st.session_state.pop(STORE_SESSION_KEY, None)

st.session_state[STORE_SESSION_KEY] = load_water_levels_store(postgres_conn)
store = st.session_state[STORE_SESSION_KEY]

store = st.session_state[STORE_SESSION_KEY]

from src.components.moisture_card import moisture_card
moisture_card(store.latest_water_level, store.latest_battery_level, store.latest_measured_time)

from src.components.levels_chart import levels_chart
levels_chart(levels_array=store.recent_levels)
