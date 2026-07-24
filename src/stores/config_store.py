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
DEFAULT_MAXIMUM_ALIVE_TIME = 5 * 60 * 1000


@dataclass(frozen=True)
class ConfigStoreState:
    min_water_level: int
    min_battery_level: int
    max_water_level: int
    max_battery_level: int
    water_burst_time: int
    water_settling_time: int
    deepsleep_time: int
    maximum_alive_time: int


def _default_config_values() -> dict[str, int]:
    return {
        "min_water_level": DEFAULT_MIN_WATER_LEVEL,
        "min_battery_level": DEFAULT_MIN_BATTERY_LEVEL,
        "max_water_level": DEFAULT_MAX_WATER_LEVEL,
        "max_battery_level": DEFAULT_MAX_BATTERY_LEVEL,
        "water_burst_time": DEFAULT_WATER_BURST_TIME,
        "water_settling_time": DEFAULT_WATER_SETTLING_TIME,
        "deepsleep_time": DEFAULT_DEEPSLEEP_TIME,
        "maximum_alive_time": DEFAULT_MAXIMUM_ALIVE_TIME,
    }


def set_store_default_values() -> None:
    for key, default_value in _default_config_values().items():
        st.session_state.setdefault(key, default_value)
        
@st.cache_data(show_spinner=True, ttl=60)
def fetch_db_config_values() -> None:
    """Fetches config values from the remote API and updates session state."""
    base_url = st.secrets.get("remote_api_url", "")

    url = "http://localhost:4000/api/fetch_params"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        payload = data.get("data", data) if isinstance(data, dict) else {}
        if not isinstance(payload, dict):
            print(f"Unexpected config payload type: {type(payload).__name__}")
            return

        for key in _default_config_values():
            value = payload.get(key)
            if value is not None:
                st.session_state[key] = int(value)
        
    except requests.RequestException as e:
        print(f"Error fetching config values from API: {e}")
    except (TypeError, ValueError) as e:
        print(f"Invalid config values returned by API: {e}")   

def load_config_store() -> ConfigStoreState:
    set_store_default_values()
    fetch_db_config_values()
    return ConfigStoreState(
        min_water_level=int(st.session_state["min_water_level"]),
        min_battery_level=int(st.session_state["min_battery_level"]),
        max_water_level=int(st.session_state["max_water_level"]),
        max_battery_level=int(st.session_state["max_battery_level"]),
        water_burst_time=int(st.session_state["water_burst_time"]),
        water_settling_time=int(st.session_state["water_settling_time"]),
        deepsleep_time=int(st.session_state["deepsleep_time"]),
        maximum_alive_time=int(st.session_state["maximum_alive_time"]),
    )
