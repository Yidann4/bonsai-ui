import sys
import pandas as pd
from pathlib import Path

# look at bonsai-ui/src before looking at streamlit hosted mount/src
app_root = Path(__file__).resolve().parent
if str(app_root) not in sys.path:
    sys.path.insert(0, str(app_root))

import streamlit as st
try:
    from src.components.glass_container import glass_container
    from src.components.moisture_gauge import moisture_gauge
except ModuleNotFoundError:
    from glass_container import glass_container
    from moisture_gauge import moisture_gauge

CARD_HEIGHT = "150px"


def moisture_card(
    moisture_percent: int,
    latest_battery_level: int,
    latest_measured_time: pd.Timestamp | None,
    latest_watered_time: pd.Timestamp | None,
    latest_bucket_stocked: bool | None,
) -> None:
    """Render a moisture card with a gauge and percentage display."""
    
    current_time_aest = pd.Timestamp.now(tz="UTC").tz_convert("Australia/Brisbane")

    latest_measured_display = latest_measured_time.strftime("%d %b %H:%M:%S") if latest_measured_time is not None else "N/A"
    latest_watered_display = latest_watered_time.strftime("%d %b %H:%M:%S") if latest_watered_time is not None else "N/A"
    latest_bucket_stocked_display = "Yes" if latest_bucket_stocked is True else "No" if latest_bucket_stocked is False else "N/A"
    
    red = "#e74c3c"
    yellow = "#f1c40f"
    green = "#2ecc71"
    
    if latest_battery_level < 30:
        battery_icon_color = red
    elif latest_battery_level < 50:
        battery_icon_color = yellow
    else:
        battery_icon_color = green

    watered_icon_color = (
        green
        if latest_watered_time is not None and (current_time_aest - latest_watered_time).total_seconds() < 24 * 3600
        else yellow
    )
    measured_icon_color = green if latest_measured_time is not None and (current_time_aest - latest_measured_time).total_seconds() < 30 * 60 else red
    bucket_icon_color = green if latest_bucket_stocked is True else red
    st.markdown(
        """
        <style>
            .metric-icon {
                font-size: 35px;
                color: var(--metric-icon-color, #f1c40f);
                text-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
            }
            
            .metric-icon.bucket {
                color: var(--metric-icon-color, #f1c40f);
            }

            .st-key-live-card {
                width: fit-content;
                max-width: 100%;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Load the Material Symbols font once — cheap to call repeatedly, browser caches it
    st.markdown(
        '<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">',
        unsafe_allow_html=True,
    )

    with glass_container(key="live-card"):
        st.text("Live")
        with st.container(key="live-card-content", horizontal=True):
            with st.container(key="moisture-gauge"):
                moisture_gauge(moisture_percent=moisture_percent, font_size=32, height=CARD_HEIGHT)
            with st.container(key="metrics"):
                st.markdown(
                    f"""
                    <div style="height:{CARD_HEIGHT}; display:flex; flex-direction:column; justify-content:space-evenly;">
                        <span style="font-size:clamp(14px, 4vw, 24px); font-weight:600; display:flex; align-items:center; gap:6px; white-space:nowrap;">
                            <span class="material-symbols-outlined metric-icon" style="--metric-icon-color:{battery_icon_color};">battery_change</span>
                            {latest_battery_level}%
                        </span>
                        <span style="font-size:clamp(14px, 4vw, 24px); font-weight:600; display:flex; align-items:center; gap:6px; white-space:nowrap;">
                            <span class="material-symbols-outlined metric-icon" style="--metric-icon-color:{watered_icon_color};">water_drops</span>
                            {latest_watered_display}
                        </span>
                        <span style="font-size:clamp(14px, 4vw, 24px); font-weight:600; display:flex; align-items:center; gap:6px; white-space:nowrap;">
                            <span class="material-symbols-outlined metric-icon" style="--metric-icon-color:{measured_icon_color};">timer</span>
                            {latest_measured_display}
                        </span>
                        <span style="font-size:clamp(14px, 4vw, 24px); font-weight:600; display:flex; align-items:center; gap:6px; white-space:nowrap;">
                            <span class="material-symbols-outlined metric-icon" style="--metric-icon-color:{bucket_icon_color};">water_full</span>
                            {latest_bucket_stocked_display}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


if __name__ == "__main__":
    st.set_page_config(page_title="Moisture Card Demo")
    sample_time = pd.Timestamp("2026-01-01T00:00:00", tz="UTC").tz_convert("Australia/Brisbane")
    moisture_card(moisture_percent=65, latest_battery_level=80, latest_measured_time=sample_time, latest_watered_time=sample_time, latest_bucket_stocked=False)