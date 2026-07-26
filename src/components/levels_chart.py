import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

from src.stores.water_levels_store import set_lookback_period
from src.components.glass_container import glass_container


LOOKBACK_OPTIONS = [
    ("Daily", pd.Timedelta(days=1)),
    ("Weekly", pd.Timedelta(weeks=1)),
    ("Monthly", pd.Timedelta(days=30)),
]


def _cycle_lookback_period() -> None:
    current_index = st.session_state.get("lookback_toggle_index", 0)
    next_index = (current_index + 1) % len(LOOKBACK_OPTIONS)
    st.session_state["lookback_toggle_index"] = next_index
    _, next_period = LOOKBACK_OPTIONS[next_index]
    set_lookback_period(next_period)


def levels_chart(levels_array: pd.DataFrame):
    tooltip_fields = [
        alt.Tooltip("id:N", title="ID"),
        alt.Tooltip("level:Q", title="Level"),
        alt.Tooltip("battery_level:Q", title="Battery Level"),
    ]

    level_chart = (
        alt.Chart(levels_array)
        .mark_area(opacity=0.45)
        .encode(
            x=alt.X("aest_time:T", title="Time"),
            y=alt.Y("level:Q", title="Level"),
            color=alt.value("#2E8B57"),
            tooltip=tooltip_fields,
        )
    )

    battery_chart = (
        alt.Chart(levels_array)
        .mark_line(strokeWidth=2)
        .encode(
            x=alt.X("aest_time:T", title="Time"),
            y=alt.Y("battery_level:Q", title="Battery Level"),
            color=alt.value("#D9534F"),
            tooltip=tooltip_fields,
        )
    )

    combined_chart = alt.layer(level_chart, battery_chart).resolve_scale(y="independent")
    if "lookback_toggle_index" not in st.session_state:
        st.session_state["lookback_toggle_index"] = 0

    current_index = st.session_state["lookback_toggle_index"]
    current_label, _ = LOOKBACK_OPTIONS[current_index]

    with glass_container(key="levels-chart"):
        with st.container(horizontal=True):
            with st.container(horizontal_alignment="left"):
                st.header("Levels")
            with st.container(horizontal=True, horizontal_alignment="right"):
                st.button(
                    f"{current_label}",
                    on_click=_cycle_lookback_period,
                    help="Toggle between Daily, Weekly, and Monthly",
                )
        st.altair_chart(combined_chart, width='stretch')
    
    
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