"""
Check what URL Streamlit is actually using
"""
import streamlit as st

st.title("URL Diagnostic")

st.write("Current URL info:")
st.write(f"Query params: {st.query_params}")

import socket
hostname = socket.gethostname()
st.write(f"Hostname: {hostname}")

st.write("\nStreamlit is running on this host")
st.write("Check the terminal for the actual URL being used")
