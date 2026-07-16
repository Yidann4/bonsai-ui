import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

def levels_chart(levels_array: pd.DataFrame):
    st.header("Daily Levels")
    level_chart = (
        alt.Chart(levels_array)
        .mark_area(opacity=0.45)
        .encode(
            x=alt.X("id:Q", title="Time"),
            y=alt.Y("level:Q", title="Level"),
            color=alt.value("#2E8B57"),
            tooltip=["id", "level", "battery_level"],
        )
    )

    battery_chart = (
        alt.Chart(levels_array)
        .mark_line(strokeWidth=2)
        .encode(
            x=alt.X("id:Q", title="Time"),
            y=alt.Y("battery_level:Q", title="Battery Level"),
            color=alt.value("#D9534F"),
            tooltip=["id", "level", "battery_level"],
        )
    )

    combined_chart = alt.layer(level_chart, battery_chart).resolve_scale(y="independent")
    st.altair_chart(combined_chart, use_container_width=True)
    
    
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".streamlit"))
    from config_parser import postgres_conn
    from stores.water_levels_store import load_water_levels_store
    store_obj = load_water_levels_store(postgres_conn)
    
    st.set_page_config(page_title="Levels Chart Demo")
    st.markdown("# Levels Chart Demo")

    levels_chart(levels_array=store_obj.recent_levels)
    store_obj.recent_levels