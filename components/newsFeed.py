import streamlit as st
import feedparser

def renderNewsFeed(selectedFeed, feeds):
    feedUrl = feeds[selectedFeed]
    feed = feedparser.parse(feedUrl)

    st.subheader(f"{selectedFeed} Headlines")

    for entry in feed.entries:
        # Display the image if available
        if 'media_thumbnail' in entry:
            for media in entry.media_thumbnail:
                st.image(media['url'], width=500)  # Display image with a fixed width
        
        # Display the title and link
        st.markdown(f"### [{entry.title}]({entry.link})")
        
        # Display the summary if available
        if hasattr(entry, 'summary'):
            st.write(entry.summary)
        
        # Display the publish date if available
        if hasattr(entry, 'published'):
            st.write(f"*Published on: {entry.published}*")
        
        st.markdown("---")
