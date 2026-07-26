from __future__ import annotations

from dataclasses import dataclass
import logging

import pandas as pd
import requests
import streamlit as st

CONF_DEFAULT_LOOKBACK_PERIOD = pd.Timedelta(days=1)
CONF_MAX_FETCH_COUNT = 7200  # 24 * 10 * 30 (30 days)

LOOKBACK_KEY = "lookback_period"
INITIALIZED_KEY = "water_levels_initialized"

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WaterLevelsStoreState:
    all_levels: pd.DataFrame
    recent_levels: pd.DataFrame  # based on lookback
    latest_water_level: float
    latest_battery_level: float
    latest_measured_time: str
    latest_watered_time: str
    latest_bucket_stocked: str


def _empty_levels_frame() -> pd.DataFrame:
    # Keep expected chart/store columns present even when DB is unavailable.
    return pd.DataFrame(
        columns=[
            "id",
            "level",
            "battery_level",
            "has_watered",
            "inserted_at",
            "updated_at",
            "aest_time",
        ]
    )

def _prepare_levels_frame(levels: pd.DataFrame) -> pd.DataFrame:
    prepared = levels.copy()
    prepared["inserted_at"] = pd.to_datetime(prepared["inserted_at"], utc=True)
    prepared["updated_at"] = pd.to_datetime(prepared["updated_at"], utc=True)
    prepared["aest_time"] = prepared["inserted_at"].dt.tz_convert("Australia/Brisbane")
    return prepared

@st.cache_data(show_spinner=True, ttl=60)
def _fetch_all_levels_cached() -> pd.DataFrame:
    """DB fetch only. Cache key depends solely on connection + ttl,
    so changing `lookback` never triggers a re-query."""
    
    url = st.secrets.get("remote_api_url", "")
    url = f"{url}/fetch_water_levels" if url else ""

    if not url:
        return None

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        payload = response.json()
    
        raw_levels = pd.DataFrame(payload)
        
        if raw_levels.empty:
            return raw_levels
        
        return _prepare_levels_frame(raw_levels)
            
    except requests.RequestException:
        return None
    except ValueError:
        return None

def load_water_levels_store(
    *,
    lookback: pd.Timedelta = None,
) -> WaterLevelsStoreState:
    
    # if its first time loading the store, clear the cache to ensure we have the latest data
    if not st.session_state.get(INITIALIZED_KEY, False):
        clear_water_levels_store_cache()
        st.session_state[INITIALIZED_KEY] = True
    
    if lookback is None:
        calculated_lookback = st.session_state.get(LOOKBACK_KEY, CONF_DEFAULT_LOOKBACK_PERIOD)
    else:
        calculated_lookback = lookback
    
    """Derives the view (recent_levels/latest_*) from the cached fetch.
    This part is cheap and always recomputed against the real 'now'."""
    try:
        all_levels = _fetch_all_levels_cached()
    except Exception as exc:
        logger.exception("Failed to fetch water levels from database", exc_info=exc)
        st.warning("Database is unavailable right now. Showing empty data until connection is restored.")
        all_levels = _empty_levels_frame()

    if all_levels is None:
        all_levels = _empty_levels_frame()
    
    if all_levels.empty:
        return WaterLevelsStoreState(
            all_levels=all_levels,
            recent_levels=all_levels,
            latest_water_level=0.0,
            latest_battery_level=0.0,
            latest_measured_time="N/A",
            latest_watered_time="N/A",
            latest_bucket_stocked="N/A",
        )

    cutoff = pd.Timestamp.now(tz="UTC") - calculated_lookback
    
    recent_levels = all_levels[all_levels["inserted_at"] >= cutoff].sort_values("inserted_at")
    
    latest_row = all_levels.iloc[0]
    formatted_latest_time = latest_row["aest_time"].strftime("%d %b %H:%M:%S")
    
    latest_has_watered_row = all_levels[all_levels["has_watered"] == True].iloc[0] if not all_levels[all_levels["has_watered"] == True].empty else None
    formatted_latest_water_time = latest_has_watered_row["aest_time"].strftime("%d %b %H:%M:%S") if latest_has_watered_row is not None else "N/A"

    formatted_latest_bucket_stocked = latest_row["bucket_stocked"] if "bucket_stocked" in latest_row else "N/A"
        
    return WaterLevelsStoreState(
        all_levels=all_levels,
        recent_levels=recent_levels,
        latest_water_level=float(latest_row["level"]),
        latest_battery_level=float(latest_row["battery_level"]),
        latest_measured_time=formatted_latest_time,
        latest_watered_time=formatted_latest_water_time,
        latest_bucket_stocked=formatted_latest_bucket_stocked,
    )


def clear_water_levels_store_cache() -> None:
    _fetch_all_levels_cached.clear()
    
    
def set_lookback_period(new_lookback: pd.Timedelta) -> None:
    st.session_state[LOOKBACK_KEY] = new_lookback
            
def get_current_lookback() -> pd.Timedelta:
    return st.session_state.get(LOOKBACK_KEY, CONF_DEFAULT_LOOKBACK_PERIOD)