"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import pandas as pd

st.write("Here's our first attempt at using data to create a table:")

test = 'this is a test'
test

df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})

df

authorized = True
if not authorized:
  st.stop()

x = st.slider('x')  # 👈 this is a widget
st.write(x, 'squared is', x * x)

st.text_input("Your name", key="name")

# You can access the value at any point with:
st.session_state.name

################### SQL TABLES #######################

# Initialize connection.
# sqlconn = st.connection("local_postgresql", type="sql")

# # Perform query.
# water_levels = sqlconn.query('SELECT * FROM water_levels;', ttl="0")
# water_levels

remoteconn = st.connection("remote_postgresql", type="sql")

# Perform query.
query = 'SELECT * FROM public.water_levels ORDER BY id DESC LIMIT 100;'
remote_water_levels = remoteconn.query(query, ttl="10m")
remote_water_levels