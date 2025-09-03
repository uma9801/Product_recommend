# Create a dummy streamlit page 
import streamlit as st
from streamlit_scroll_navigation import scroll_navbar

# Anchor IDs and icons
anchor_ids = ["Top", "About", "Features", "uma", "Settings", "Pricing", "Contact"]
anchor_icons = ["arrow-bar-up", "info-circle", "lightbulb", "playstation", "gear", "tag", "envelope"]

# 1. as sidebar menu
with st.sidebar:
    st.subheader("Example 01")
    scroll_navbar(
        anchor_ids,
        key = "navbar1", # scroll_navbarの判定用のkey
        anchor_labels=None, # Use anchor_ids as labels
        anchor_icons=anchor_icons,
        )

# 2. horizontal menu
st.subheader("Example 02")
scroll_navbar(
        anchor_ids,
        key = "navbar2",
        anchor_icons=anchor_icons,
        orientation="horizontal" # メニュー表記指定 無指定：縦、horizontal：横
        )

# Dummy page setup
for anchor_id in anchor_ids:
    st.subheader(anchor_id,anchor=anchor_id)
    st.write("content " * 100)