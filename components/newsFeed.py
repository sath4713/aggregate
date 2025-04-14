# components/newsFeed.py

import streamlit as st
import feedparser
import datetime
import logging
from operator import itemgetter # For sorting
from .available_feeds import get_feed_name_from_url # Helper to get name

# --- Cached Data Fetching Function (Keep As Is) ---
@st.cache_data(ttl=600) # Cache feed data for 10 minutes
def fetch_and_parse_feed(feed_url: str):
    """ Fetches and parses RSS feed. Returns parsed feed object or None. """
    logging.info(f"Cache miss. Fetching and parsing feed: {feed_url}")
    try:
        feed = feedparser.parse(feed_url)
        if feed.bozo:
            logging.warning(f"Feed at {feed_url} not well-formed: {feed.bozo_exception}")
        return feed
    except Exception as e:
        logging.error(f"Error fetching/parsing {feed_url}: {e}", exc_info=True)
        return None

# --- NEW Function to Render Multiple Feeds ---
def renderMultipleNewsFeeds(selected_urls: list, max_items_per_feed: int = 10):
    """
    Fetches, combines, sorts, and renders news items from multiple feed URLs.

    Args:
        selected_urls (list): A list of feed URLs to display.
        max_items_per_feed (int): Max items to initially fetch *per feed* before combining.
                                  The final displayed count might be less after sorting/filtering.
    """
    if not selected_urls:
        st.info("Select one or more feeds from the sidebar to build your news feed.")
        return

    all_entries = []
    errors = {}

    st.header("Your Custom News Feed")
    with st.spinner(f"Fetching news from {len(selected_urls)} sources..."):
        for url in selected_urls:
            feed = fetch_and_parse_feed(url) # Use the cached function

            if feed is None or feed.bozo: # Basic error check
                errors[url] = f"Could not fetch or parse feed."
                logging.warning(f"Skipping feed due to error/bozo: {url}")
                continue # Skip this feed

            feed_name = get_feed_name_from_url(url) or url # Get readable name or use URL

            for entry in feed.entries[:max_items_per_feed]:
                # Add source info and parsed date (if available) to each entry for sorting
                entry['source_name'] = feed_name # Add source name
                entry['source_url'] = url       # Add source url
                try:
                    # Use published_parsed for reliable sorting, fallback needed
                    entry['published_datetime'] = datetime.datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') and entry.published_parsed else None
                except Exception: # Handle potential errors during datetime creation
                    entry['published_datetime'] = None

                all_entries.append(entry)

    # --- Sort combined entries by date (most recent first) ---
    # Handle entries without a valid date (put them at the end or beginning)
    all_entries.sort(
        key=lambda x: x.get('published_datetime', datetime.datetime.min), # Sort key
        reverse=True # Most recent first
    )

    # --- Display combined and sorted entries ---
    if not all_entries:
         st.warning("No news items found from the selected sources.")
         # Optionally display errors encountered
         if errors:
             st.error("Some feeds could not be loaded:")
             for url, msg in errors.items():
                 st.caption(f"- {get_feed_name_from_url(url) or url}: {msg}")
         return

    st.write(f"Showing latest combined articles:")
    for entry in all_entries: # Consider limiting total combined articles e.g., [:50]
         # --- Title and Link ---
         title = entry.get('title', 'No Title Available')
         link = entry.get('link')
         if link:
             st.markdown(f"### [{title}]({link})")
         else:
             st.markdown(f"### {title}")

         # --- Image (using same logic as before) ---
         img_url = None
         if 'media_thumbnail' in entry and entry.media_thumbnail:
             img_url = entry.media_thumbnail[0].get('url')
         elif 'links' in entry:
              for item_link in entry.links:
                  if 'image' in item_link.get('type', ''):
                      img_url = item_link.get('href')
                      break
         if img_url:
             st.image(img_url, width=500)

         # --- Summary (using same logic as before) ---
         summary = entry.get('summary')
         if summary:
             st.markdown(summary, unsafe_allow_html=True) # Caution with untrusted sources

         # --- Published Date & Source ---
         published_str = "Date not available"
         if entry.get('published_datetime'):
             try:
                published_str = entry['published_datetime'].strftime('%a, %d %b %Y %H:%M') # Format
             except Exception: # Fallback if formatting fails
                 published_str = entry.get('published', 'Date parse error')
         elif entry.get('published'):
             published_str = entry.get('published') # Raw string fallback

         source_name = entry.get('source_name', 'Unknown Source')
         st.write(f"*Source: {source_name} | Published: {published_str}*")

         # --- Separator ---
         st.markdown("---")

    # Optionally display errors encountered at the end as well
    if errors:
        st.sidebar.error("Some feeds could not be loaded:")
        for url, msg in errors.items():
            st.sidebar.caption(f"- {get_feed_name_from_url(url) or url}")