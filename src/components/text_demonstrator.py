import streamlit as st

def text_demonstrator(value: float, unit: str | None):
    left, right = st.columns([1, 3])
    with left:
        if st.button("Water Action", icon=":material/water_drop:"):
            st.write("The button was clicked!")
    st.metric("test", 123)
    
    st.info("This is an info message.")
    st.warning("This is a warning message.")
    st.error("This is an error message.")
    
    # structured data elements
    st.json({"key": "value", "number": 123, "list": [1, 2, 3]})
    st.table({"Column 1": [1, 2, 3], "Column 2": ["A", "B", "C"]})
    st.dataframe({"Column 1": [1, 2, 3], "Column 2": ["A", "B", "C"]})
    
    # styled
    st.markdown("<h1 style='color: blue;'>This is a blue heading</h1>", unsafe_allow_html=True)
    st.code("print('Hello, world!')", language="python")
    st.latex(r"e^{i\pi} + 1 = 0")
    
    # text and headers
    st.title("This is a title")
    st.header("This is a header")
    st.subheader("This is a subheader")
    st.text("This is some text.")
    st.caption("This is a caption.")
    
    # streamlit fundamentals
    st.write("This is a write statement.")
    
    st.metric("Value", value, delta=5, delta_color="inverse", help="This is a metric with a delta.")

if __name__ == "__main__":
    st.set_page_config(page_title="Text Demonstrator Demo")
    text_demonstrator(value=67, unit="%")