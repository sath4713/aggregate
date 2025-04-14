# components/feedSelector.py
import streamlit as st
from .available_feeds import available_feeds # Import the structure

def renderFeedSelector():
    """
    Renders checkboxes for feed selection, grouped by sport/league.
    Manages selected feeds using st.session_state.
    Returns the list of currently selected feed URLs.
    """
    st.sidebar.header("Customize Your Feed")

    # Initialize session state for selected feeds if it doesn't exist
    if 'selected_feed_urls' not in st.session_state:
        st.session_state.selected_feed_urls = [] # Start with empty list

    # --- Callback function to update selection ---
    def update_selection(url, is_checked):
        current_selection = st.session_state.selected_feed_urls
        if is_checked and url not in current_selection:
            st.session_state.selected_feed_urls.append(url)
        elif not is_checked and url in current_selection:
            st.session_state.selected_feed_urls.remove(url)
        # No need to return anything, modifies session_state directly

    # --- Render checkboxes ---
    # Keep track of rendered URLs to avoid duplicates if any exist in the source dict
    rendered_urls = set()

    for sport, content in available_feeds.items():
        with st.sidebar.expander(f"**{sport}**", expanded=False): # Use expanders for sports
            if isinstance(content, list): # Sport has a direct list of feeds
                for feed in content:
                    if feed['url'] not in rendered_urls:
                        is_selected = feed['url'] in st.session_state.selected_feed_urls
                        st.checkbox(
                            feed['name'],
                            value=is_selected,
                            key=f"cb_{feed['url']}", # Unique key for each checkbox
                            # Use args to pass necessary info to the callback
                            on_change=update_selection,
                            args=(feed['url'], not is_selected) # Pass URL and the *new* state
                        )
                        rendered_urls.add(feed['url'])

            elif isinstance(content, dict): # Sport has leagues
                for league, feeds in content.items():
                    st.subheader(f"*{league}*") # Display league name
                    for feed in feeds:
                         if feed['url'] not in rendered_urls:
                            is_selected = feed['url'] in st.session_state.selected_feed_urls
                            st.checkbox(
                                feed['name'],
                                value=is_selected,
                                key=f"cb_{feed['url']}",
                                on_change=update_selection,
                                args=(feed['url'], not is_selected)
                            )
                            rendered_urls.add(feed['url'])
                    st.markdown("---") # Separator between leagues

    # Return the current list of selected URLs (read directly from session state)
    return st.session_state.selected_feed_urls