from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

CONF_DEFAULT_LOOKBACK_PERIOD = pd.Timedelta(days=1)

@dataclass(frozen=True)
class WaterLevelsStoreState:
    all_levels: pd.DataFrame
    recent_levels: pd.DataFrame # based on CONF_DEFAULT_LOOKBACK_PERIOD
    latest_water_level: float
    latest_battery_level: float
    latest_measured_time: str

def _build_query(limit: int) -> str:
    return f"SELECT * FROM public.water_levels ORDER BY id DESC LIMIT {int(limit)};"


def _prepare_levels_frame(levels: pd.DataFrame) -> pd.DataFrame:
    prepared = levels.copy()
    prepared["inserted_at"] = pd.to_datetime(prepared["inserted_at"], utc=True)
    prepared["aest_time"] = prepared["inserted_at"].dt.tz_convert("Australia/Brisbane")
    return prepared


@st.cache_data(show_spinner=False)
def _load_water_levels_store_cached(
    postgres_connection_name: str,
    *,
    limit: int = 100,
    lookback: pd.Timedelta = pd.Timedelta(days=1),
    ttl: str = "0",
) -> WaterLevelsStoreState:
    connection = st.connection(postgres_connection_name, type="sql")
    raw_levels = connection.query(_build_query(limit), ttl=ttl)

    if raw_levels.empty:
        empty = raw_levels.copy()
        return WaterLevelsStoreState(
            all_levels=empty,
            recent_levels=empty,
            latest_water_level=0.0,
            latest_battery_level=0.0,
            latest_measured_time="N/A",
        )

    all_levels = _prepare_levels_frame(raw_levels)
    latest_row = all_levels.iloc[0]

    cutoff = pd.Timestamp.now(tz="UTC") - lookback
    recent_levels = all_levels[all_levels["inserted_at"] >= cutoff].sort_values("inserted_at")
    formatted_latest_time = latest_row["aest_time"].strftime("%d %b %H:%M:%S")
    
    return WaterLevelsStoreState(
        all_levels=all_levels,
        recent_levels=recent_levels,
        latest_water_level=float(latest_row["level"]),
        latest_battery_level=float(latest_row["battery_level"]),
        latest_measured_time=formatted_latest_time,
    )


def load_water_levels_store(
    postgres_connection_name: str,
    *,
    limit: int = 100,
    lookback: pd.Timedelta = CONF_DEFAULT_LOOKBACK_PERIOD,
    ttl: str = "0",
) -> WaterLevelsStoreState:
    return _load_water_levels_store_cached(
        postgres_connection_name,
        limit=limit,
        lookback=lookback,
        ttl=ttl,
    )


def clear_water_levels_store_cache() -> None:
    _load_water_levels_store_cached.clear()
