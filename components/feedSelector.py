import streamlit as st

def renderFeedSelector(feeds):
    selectedFeed = st.sidebar.selectbox("Select a news source", list(feeds.keys()))
    return selectedFeed
