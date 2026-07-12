import streamlit as st
try:
    from src.components.moisture_gauge import moisture_gauge
except ModuleNotFoundError:
    from moisture_gauge import moisture_gauge
    
CARD_HEIGHT = "100px"

def moisture_card(moisture_percent: int, last_measured: str):
    """Render a moisture card with a gauge and percentage display."""
    st.markdown(
        """
        <style>
            div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div:has(.stEcharts) {
                margin-bottom: 0 !important;
            }
            .stEcharts {
                margin: 0 !important;
                padding: 0 !important;
            }
            .metric-icon {
                font-size: 30px;
                color: #2f9e44;
                text-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
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

    left, right = st.columns([1, 1])
    with left:
        moisture_gauge(moisture_percent=moisture_percent, font_size=40, height=CARD_HEIGHT)
    with right:
        st.markdown(
            f"""
            <div style="height:{CARD_HEIGHT}; display:flex; flex-direction:column; justify-content:space-evenly;">
                <span style="font-size:30px; font-weight:600; display:flex; align-items:center; gap:6px;">
                    <span class="material-symbols-outlined metric-icon">water_drop</span>
                    {moisture_percent}%
                </span>
                <span style="font-size:30px; font-weight:600; display:flex; align-items:center; gap:6px;">
                    <span class="material-symbols-outlined metric-icon">timer</span>
                    {last_measured}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

if __name__ == "__main__":
    st.set_page_config(page_title="Moisture Card Demo")
    moisture_card(moisture_percent=65, last_measured="test") #"2026-01-01T00:00:00") # ISO 8601 YYYY-MM-DDTHH:MM:SS

