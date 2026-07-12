import streamlit as st
import matplotlib.pyplot as plt

def render_vertical_progress_bar(
    value: float,
    *,
    color: str = "blue",
    alpha: float = 0.5,
    figsize: tuple[float, float] = (0.5, 0.75),
) -> None:
    """Render a compact vertical progress bar in Streamlit.

    Accepts values in either 0-1 or 0-100 range and clamps to valid bounds.
    """
    normalized = value / 100 if value > 1 else value
    normalized = max(0.0, min(1.0, float(normalized)))

    fig, ax = plt.subplots(figsize=figsize)
    glass = plt.Rectangle((0.25, 0), 0.5, 1, fill=False, linewidth=2, edgecolor=color)
    ax.add_patch(glass)
    water = plt.Rectangle((0.25, 0), 0.5, normalized, color=color, alpha=alpha)
    ax.add_patch(water)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 1.02, f"{value:.1f}%", ha="center", va="bottom", fontsize=7)
    st.pyplot(fig, use_container_width=False)
    plt.close(fig)