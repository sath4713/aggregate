# app.py
import streamlit as st
from components.feedSelector import renderFeedSelector
from components.newsFeed import renderNewsFeed
from components.feeds import feeds  # Import the feeds from the new component

st.title("📰 Sports News Feed")

# Sidebar for feed selection
selectedFeed = renderFeedSelector(feeds)

# Display the selected feed
renderNewsFeed(selectedFeed, feeds)
