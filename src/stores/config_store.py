from __future__ import annotations

from dataclasses import asdict
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

KEY_HAS_LOADED = "has_loaded_config_store"
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


def _coerce_int(value: object, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _stored_configs_dict() -> dict[str, object]:
    stored = st.session_state.get(KEY_ALL_CONFIGS, {})
    return stored if isinstance(stored, dict) else {}


def _resolve_config_value(key: str, default: int) -> int:
    if key in st.session_state:
        return _coerce_int(st.session_state.get(key), default)
    return _coerce_int(_stored_configs_dict().get(key, default), default)

def config_object_from_state() -> ConfigStoreState:
    return ConfigStoreState(
        min_water_level=_resolve_config_value("min_water_level", DEFAULT_MIN_WATER_LEVEL),
        min_battery_level=_resolve_config_value("min_battery_level", DEFAULT_MIN_BATTERY_LEVEL),
        max_water_level=_resolve_config_value("max_water_level", DEFAULT_MAX_WATER_LEVEL),
        max_battery_level=_resolve_config_value("max_battery_level", DEFAULT_MAX_BATTERY_LEVEL),
        watering_level_start=_resolve_config_value("watering_level_start", DEFAULT_WATERING_LEVEL_START),
        watering_level_end=_resolve_config_value("watering_level_end", DEFAULT_WATERING_LEVEL_END),
        water_burst_time=_resolve_config_value("water_burst_time", DEFAULT_WATER_BURST_TIME),
        water_settling_time=_resolve_config_value("water_settling_time", DEFAULT_WATER_SETTLING_TIME),
        deepsleep_time=_resolve_config_value("deepsleep_time", DEFAULT_DEEPSLEEP_TIME),
        max_alive_time=_resolve_config_value("max_alive_time", DEFAULT_MAX_ALIVE_TIME),
    )

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
    st.session_state[KEY_ALL_CONFIGS] = asdict(default_configs)
        
@st.cache_data(show_spinner=True, ttl=60)
def fetch_db_config_values() -> ConfigStoreState:
    """Fetches config values from the remote API and updates session state."""
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
        st.session_state[KEY_HAS_LOADED] = True
        
        return ConfigStoreState(
            min_water_level=_coerce_int(payload.get("min_water_level", DEFAULT_MIN_WATER_LEVEL), DEFAULT_MIN_WATER_LEVEL),
            min_battery_level=_coerce_int(payload.get("min_battery_level", DEFAULT_MIN_BATTERY_LEVEL), DEFAULT_MIN_BATTERY_LEVEL),
            max_water_level=_coerce_int(payload.get("max_water_level", DEFAULT_MAX_WATER_LEVEL), DEFAULT_MAX_WATER_LEVEL),
            max_battery_level=_coerce_int(payload.get("max_battery_level", DEFAULT_MAX_BATTERY_LEVEL), DEFAULT_MAX_BATTERY_LEVEL),
            watering_level_start=_coerce_int(payload.get("watering_level_start", DEFAULT_WATERING_LEVEL_START), DEFAULT_WATERING_LEVEL_START),
            watering_level_end=_coerce_int(payload.get("watering_level_end", DEFAULT_WATERING_LEVEL_END), DEFAULT_WATERING_LEVEL_END),
            water_burst_time=_coerce_int(payload.get("water_burst_time", DEFAULT_WATER_BURST_TIME), DEFAULT_WATER_BURST_TIME),
            water_settling_time=_coerce_int(payload.get("water_settling_time", DEFAULT_WATER_SETTLING_TIME), DEFAULT_WATER_SETTLING_TIME),
            deepsleep_time=_coerce_int(payload.get("deepsleep_time", DEFAULT_DEEPSLEEP_TIME), DEFAULT_DEEPSLEEP_TIME),
            max_alive_time=_coerce_int(payload.get("max_alive_time", DEFAULT_MAX_ALIVE_TIME), DEFAULT_MAX_ALIVE_TIME),
        )
        
    except requests.RequestException as e:
        print(f"Error fetching config values from API: {e}")
    except (TypeError, ValueError) as e:
        print(f"Invalid config values returned by API: {e}")

    st.session_state[KEY_HAS_LOADED] = False
    return config_object_from_state()

def load_config_store() -> ConfigStoreState:
    """Sets config values in session state from the remote API."""
    
    if st.session_state.get(KEY_HAS_LOADED, False):
        # Rehydrate from current session state (or last persisted payload).
        configs = config_object_from_state()
        print(f"Water level start config: {configs.watering_level_start}")
        print("Using cached config values from session state.")
    else:
        # First load, or after save where cache was explicitly invalidated.
        configs = fetch_db_config_values()
        print("Fetched config values from API and updated session state.")
    
    set_state_from_config_store(configs)
    
    print(f"State water_level_start after load_config_store: {st.session_state.get('watering_level_start')}")
        
    return configs
    
def push_config_updates() -> None:
    """Pushes updated config values to the remote API."""
    base_url = st.secrets.get("remote_api_url", "")
    url = f"{base_url}/update_params"

    payload = {
        key: st.session_state[key]
        for key in ConfigStoreState.__dataclass_fields__
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        # Keep cancel restore source in sync with latest persisted values.
        st.session_state[KEY_ALL_CONFIGS] = payload
        
        # cause cached db query to reload next time it's called, so that the latest values are fetched from the API
        fetch_db_config_values.clear()
        st.session_state[KEY_HAS_LOADED] = False
        
        print("Config values successfully pushed to API.")
    except requests.RequestException as e:
        print(f"Error pushing config values to API: {e}")
