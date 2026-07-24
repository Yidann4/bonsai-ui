import streamlit as st

try:
    from src.stores.config_store import ConfigStoreState, load_config_store, push_config_updates, set_store_default_values, load_configs_from_state
except ModuleNotFoundError:
    from stores.config_store import ConfigStoreState, load_config_store, push_config_updates, set_store_default_values, load_configs_from_state


def config_modal(
    open: bool = False,
) -> None:

    if not open:
        return

    config_modal_body(can_edit=True)

    
def water_max_mins_config(configs: ConfigStoreState, can_edit: bool = False):
    st.subheader("ADC Ranges")
    with st.container(horizontal=True):
        with st.container(horizontal=False):
            st.markdown("Minimums")
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

        with st.container(horizontal=False):
            st.markdown("Maximums")
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
    
    with st.container(horizontal=True):
        st.number_input(
            "Watering Level Start (ADC)",
            min_value=0,
            value=configs.watering_level_start,
            step=1,
            format="%d",
            key="watering_level_start",
            disabled=not can_edit,
        )
        
        st.number_input(
            "Watering Level End (ADC)",
            min_value=0,
            value=configs.watering_level_end,
            step=1,
            format="%d",
            key="watering_level_end",
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
            "Max Alive Time (ms)",
            min_value=0,
            value=configs.max_alive_time,
            step=1,
            format="%d",
            key="max_alive_time",
            disabled=not can_edit,
        )
        
@st.dialog("Bonsai Configs", width="large")
def config_modal_body(can_edit: bool = True):
    configs = load_config_store()
    
    with st.container(horizontal=True):
        st.button("Save Configs", on_click=push_config_updates, disabled=not can_edit)
        st.button("Reset to Defaults", on_click=set_store_default_values, disabled=not can_edit)
        st.button("Cancel", on_click=load_configs_from_state, disabled=not can_edit)

    watering_timings_config(configs=configs, can_edit=can_edit)

    esp32_sleep_timings_config(configs=configs, can_edit=can_edit)
        
    water_max_mins_config(configs=configs, can_edit=can_edit)
    
    

if __name__ == "__main__":
    st.set_page_config(page_title="Fullscreen Modal Demo")
    st.markdown("# Fullscreen Modal Demo")

    open_clicked = st.button("Open Fullscreen Modal")
    config_modal(open=open_clicked)