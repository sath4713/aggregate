import streamlit as st
from components.feedSelector import renderFeedSelector
from components.newsFeed import renderNewsFeed

st.title("📰 Sports News Feed")

# Define feeds dictionary (could move to config later)
feeds = {
    "ESPN": "https://www.espn.com/espn/rss/news",
    "BBC Sport": "http://feeds.bbci.co.uk/sport/rss.xml?edition=uk",
    "Sky Sports": "https://www.skysports.com/rss/12040",
}

# Sidebar for feed selection
selectedFeed = renderFeedSelector(feeds)

# Display the selected feed
renderNewsFeed(selectedFeed, feeds)
