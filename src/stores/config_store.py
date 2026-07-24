from __future__ import annotations

from dataclasses import dataclass

import requests
import streamlit as st

DEFAULT_MIN_WATER_LEVEL = 20
DEFAULT_MIN_BATTERY_LEVEL = 20
DEFAULT_MAX_WATER_LEVEL = 100
DEFAULT_MAX_BATTERY_LEVEL = 100
DEFAULT_WATER_BURST_TIME = 30
DEFAULT_WATER_SETTLING_TIME = 30
DEFAULT_DEEPSLEEP_TIME = 15 * 60
DEFAULT_MAX_ALIVE_TIME = 5 * 60 * 1000

KEY_ALL_CONFIGS = "all_configs"

@dataclass(frozen=True)
class ConfigStoreState:
    min_water_level: int
    min_battery_level: int
    max_water_level: int
    max_battery_level: int
    water_burst_time: int
    water_settling_time: int
    deepsleep_time: int
    max_alive_time: int


def _default_config_values() -> dict[str, int]:
    return {
        "min_water_level": DEFAULT_MIN_WATER_LEVEL,
        "min_battery_level": DEFAULT_MIN_BATTERY_LEVEL,
        "max_water_level": DEFAULT_MAX_WATER_LEVEL,
        "max_battery_level": DEFAULT_MAX_BATTERY_LEVEL,
        "water_burst_time": DEFAULT_WATER_BURST_TIME,
        "water_settling_time": DEFAULT_WATER_SETTLING_TIME,
        "deepsleep_time": DEFAULT_DEEPSLEEP_TIME,
        "max_alive_time": DEFAULT_MAX_ALIVE_TIME,
    }


def set_store_default_values() -> None:
    for key, default_value in _default_config_values().items():
        st.session_state[key] = default_value
        
@st.cache_data(show_spinner=True, ttl=60)
def fetch_db_config_values() -> None:
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
            return

        st.session_state[KEY_ALL_CONFIGS] = payload
                
        for key in _default_config_values():
            value = payload.get(key)
            if value is not None:
                st.session_state[key] = int(value)
        
    except requests.RequestException as e:
        print(f"Error fetching config values from API: {e}")
    except (TypeError, ValueError) as e:
        print(f"Invalid config values returned by API: {e}")   
        
def load_configs_from_state() -> None:    
    for key in _default_config_values():
        all_configs = st.session_state.get(KEY_ALL_CONFIGS, {})
        value = all_configs.get(key)
        if value is not None:
            st.session_state[key] = int(value)
        

def load_config_store() -> ConfigStoreState:
    fetch_db_config_values()
    return ConfigStoreState(
        min_water_level=int(st.session_state["min_water_level"]),
        min_battery_level=int(st.session_state["min_battery_level"]),
        max_water_level=int(st.session_state["max_water_level"]),
        max_battery_level=int(st.session_state["max_battery_level"]),
        water_burst_time=int(st.session_state["water_burst_time"]),
        water_settling_time=int(st.session_state["water_settling_time"]),
        deepsleep_time=int(st.session_state["deepsleep_time"]),
        max_alive_time=int(st.session_state["max_alive_time"]),
    )
    
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
