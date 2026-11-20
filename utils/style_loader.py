"""
style_loader.py
Injects custom CSS from styles/theme.css into the Streamlit app.
"""

import os
import streamlit as st


def inject_css() -> None:
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "theme.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
