import streamlit as st
import requests
import feedparser
import datetime
import logging
from bs4 import BeautifulSoup
import re
from .available_feeds import get_feed_name_from_url


# Cache only the raw feed text
@st.cache_data(ttl=600)
def fetch_feed_text(feed_url: str) -> str | None:
    """Fetches the RSS XML as text (cached)."""
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X)"}
    try:
        resp = requests.get(feed_url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logging.error(f"Error fetching feed {feed_url}: {e}")
        return None


def renderMultipleNewsFeeds(selected_urls: list[str], max_items_per_feed: int = 10):
    """
    Fetches, combines, sorts, and renders news items from selected RSS URLs.
    Displays each entry as a simple card: headline, large image, summary, and metadata.
    Attempts multiple strategies to extract images (thumbnail, media_content, enclosures, content, summary).
    """
    if not selected_urls:
        st.info("Select leagues in Profile to see news.")
        return

    all_entries = []
    errors = {}

    st.header("Headlines")
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

            source = get_feed_name_from_url(url) or url
            for entry in feed.entries[:max_items_per_feed]:
                # parse publication date
                pub_dt = None
                if getattr(entry, "published_parsed", None):
                    try:
                        pub_dt = datetime.datetime(*entry.published_parsed[:6])
                    except Exception:
                        pass

                # extract image using multiple strategies
                img_url = None
                # 1) media_thumbnail
                if getattr(entry, "media_thumbnail", None):
                    img_url = entry.media_thumbnail[0].get("url")
                # 2) media_content
                if not img_url and getattr(entry, "media_content", None):
                    img_url = entry.media_content[0].get("url")
                # 3) enclosures
                if not img_url and getattr(entry, "enclosures", None):
                    for enc in entry.enclosures:
                        if enc.get("type", "").startswith("image"):
                            img_url = enc.get("href") or enc.get("url")
                            break
                # 4) content (HTML blocks)
                if not img_url and getattr(entry, "content", None):
                    for cont in entry.content:
                        soup0 = BeautifulSoup(cont.get("value", ""), "html.parser")
                        tag = soup0.find("img")
                        if tag and tag.get("src"):
                            img_url = tag["src"]
                            break
                # 5) fallback: first <img> in summary
                if not img_url:
                    soup1 = BeautifulSoup(entry.get("summary", ""), "html.parser")
                    tag = soup1.find("img")
                    if tag and tag.get("src"):
                        img_url = tag.get("src")

                # extract plain text summary
                summary_text = BeautifulSoup(
                    entry.get("summary", ""), "html.parser"
                ).get_text()

                summary_text = re.sub(r'\s*Read More.*$', '', summary_text, flags=re.DOTALL)
                summary_text = re.sub(r'\s*The post.*appeared first on.*$', '', summary_text, flags=re.DOTALL)

                all_entries.append(
                    {
                        "title": entry.get("title", "No title"),
                        "link": entry.get("link"),
                        "summary": summary_text,
                        "img_url": img_url,
                        "published_datetime": pub_dt,
                        "published": entry.get("published", ""),
                        "source_name": source,
                    }
                )

    # sort by date desc, undated last
    all_entries.sort(
        key=lambda e: e.get("published_datetime") or datetime.datetime.min, reverse=True
    )

    if not all_entries:
        st.warning("No news items found from selected leagues.")
        if errors:
            st.error("Some feeds failed to load:")
            for url, msg in errors.items():
                name = get_feed_name_from_url(url) or url
                st.caption(f"- {name}: {msg}")
        return

    # render entries
    for entry in all_entries:
        title = entry["title"]
        link = entry["link"]
        summary = entry.get("summary", "")
        img_url = entry.get("img_url")
        pub_dt = entry.get("published_datetime")
        pub_str = (
            entry["published_datetime"].strftime("%a, %d %b %Y %H:%M")
            if entry.get("published_datetime")
            else entry.get("published") or "Date n/a"
        )
        source = entry.get("source_name")

        # Headline
        if link:
            st.markdown(f"### [{title}]({link})")
        else:
            st.markdown(f"### {title}")

        # Large image
        if img_url:
            st.image(img_url, width=500)

        # Summary
        if summary:
            st.write(summary)

        # Metadata
        st.write(f"*Source: {source} | Published: {pub_str}*")

        # Divider
        st.markdown("---")

    # show errors in sidebar
    if errors:
        st.sidebar.error("Some feeds failed to load:")
        for url, msg in errors.items():
            name = get_feed_name_from_url(url) or url
            st.sidebar.caption(f"- {name}: {msg}")
