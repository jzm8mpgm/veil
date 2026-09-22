"""Streamlit Cloud entrypoint for Veil.

The app must be executed on every Streamlit rerun. ``runpy`` deliberately
avoids Python's import cache, which would otherwise leave the Cloud page blank
after the form submits.
"""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name('app.py')), run_name='__main__')
