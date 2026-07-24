from __future__ import annotations

from dataclasses import dataclass

import requests
import streamlit as st

DEFAULT_MIN_WATER_LEVEL = 1000
DEFAULT_MIN_BATTERY_LEVEL = 1000
DEFAULT_MAX_WATER_LEVEL = 3000
DEFAULT_MAX_BATTERY_LEVEL = 3000

DEFAULT_WATERING_LEVEL_START = 1500
DEFAULT_WATERING_LEVEL_END = 2000
DEFAULT_WATER_BURST_TIME = 3
DEFAULT_WATER_SETTLING_TIME = 5

DEFAULT_DEEPSLEEP_TIME = 15 * 60
DEFAULT_MAX_ALIVE_TIME = 5 * 60

KEY_ALL_CONFIGS = "all_configs"

@dataclass(frozen=True)
class ConfigStoreState:
    min_water_level: int
    min_battery_level: int
    max_water_level: int
    max_battery_level: int
    watering_level_start: int
    watering_level_end: int
    water_burst_time: int
    water_settling_time: int
    deepsleep_time: int
    max_alive_time: int

def set_state_from_config_store(configs: ConfigStoreState) -> None:
    st.session_state["min_water_level"] = configs.min_water_level
    st.session_state["min_battery_level"] = configs.min_battery_level
    st.session_state["max_water_level"] = configs.max_water_level
    st.session_state["max_battery_level"] = configs.max_battery_level
    st.session_state["watering_level_start"] = configs.watering_level_start
    st.session_state["watering_level_end"] = configs.watering_level_end
    st.session_state["water_burst_time"] = configs.water_burst_time
    st.session_state["water_settling_time"] = configs.water_settling_time
    st.session_state["deepsleep_time"] = configs.deepsleep_time
    st.session_state["max_alive_time"] = configs.max_alive_time
    return None

def _default_config_values() -> ConfigStoreState:
    return ConfigStoreState(
        min_water_level=DEFAULT_MIN_WATER_LEVEL,
        min_battery_level=DEFAULT_MIN_BATTERY_LEVEL,
        max_water_level=DEFAULT_MAX_WATER_LEVEL,
        max_battery_level=DEFAULT_MAX_BATTERY_LEVEL,
        watering_level_start=DEFAULT_WATERING_LEVEL_START,
        watering_level_end=DEFAULT_WATERING_LEVEL_END,
        water_burst_time=DEFAULT_WATER_BURST_TIME,
        water_settling_time=DEFAULT_WATER_SETTLING_TIME,
        deepsleep_time=DEFAULT_DEEPSLEEP_TIME,
        max_alive_time=DEFAULT_MAX_ALIVE_TIME,
    )

def set_store_default_values() -> None:
    default_configs = _default_config_values()
    set_state_from_config_store(default_configs)
        
@st.cache_data(show_spinner=True, ttl=60)
def fetch_db_config_values() -> ConfigStoreState:
    """Fetches config values from the remote API and updates session state."""
    set_store_default_values()
    
    base_url = st.secrets.get("remote_api_url", "")
    url = f"{base_url}/fetch_params"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        payload = data.get("data", data) if isinstance(data, dict) else {}
        if not isinstance(payload, dict):
            print(f"Unexpected config payload type: {type(payload).__name__}")
            return _default_config_values()

        st.session_state[KEY_ALL_CONFIGS] = payload
        
        return ConfigStoreState(
            min_water_level=int(payload.get("min_water_level", DEFAULT_MIN_WATER_LEVEL)),
            min_battery_level=int(payload.get("min_battery_level", DEFAULT_MIN_BATTERY_LEVEL)),
            max_water_level=int(payload.get("max_water_level", DEFAULT_MAX_WATER_LEVEL)),
            max_battery_level=int(payload.get("max_battery_level", DEFAULT_MAX_BATTERY_LEVEL)),
            watering_level_start=int(payload.get("watering_level_start", DEFAULT_WATERING_LEVEL_START)),
            watering_level_end=int(payload.get("watering_level_end", DEFAULT_WATERING_LEVEL_END)),
            water_burst_time=int(payload.get("water_burst_time", DEFAULT_WATER_BURST_TIME)),
            water_settling_time=int(payload.get("water_settling_time", DEFAULT_WATER_SETTLING_TIME)),
            deepsleep_time=int(payload.get("deepsleep_time", DEFAULT_DEEPSLEEP_TIME)),
            max_alive_time=int(payload.get("max_alive_time", DEFAULT_MAX_ALIVE_TIME)),
        )
        
    except requests.RequestException as e:
        print(f"Error fetching config values from API: {e}")
    except (TypeError, ValueError) as e:
        print(f"Invalid config values returned by API: {e}")   

def load_config_store() -> ConfigStoreState:
    """Sets config values in session state from the remote API."""
    configs = fetch_db_config_values()
    set_state_from_config_store(configs)
    return configs
    
def push_config_updates() -> None:
    """Pushes updated config values to the remote API."""
    base_url = st.secrets.get("remote_api_url", "")
    url = f"{base_url}/update_params"

    payload = {key: st.session_state[key] for key in _default_config_values()}

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        # Keep cancel restore source in sync with latest persisted values.
        st.session_state[KEY_ALL_CONFIGS] = payload
        print("Config values successfully pushed to API.")
    except requests.RequestException as e:
        print(f"Error pushing config values to API: {e}")
