import streamlit as st
from streamlit_echarts import st_echarts

DEFAULT_RANGES = [[0.35, "#EF4444"], [0.75, "#F59E0B"], [1, "#22C55E"]]


def moisture_gauge(
    moisture_percent: int,
    font_size: int = 60,
    height: str = "300px",
    *,
    track_width: int = 20,             # thickness of the background color bands
    progress_width: int = 20,          # thickness of the value arc
    progress_color: str = "#3EB4EB",
    progress_opacity: float = 0.75,
    ranges: list | None = None,        # [[fraction, color], ...] background bands
    round_cap: bool = True,
    show_progress: bool = True,
    font_weight: str | int = "bold",
    detail_offset: list | None = None,  # e.g. [0, "-20%"]
    start_angle: int = 180,
    end_angle: int = 0,
    radius: str = "100%",
):
    """Render a semicircular moisture gauge.

    All visual aspects (colors, widths, angles, label size/position) are
    exposed as keyword arguments so callers can restyle the gauge without
    touching this file.
    """
    ranges = ranges or DEFAULT_RANGES
    detail_offset = detail_offset or [0, "-20%"]
    
    # cap_moisture_percent to [0, 100] to avoid rendering issues with ECharts
    moisture_percent = max(0, min(100, moisture_percent))

    value_colour = next(colour for max_v, colour in ranges if moisture_percent / 100 <= max_v)

    options = {
        "backgroundColor": "rgba(0,0,0,0)",
        "series": [
            {
                "type": "gauge",
                "startAngle": start_angle,
                "endAngle": end_angle,
                # Pin the center near the bottom and enlarge radius so the
                # semicircle fills the component's width/height.
                "center": ["50%", "85%"],
                "radius": radius,
                "data": [{"value": moisture_percent}],
                "min": 0,
                "max": 100,
                "splitNumber": 5,
                "axisLine": {
                    "lineStyle": {"width": track_width, "color": ranges},
                    "roundCap": round_cap,
                },
                "progress": {
                    "show": show_progress,
                    "roundCap": round_cap,
                    "width": progress_width,
                    "itemStyle": {"color": progress_color, "opacity": progress_opacity},
                },
                "splitLine": {"show": False},
                "axisTick": {"show": False},
                "axisLabel": {"show": False},
                "pointer": {"show": False},
                "detail": {
                    "show": True,
                    "color": value_colour,
                    "offsetCenter": detail_offset,
                    "fontSize": font_size,
                    "fontWeight": font_weight,
                    "formatter": "{value}%",
                },
            }
        ]
    }
    st_echarts(options=options, height=height)


if __name__ == "__main__":
    st.set_page_config(page_title="Moisture Gauge Demo")
    moisture_gauge(moisture_percent=72, font_size=60, height="300px")
    # Example of overriding styling:
    moisture_gauge(
        moisture_percent=40,
        font_size=40,
        height="200px",
        progress_color="#0EA5E9",
        track_width=14,
        progress_width=14,
    )