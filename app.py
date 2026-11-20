"""
app.py — Career Readiness Coach entry point.
Streamlit multi-page apps route automatically via the pages/ folder.
This file sets global page config and renders a landing redirect.
"""

import streamlit as st

st.set_page_config(
    page_title="Career Readiness Coach",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.switch_page("pages/01_resume_builder.py")
