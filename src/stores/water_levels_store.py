from __future__ import annotations

from dataclasses import dataclass
import logging

import pandas as pd
import requests
import streamlit as st

try:
    from src.stores.config_store import config_object_from_state
except ModuleNotFoundError:
    from stores.config_store import config_object_from_state

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
    latest_measured_time: pd.Timestamp | None
    latest_watered_time: pd.Timestamp | None
    latest_bucket_stocked: bool | None


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


def _normalise_series(values: pd.Series, minimum: float, maximum: float) -> pd.Series:
    scaled = ((values - minimum) / (maximum - minimum)) * 100.0
    return scaled.clip(lower=0.0, upper=100.0).fillna(0.0)


def _apply_config_normalisation(levels: pd.DataFrame) -> pd.DataFrame:
    configs = config_object_from_state()

    prepared = levels.copy()
    water_levels = pd.to_numeric(prepared["level"], errors="coerce")
    battery_levels = pd.to_numeric(prepared["battery_level"], errors="coerce")

    prepared["normalised_level"] = _normalise_series(
        water_levels,
        float(configs.min_water_level),
        float(configs.max_water_level),
    )
    prepared["normalised_battery_level"] = _normalise_series(
        battery_levels,
        float(configs.min_battery_level),
        float(configs.max_battery_level),
    )
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
        
        sorted_raw_levels = raw_levels.sort_values("inserted_at", ascending=False)
        return _prepare_levels_frame(sorted_raw_levels)
            
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
            latest_measured_time=None,
            latest_watered_time=None,
            latest_bucket_stocked=None,
        )

    all_levels = _apply_config_normalisation(all_levels)

    cutoff = pd.Timestamp.now(tz="UTC") - calculated_lookback
    
    recent_levels = all_levels[all_levels["inserted_at"] >= cutoff].sort_values("inserted_at")
    
    latest_row = all_levels.iloc[0]
    latest_measured_time = latest_row["aest_time"]
    
    latest_has_watered_row = all_levels[all_levels["has_watered"] == True].iloc[0] if not all_levels[all_levels["has_watered"] == True].empty else None
    latest_watered_time = latest_has_watered_row["aest_time"] if latest_has_watered_row is not None else None
    
    latest_bucket_stocked = bool(latest_row["bucket_stocked"]) if "bucket_stocked" in latest_row and pd.notna(latest_row["bucket_stocked"]) else None
        
    return WaterLevelsStoreState(
        all_levels=all_levels,
        recent_levels=recent_levels,
        latest_water_level=int(latest_row["normalised_level"]),
        latest_battery_level=int(latest_row["normalised_battery_level"]),
        latest_measured_time=latest_measured_time,
        latest_watered_time=latest_watered_time,
        latest_bucket_stocked=latest_bucket_stocked,
    )


def clear_water_levels_store_cache() -> None:
    _fetch_all_levels_cached.clear()
    
    
def set_lookback_period(new_lookback: pd.Timedelta) -> None:
    st.session_state[LOOKBACK_KEY] = new_lookback
            
def get_current_lookback() -> pd.Timedelta:
    return st.session_state.get(LOOKBACK_KEY, CONF_DEFAULT_LOOKBACK_PERIOD)