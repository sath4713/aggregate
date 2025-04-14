# app.py
import streamlit as st
import logging

# Import the new components
from components.feedSelector import renderFeedSelector
from components.newsFeed import renderMultipleNewsFeeds
# available_feeds is used implicitly by feedSelector now

# --- Basic Logging Configuration --- (Optional but recommended)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Streamlit App Layout ---
st.set_page_config(layout="wide") # Use wide layout for better news display

st.title("📰 Your Custom Sports News Feed")
st.caption("Select your favorite feeds from the sidebar to build your personalized news stream.")

# --- Sidebar for feed selection ---
# The selector now manages its state via session_state and returns the selected list
selected_urls = renderFeedSelector()

# --- Main Area for Displaying Feeds ---
# Pass the list of selected URLs to the rendering function
renderMultipleNewsFeeds(selected_urls, max_items_per_feed=10) # Adjust max items per feed if needed

# --- Optional: Footer or other info ---
# st.sidebar.info("Your selections are saved for this session.")