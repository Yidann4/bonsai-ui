import streamlit as st

try:
    from src.components.fullscreen_modal import render_fullscreen_modal
except ModuleNotFoundError:
    from fullscreen_modal import render_fullscreen_modal

try:
    from src.stores.config_store import ConfigStoreState, load_config_store
except ModuleNotFoundError:
    from stores.config_store import ConfigStoreState, load_config_store


def config_modal(
    *,
    open: bool = False,
    title: str = "Bonsai Configs",
    state_key: str = "config_modal_open",
    key: str = "config-modal",
) -> None:
    """Open and/or render the config modal in one call.

    Use `open=True` on the run where a trigger is clicked, and call this
    function once per rerun from your app layout.
    """
    if open:
        st.session_state[state_key] = True

    modal_body = config_modal_body

    render_fullscreen_modal(
        body=modal_body,
        title=title,
        state_key=state_key,
        key=key,
    )
    
def water_max_mins_config(configs: ConfigStoreState, can_edit: bool = False):
    left, right = st.columns([1, 1])
    with left:
        st.subheader("Minimums")
        st.number_input(
            "min_water_level",
            min_value=0,
            value=configs.min_water_level,
            step=1,
            format="%d",
            key="min_water_level",
            disabled=not can_edit,
        )
        st.number_input(
            "min_battery_level",
            min_value=0,
            value=configs.min_battery_level,
            step=1,
            format="%d",
            key="min_battery_level",
            disabled=not can_edit,
        )

    with right:
        st.subheader("Maximums")
        st.number_input(
            "max_water_level",
            min_value=0,
            value=configs.max_water_level,
            step=1,
            format="%d",
            key="max_water_level",
            disabled=not can_edit,
        )
        st.number_input(
            "max_battery_level",
            min_value=0,
            value=configs.max_battery_level,
            step=1,
            format="%d",
            key="max_battery_level",
            disabled=not can_edit,
        )

def watering_timings_config(configs: ConfigStoreState, can_edit: bool = False):
    st.subheader("Watering Timings")
    with st.container(horizontal=True):
        st.number_input(
            "Water Burst Time (seconds)",
            min_value=0,
            value=configs.water_burst_time,
            step=1,
            format="%d",
            key="water_burst_time",
            disabled=not can_edit,
        )
        
        st.number_input(
            "Water Settling Time (seconds)",
            min_value=0,
            value=configs.water_settling_time,
            step=1,
            format="%d",
            key="water_settling_time",
            disabled=not can_edit,
        )
    
def esp32_sleep_timings_config(configs: ConfigStoreState, can_edit: bool = False):
    st.subheader("ESP32 Sleep Timings")
    with st.container(horizontal=True):
        st.number_input(
            "Deepsleep Time (seconds)",
            min_value=0,
            value=configs.deepsleep_time,
            step=1,
            format="%d",
            key="deepsleep_time",
            disabled=not can_edit,
        )
        
        st.number_input(
            "Maximum Alive Time (ms)",
            min_value=0,
            value=configs.maximum_alive_time,
            step=1,
            format="%d",
            key="maximum_alive_time",
            disabled=not can_edit,
        )
        
def config_modal_body(can_edit: bool = True):
    configs = load_config_store()

    watering_timings_config(configs=configs, can_edit=can_edit)

    esp32_sleep_timings_config(configs=configs, can_edit=can_edit)
        
    water_max_mins_config(configs=configs, can_edit=can_edit)
    
    

if __name__ == "__main__":
    st.set_page_config(page_title="Fullscreen Modal Demo")
    st.markdown("# Fullscreen Modal Demo")

    open_clicked = st.button("Open Fullscreen Modal")
    config_modal(open=open_clicked)