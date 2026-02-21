import os
import streamlit as st
from supabase import create_client, Client

_client: Client | None = None

def get_supabase() -> Client:
    global _client
    if _client is None:
        try:
            # Streamlit Cloud (secrets.toml)
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
        except Exception:
            # Local dev (.env)
            from dotenv import load_dotenv
            load_dotenv()
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_KEY")

        if not url or not key:
            raise ValueError("Supabase credentials not found in .env or secrets.toml")
        _client = create_client(url, key)
    return _client
