from __future__ import annotations

from typing import Any

import requests
import streamlit as st


@st.cache_data(show_spinner=True, ttl=60)
def fetch_users() -> list[dict[str, Any]]:
    """Fetch users from the URL configured in st.secrets['remote_api_url']."""
    url = st.secrets.get("remote_api_url", "")
    url = f"{url}/fetch_users" if url else ""

    if not url:
        return []

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        payload = response.json()

        print(f"Fetched users from API: {payload}")  # Debugging statement

        # payload = %{id: 1, name: "User 1"}
        if isinstance(payload, dict):
            users = payload.get("data", payload.get("users", []))
            if isinstance(users, list):
                return [item for item in users if isinstance(item, dict)]

        return []
    except requests.RequestException:
        return []
    except ValueError:
        return []
