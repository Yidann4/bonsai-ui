from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

CONF_DEFAULT_LOOKBACK_PERIOD = pd.Timedelta(days=1)
CONF_MAX_FETCH_COUNT = 7200  # 24 * 10 * 30 (30 days)

POSTGRES_CONN_KEY = "postgres_conn"
LOOKBACK_KEY = "lookback_period"


@dataclass(frozen=True)
class WaterLevelsStoreState:
    all_levels: pd.DataFrame
    recent_levels: pd.DataFrame  # based on lookback
    latest_water_level: float
    latest_battery_level: float
    latest_measured_time: str


def _build_query() -> str:
    return f"SELECT * FROM public.water_levels ORDER BY id DESC LIMIT {CONF_MAX_FETCH_COUNT};"


def _prepare_levels_frame(levels: pd.DataFrame) -> pd.DataFrame:
    prepared = levels.copy()
    prepared["inserted_at"] = pd.to_datetime(prepared["inserted_at"], utc=True)
    prepared["aest_time"] = prepared["inserted_at"].dt.tz_convert("Australia/Brisbane")
    return prepared


@st.cache_data(show_spinner=False)
def _fetch_all_levels_cached(
    postgres_connection_name: str,
    *,
    ttl: str = "0",
) -> pd.DataFrame:
    """DB fetch only. Cache key depends solely on connection + ttl,
    so changing `lookback` never triggers a re-query."""
    connection = st.connection(postgres_connection_name, type="sql")
    raw_levels = connection.query(_build_query(), ttl=ttl)

    if raw_levels.empty:
        return raw_levels

    return _prepare_levels_frame(raw_levels)


def load_water_levels_store(
    postgres_connection_name: str,
    *,
    lookback: pd.Timedelta = None,
    ttl: str = "0",
) -> WaterLevelsStoreState:
    
    if lookback is None:
        calculated_lookback = st.session_state.get(LOOKBACK_KEY, CONF_DEFAULT_LOOKBACK_PERIOD)
    else:
        calculated_lookback = lookback
    
    """Derives the view (recent_levels/latest_*) from the cached fetch.
    This part is cheap and always recomputed against the real 'now'."""
    all_levels = _fetch_all_levels_cached(postgres_connection_name, ttl=ttl)
    
    st.session_state[POSTGRES_CONN_KEY] = postgres_connection_name

    if all_levels.empty:
        return WaterLevelsStoreState(
            all_levels=all_levels,
            recent_levels=all_levels,
            latest_water_level=0.0,
            latest_battery_level=0.0,
            latest_measured_time="N/A",
        )

    latest_row = all_levels.iloc[0]

    cutoff = pd.Timestamp.now(tz="UTC") - calculated_lookback
    
    print(cutoff)
    recent_levels = all_levels[all_levels["inserted_at"] >= cutoff].sort_values("inserted_at")
    formatted_latest_time = latest_row["aest_time"].strftime("%d %b %H:%M:%S")

    print("AIDAN INTERACTION RELOADED")
    return WaterLevelsStoreState(
        all_levels=all_levels,
        recent_levels=recent_levels,
        latest_water_level=float(latest_row["level"]),
        latest_battery_level=float(latest_row["battery_level"]),
        latest_measured_time=formatted_latest_time,
    )


def clear_water_levels_store_cache() -> None:
    _fetch_all_levels_cached.clear()
    
    
def set_lookback_period(new_lookback: pd.Timedelta) -> None:
    st.session_state[LOOKBACK_KEY] = new_lookback
            
def get_current_lookback() -> pd.Timedelta:
    return st.session_state.get(LOOKBACK_KEY, CONF_DEFAULT_LOOKBACK_PERIOD)