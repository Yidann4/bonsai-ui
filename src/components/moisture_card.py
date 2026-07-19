import sys
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

CARD_HEIGHT = "100px"


def moisture_card(moisture_percent: int, latest_battery_level: int, latest_measured_time: str):
    """Render a moisture card with a gauge and percentage display."""
    st.markdown(
        """
        <style>
            .st-key-live-card div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div:has(.stEcharts) {
                margin-bottom: 0 !important;
            }
            .st-key-live-card .stEcharts {
                margin: 0 !important;
                padding: 0 !important;
            }
            .metric-icon {
                font-size: 30px;
                color: #f1c40f;
                text-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
            }

            /* Keep the gauge and the text side-by-side at every viewport
               width. Streamlit's stHorizontalBlock switches to a vertical
               stack below its mobile breakpoint (~640px) by default; this
               forces it to stay a row. */
            .st-key-live-card div[data-testid="stHorizontalBlock"] {
                flex-wrap: nowrap !important;
                align-items: center;
                width: auto !important;
                display: inline-flex !important;
            }
            .st-key-live-card .stHorizontalBlock .stColumn,
            .st-key-live-card div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
                min-width: 11rem !important;
                width: auto !important;
                max-width: 50% !important; 
                flex: 0 0 auto !important;
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
        left, right = st.columns([1, 1])
        with left.container():
            moisture_gauge(moisture_percent=moisture_percent, font_size=32, height=CARD_HEIGHT)
        with right.container():
            st.markdown(
                f"""
                <div style="height:{CARD_HEIGHT}; display:flex; flex-direction:column; justify-content:space-evenly;">
                    <span style="font-size:clamp(16px, 5vw, 30px); font-weight:600; display:flex; align-items:center; gap:6px; white-space:nowrap;">
                        <span class="material-symbols-outlined metric-icon">battery_change</span>
                        {latest_battery_level}%
                    </span>
                    <span style="font-size:clamp(14px, 4vw, 24px); font-weight:600; display:flex; align-items:center; gap:6px; white-space:nowrap;">
                        <span class="material-symbols-outlined metric-icon">timer</span>
                        {latest_measured_time}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    st.set_page_config(page_title="Moisture Card Demo")
    moisture_card(moisture_percent=65, latest_battery_level=80, latest_measured_time="2026-01-01T00:00:00")  # ISO 8601 YYYY-MM-DDTHH:MM:SS