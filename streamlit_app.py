"""Streamlit Cloud entrypoint for Veil.

The canonical local command remains ``streamlit run app.py``; this small
wrapper also supports the conventional ``streamlit_app.py`` Cloud path.
"""
from app import *  # noqa: F401,F403
