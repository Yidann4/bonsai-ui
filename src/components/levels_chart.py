import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

from src.stores.water_levels_store import set_lookback_period
from src.components.glass_container import glass_container


def levels_chart(levels_array: pd.DataFrame):
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
    with glass_container(key="levels-chart"):
        with st.container(horizontal=True):
            with st.container(horizontal_alignment="left"):
                st.header("Levels")
                # Lay out the buttons horizontally and aligned to the right
            with st.container(horizontal=True, horizontal_alignment="right"):
                st.button("Daily", on_click=set_lookback_period, args=(pd.Timedelta(days=1),))
                st.button("Weekly", on_click=set_lookback_period, args=(pd.Timedelta(weeks=1),))
                st.button("Monthly", on_click=set_lookback_period, args=(pd.Timedelta(days=30),))
        st.altair_chart(combined_chart, use_container_width=True)
    
    
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".streamlit"))
    from stores.water_levels_store import load_water_levels_store
    store_obj = load_water_levels_store()
    
    st.set_page_config(page_title="Levels Chart Demo")
    st.markdown("# Levels Chart Demo")

    levels_chart(levels_array=store_obj.recent_levels)
    st.write(store_obj.recent_levels)