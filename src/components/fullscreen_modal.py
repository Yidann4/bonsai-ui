from __future__ import annotations

from typing import Callable

import streamlit as st


def open_modal(state_key: str = "fullscreen_modal_open") -> None:
    """Set modal state to open."""
    st.session_state[state_key] = True


def close_modal(state_key: str = "fullscreen_modal_open") -> None:
    """Set modal state to closed."""
    st.session_state[state_key] = False


def _inject_fullscreen_modal_css() -> None:
    """Force Streamlit's dialog to take almost the entire viewport."""
    st.markdown(
        """
        <style>
            div[data-testid="stDialog"] {
                width: 96vw !important;
                max-width: 96vw !important;
            }

            div[data-testid="stDialog"] > div {
                width: 96vw !important;
                max-width: 96vw !important;
                height: 92vh !important;
                max-height: 92vh !important;
                margin: 2vh auto !important;
                border-radius: 14px !important;
                overflow: hidden !important;
            }

            div[data-testid="stDialog"] section[role="dialog"] {
                height: 100% !important;
            }

            div[data-testid="stDialog"] section[role="dialog"] > div {
                height: 100% !important;
                display: flex !important;
                flex-direction: column !important;
            }

            .fullscreen-modal-content {
                height: 100%;
                overflow: auto;
                padding-bottom: 0.25rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_fullscreen_modal(
    body: Callable[[], None],
    *,
    state_key: str = "fullscreen_modal_open",
    title: str = "",
    key: str = "fullscreen-modal",
) -> None:
    """Render a near full-screen modal while `state_key` is True.

    Call `open_modal(state_key)` to show it and `close_modal(state_key)` to hide it.
    """
    if not st.session_state.get(state_key, False):
        return

    _inject_fullscreen_modal_css()

    @st.dialog(title, width="large")
    def _dialog() -> None:

        with st.container(key=f"{key}-content"):
            st.markdown('<div class="fullscreen-modal-content">', unsafe_allow_html=True)
            body()
            st.markdown("</div>", unsafe_allow_html=True)

    _dialog()

if __name__ == "__main__":
    st.set_page_config(page_title="Fullscreen Modal Demo")
    st.write("This is the main page content.")

    if st.button("Open Fullscreen Modal"):
        open_modal()

    render_fullscreen_modal(
        body=lambda: st.write("This is the fullscreen modal content."),
        title="Fullscreen Modal",
    )