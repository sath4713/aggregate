import streamlit as st
import feedparser

def renderNewsFeed(selectedFeed, feeds):
    feedUrl = feeds[selectedFeed]
    feed = feedparser.parse(feedUrl)

    st.subheader(f"{selectedFeed} Headlines")

    for entry in feed.entries:
        st.markdown(f"### [{entry.title}]({entry.link})")
        if hasattr(entry, 'summary'):
            st.write(entry.summary)
        if hasattr(entry, 'published'):
            st.write(f"*Published on: {entry.published}*")
        st.markdown("---")
