"""
Supabase Client Module
Creates and provides a single shared database connection to Supabase.

📌 TEACHING NOTE — What is Supabase?
    Supabase is an open-source Firebase alternative built on PostgreSQL.
    It provides:
    - A hosted PostgreSQL database
    - A REST and real-time API auto-generated from your database schema
    - Authentication, storage, and edge functions

    In this app, Supabase is used to persist analysis results — so a user
    can view their resume history across sessions.

📌 TEACHING NOTE — What does THIS file do?
    It solves one problem: "how do we get a database connection anywhere
    in the app without creating a new connection every time?"

    The answer is the Singleton Pattern — one shared client object,
    created once, reused everywhere.

    Any other module that needs the database just imports get_supabase():
        from app.core.supabase_client import get_supabase
        db = get_supabase()
        db.table('analyses').insert({...}).execute()

📌 TEACHING NOTE — Two environments, one function:
    Development:  credentials stored in a local .env file
    Production:   credentials stored in Streamlit Cloud's secrets.toml

    get_supabase() handles BOTH transparently — the caller never needs to
    know which environment it's running in.
"""

import os
import streamlit as st
from supabase import create_client, Client


# ── Module-level singleton variable ───────────────────────────────────────────

# 📌 TEACHING NOTE — Module-level variable with type annotation:
#   _client: Client | None = None
#
#   This is a MODULE-LEVEL variable (not inside any class or function).
#   It lives for the entire lifetime of the Python process.
#   The leading underscore _ signals "private to this module — don't import directly."
#
#   Client | None is Python 3.10+ union type syntax.
#   Equivalent to Optional[Client] from typing.
#   Means: this variable holds either a Client object OR None.
#
#   It starts as None (no connection yet).
#   After the first call to get_supabase(), it holds the real Client object.
_client: Client | None = None


def get_supabase() -> Client:
    """
    Return the shared Supabase client, creating it on first call.

    📌 TEACHING NOTE — The Singleton Pattern:
        A Singleton ensures only ONE instance of something is ever created,
        no matter how many times you ask for it.

        Implementation here uses the "lazy initialization" approach:
            global _client           ← refer to the module-level variable
            if _client is None:      ← only create if not yet created
                _client = create_client(url, key)
            return _client           ← always return the same object

        "Lazy" means we don't create the connection at import time —
        only when first needed. This avoids:
        - Startup delays if the DB is never actually used
        - Credential errors at import time in environments without credentials

        After the first call, _client is no longer None, so every subsequent
        call skips the if block entirely and immediately returns the existing client.

    📌 TEACHING NOTE — global keyword:
        global _client
        This tells Python: "when I say _client in this function, I mean
        the module-level _client variable, not a new local one."

        Without 'global', Python would create a NEW local variable _client
        inside the function scope, leaving the module-level one unchanged.
        The singleton would break — a new client would be created every call.

        Rule of thumb: 'global' is needed whenever you want to REASSIGN
        a module-level variable inside a function. Reading it doesn't need 'global'.

    📌 TEACHING NOTE — Two-environment credential loading (try/except):
        try:
            url = st.secrets["SUPABASE_URL"]   ← Streamlit Cloud
            key = st.secrets["SUPABASE_KEY"]
        except Exception:
            from dotenv import load_dotenv      ← local .env file
            load_dotenv()
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_KEY")

        Streamlit Cloud stores secrets in a managed secrets.toml file
        (set via the Streamlit Cloud dashboard). These are injected into
        st.secrets at runtime.

        In local development, a .env file holds the same credentials.
        load_dotenv() reads the .env file and injects the values into
        os.environ, making them accessible via os.environ.get().

        The try/except catches the case where st.secrets isn't available
        (e.g., running in plain Python or a unit test) and falls back to .env.

        This is environment-aware configuration — the same code runs
        correctly in both environments without modification.

    📌 TEACHING NOTE — Guard for missing credentials:
        if not url or not key:
            raise ValueError("Supabase credentials not found in .env or secrets.toml")

        'not url' is True if url is None (os.environ.get returned None)
        OR if url is an empty string "".

        Raising a ValueError with a clear message is much more helpful than
        letting the code fail later with a cryptic connection error.
        "Supabase credentials not found in .env or secrets.toml" tells the
        developer exactly what to fix and where to look.

        This is the "fail fast with a clear message" principle — catch
        configuration problems at startup, not buried inside a request handler.

    📌 TEACHING NOTE — create_client(url, key):
        This is the Supabase Python SDK's constructor.
        It sets up the HTTP client configured to talk to your Supabase project.
        It does NOT make a network request yet — the connection is established
        lazily when the first actual database operation is performed.

    Returns:
        The shared Supabase Client instance

    Raises:
        ValueError: If credentials are missing from both secrets.toml and .env
    """
    global _client  # Refer to the module-level variable, not a new local one

    if _client is None:
        # ── Load credentials: try Streamlit Cloud secrets first ───────────
        try:
            url = st.secrets["SUPABASE_URL"]   # Set via Streamlit Cloud dashboard
            key = st.secrets["SUPABASE_KEY"]
        except Exception:
            # ── Fallback: load from local .env file ───────────────────────
            from dotenv import load_dotenv
            load_dotenv()                                   # Reads .env → os.environ
            url = os.environ.get("SUPABASE_URL")            # None if not set
            key = os.environ.get("SUPABASE_KEY")

        # ── Guard: fail fast if credentials are missing ───────────────────
        if not url or not key:
            raise ValueError(
                "Supabase credentials not found in .env or secrets.toml"
            )

        # ── Create the client and cache it in the module-level variable ───
        _client = create_client(url, key)

    return _client  # Same object returned on every subsequent call