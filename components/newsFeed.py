# components/newsFeed.py
import streamlit as st
import requests
import feedparser
import datetime
import logging
from .available_feeds import get_feed_name_from_url

# 1) Cache only the raw feed text
@st.cache_data(ttl=600)
def fetch_feed_text(feed_url: str) -> str | None:
    """Fetches the RSS XML as text (cached), with a browser User‑Agent."""
    logging.info(f"Cache miss fetching feed text: {feed_url}")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/100.0.4896.127 Safari/537.36"
        )
    }
    try:
        resp = requests.get(feed_url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.text
    except requests.exceptions.HTTPError as e:
        # If ESPN returns 403, try HTTP instead of HTTPS
        if e.response.status_code in (403, 401) and feed_url.startswith("https://"):
            try:
                alt_url = feed_url.replace("https://", "http://", 1)
                logging.info(f"Retrying via HTTP for {alt_url}")
                resp = requests.get(alt_url, headers=headers, timeout=10)
                resp.raise_for_status()
                return resp.text
            except Exception as e2:
                logging.error(f"Retry HTTP failed for {alt_url}: {e2}", exc_info=True)
        logging.error(f"Error fetching {feed_url}: {e}", exc_info=True)
        return None
    except Exception as e:
        logging.error(f"Error fetching {feed_url}: {e}", exc_info=True)
        return None

def renderMultipleNewsFeeds(selected_urls: list, max_items_per_feed: int = 10):
    """
    Fetches, combines, sorts, and renders news items from the selected RSS URLs.
    Only the XML fetch is cached; parsing runs on every render to avoid pickling issues.
    """
    if not selected_urls:
        st.info("Select one or more leagues in your Profile to see news here.")
        return

    all_entries = []
    errors = {}

    st.header("🗞️ Your Custom News Feed")
    with st.spinner(f"Fetching news from {len(selected_urls)} sources..."):
        for url in selected_urls:
            xml = fetch_feed_text(url)
            if not xml:
                errors[url] = "Failed to fetch feed."
                continue

            feed = feedparser.parse(xml)
            if feed.bozo:
                errors[url] = f"Malformed feed: {feed.bozo_exception}"
                logging.warning(f"Skipping malformed feed {url}: {feed.bozo_exception}")
                continue

            feed_name = get_feed_name_from_url(url) or url
            for entry in feed.entries[:max_items_per_feed]:
                # Build a plain dict of only the fields we need
                published_dt = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        published_dt = datetime.datetime(*entry.published_parsed[:6])
                    except Exception:
                        published_dt = None

                all_entries.append({
                    'title':              entry.get('title', 'No title'),
                    'link':               entry.get('link'),
                    'summary':            entry.get('summary', ''),
                    'media_thumbnail':    getattr(entry, 'media_thumbnail', None),
                    'links':              entry.get('links', []),
                    'published':          entry.get('published', ''),
                    'published_datetime': published_dt,
                    'source_name':        feed_name,
                    'source_url':         url
                })

    # Sort by published_datetime (desc), putting undated entries last
    all_entries.sort(
        key=lambda e: e.get('published_datetime') or datetime.datetime.min,
        reverse=True
    )

    # Render
    if not all_entries:
        st.warning("No news items found from your selected leagues.")
        if errors:
            st.error("Some feeds failed to load:")
            for url, msg in errors.items():
                st.caption(f"- {get_feed_name_from_url(url) or url}: {msg}")
        return

    st.write(f"Showing the latest combined articles:")
    for entry in all_entries:
        title = entry['title']
        link  = entry['link']
        if link:
            st.markdown(f"### [{title}]({link})")
        else:
            st.markdown(f"### {title}")

        # Image
        img_url = None
        if entry['media_thumbnail']:
            img_url = entry['media_thumbnail'][0].get('url')
        else:
            for l in entry['links']:
                if 'image' in l.get('type',''):
                    img_url = l.get('href')
                    break
        if img_url:
            st.image(img_url, width=500)

        # Summary
        if entry['summary']:
            st.markdown(entry['summary'], unsafe_allow_html=True)

        # Date & Source
        pub_str = "Date n/a"
        if entry['published_datetime']:
            pub_str = entry['published_datetime'].strftime('%a, %d %b %Y %H:%M')
        elif entry['published']:
            pub_str = entry['published']
        st.write(f"*Source: {entry['source_name']} | Published: {pub_str}*")

        st.markdown("---")

    # Sidebar errors
    if errors:
        st.sidebar.error("Some feeds failed:")
        for url, msg in errors.items():
            st.sidebar.caption(f"- {get_feed_name_from_url(url) or url}: {msg}")
