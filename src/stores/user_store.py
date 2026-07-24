from __future__ import annotations

from typing import Any

import requests
import streamlit as st

KEY_USER_LIST = "user_list"
KEY_SIGNED_IN_USER = "signed_in_user"

def fetch_users() -> None:
    payload = query_db_users()
    
    # payload = [{'id': 1, 'name': 'Billy bob'}, {'id': 2, 'name': 'Uncle Joe'}]
    if isinstance(payload, list):
        st.session_state[KEY_USER_LIST] = payload

@st.cache_data(show_spinner=True, ttl=60)
def query_db_users() -> list:
    """Fetch users from the URL configured in st.secrets['remote_api_url']."""
    url = st.secrets.get("remote_api_url", "")
    url = f"{url}/fetch_users" if url else ""

    if not url:
        return None

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        payload = response.json()
    
        return payload
            
    except requests.RequestException:
        return None
    except ValueError:
        return None
    
def set_signed_in_user() -> None:
    """Set the signed-in user in session state."""
    # clear any signed in user if the username input is changed
    st.session_state[KEY_SIGNED_IN_USER] = None
    
    username = st.session_state["username_input"]
    if KEY_USER_LIST not in st.session_state:
        return None
    
    for user in st.session_state[KEY_USER_LIST]:
        if user.get("name") == username:
            st.session_state[KEY_SIGNED_IN_USER] = user
    
    return None
        
def check_user_edit_permissions() -> bool:    
    if st.session_state.get(KEY_SIGNED_IN_USER) is None:
        return False
    elif len(st.session_state[KEY_SIGNED_IN_USER].get("name", "")) >= 5:
        return True
        
    return False
        