from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import streamlit as st


@contextmanager
def glass_container(
    key: str,
    *,
    padding_px: int = 20,
    radius_px: int = 10,
    blur_px: int = 10,
    saturation_pct: int = 120,
    gradient_start_alpha: float = 0.40,
    gradient_end_alpha: float = 0.08,
    border_alpha: float = 0.35,
    shadow_alpha: float = 0.18,
) -> Iterator[None]:
    """Wrap content in a reusable frosted-glass Streamlit container.

    The Streamlit `key` maps to the CSS class `st-key-<key>`, which is used
    to scope the glass style to this specific container.
    """
    st.markdown(
        f"""
        <style>
        .st-key-{key} {{
            background: linear-gradient(
                135deg,
                rgba(255, 255, 255, {gradient_start_alpha}),
                rgba(255, 255, 255, {gradient_end_alpha})
            );
            backdrop-filter: blur({blur_px}px) saturate({saturation_pct}%);
            -webkit-backdrop-filter: blur({blur_px}px) saturate({saturation_pct}%);
            border: 1px solid rgba(255, 255, 255, {border_alpha});
            box-shadow: 0 10px 30px rgba(0, 0, 0, {shadow_alpha});
            padding: {padding_px}px;
            border-radius: {radius_px}px;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key=key):
        yield
