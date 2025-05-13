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


def renderMultipleNewsFeeds(selected_urls: list[str], max_items_per_feed: int = 10):
    """
    Fetches, combines, sorts, and renders news items from the selected RSS URLs.
    Only the XML fetch is cached; parsing runs on every render to avoid pickling issues.
    """
    # Inject compact heading CSS once
    # Inject tight CSS once
    # Inject tight CSS for expander spacing (handles different Streamlit class names)
    if not st.session_state.get("_news_css_loaded", False):
        st.markdown(
            """
            <style>
            /* Tighter spacing around each expander */
            .stExpander, .streamlit-expander {
                margin: 0.25rem 0;
            }
            /* Reduce header padding and headline margins */
            .stExpanderHeader, .streamlit-expanderHeader {
                padding-top: 0;
                padding-bottom: 0;
            }
            .stExpanderHeader h3, .streamlit-expanderHeader h3 {
                margin: 0.1rem 0;
                font-size: 1rem;
            }
            /* Tighten summary paragraph spacing */
            .stExpanderContent p, .streamlit-expanderContent p {
                margin: 0.1rem 0 0.5rem 0;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.session_state["_news_css_loaded"] = True

    if not selected_urls:
        st.info("Select one or more leagues in your Profile to see news here.")
        return

    all_entries = []
    errors = {}

    st.header("News Feed")
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
                published_dt = None
                if getattr(entry, "published_parsed", None):
                    try:
                        published_dt = datetime.datetime(*entry.published_parsed[:6])
                    except Exception:
                        pass

                all_entries.append(
                    {
                        "title": entry.get("title", "No title"),
                        "link": entry.get("link"),
                        "summary": entry.get("summary", ""),
                        "media_thumbnail": getattr(entry, "media_thumbnail", None),
                        "links": entry.get("links", []),
                        "published": entry.get("published", ""),
                        "published_datetime": published_dt,
                        "source_name": feed_name,
                        "source_url": url,
                    }
                )

    # Sort by published_datetime (desc), undated last
    all_entries.sort(
        key=lambda e: e.get("published_datetime") or datetime.datetime.min, reverse=True
    )

    if not all_entries:
        st.warning("No news items found from your selected leagues.")
        if errors:
            st.error("Some feeds failed to load:")
            for url, msg in errors.items():
                st.caption(f"- {get_feed_name_from_url(url) or url}: {msg}")
        return

    # Render each entry as a collapsible card
    for entry in all_entries:
        title = entry["title"]
        link = entry.get("link")
        pub_dt = entry.get("published_datetime")
        pub_str = (
            pub_dt.strftime("%a, %d %b %Y %H:%M")
            if pub_dt
            else entry.get("published") or "Date n/a"
        )
        source = entry.get("source_name")

        with st.expander(f"{title}  —  {source}", expanded=False):
            cols = st.columns([1, 3])
            # Thumbnail in left column
            img_url = None
            if entry.get("media_thumbnail"):
                img_url = entry["media_thumbnail"][0].get("url")
            else:
                for l in entry.get("links", []):
                    if "image" in l.get("type", ""):
                        img_url = l.get("href")
                        break
            if img_url:
                cols[0].image(img_url, use_column_width=True)

            # Content in right column
            cols[1].markdown(f"**[{title}]({link})**")
            if entry.get("summary"):
                cols[1].write(entry["summary"])
            cols[1].caption(f"Published: {pub_str}  |  Source: {source}")

        st.divider()

    # Show errors at bottom if any
    if errors:
        st.error("Some feeds failed to load:")
        for url, msg in errors.items():
            st.caption(f"- {get_feed_name_from_url(url) or url}: {msg}")
