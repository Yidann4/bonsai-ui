import streamlit as st
from streamlit_echarts import st_echarts

gauge_ranges = [[0.35, "#EF4444"], [0.75, "#F59E0B"], [1, "#22C55E"]]



def moisture_gauge(moisture_percent: int, font_size: int, height: str):    
    for max, colour in gauge_ranges:
        if moisture_percent / 100 <= max:
            value_colour = colour
            break
        
    options = {
        "series": [
            {
                "type": "gauge",
                "startAngle": 180, "endAngle": 0,
                # Pin the center near the bottom and enlarge radius so the
                # semicircle fills the component's width/height.
                "center": ["50%", "85%"],
                "radius": "170%",
                "data": [{"value": moisture_percent}],
                "min": 0,
                "max": 100,
                "splitNumber": 5,
                "axisLine": {"lineStyle": {"width": 20, "color": gauge_ranges}, "roundCap": True},
                "progress": {"show": True, "roundCap": True, "width": 20, "itemStyle": {"color": "#3EB4EB", "opacity": 0.75}},
                "splitLine": {"show": False},
                "axisTick": {"show": False},
                "axisLabel": {"show": False},
                "pointer": {"show": False},
                "detail": {"show": True, "color": value_colour, "offsetCenter": [0, "-20%"], "fontSize": font_size, "formatter": "{value}%"},
            }
        ]
    }
    st_echarts(options=options, height=height)

if __name__ == "__main__":
    st.set_page_config(page_title="Moisture Gauge Demo")
    moisture_gauge(moisture_percent=72, font_size=60, height="300px")