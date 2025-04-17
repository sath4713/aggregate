# components/available_feeds.py

# Define available RSS feed URLs, grouped by sport and league where applicable.
# Structure: { Sport: { League: [ {name: str, url: str}, ... ] } }
# Or:        { Sport: [ {name: str, url: str}, ... ] }

available_feeds = {
    "Football": {
        "NFL": [
            {'name': 'NFL - The Athletic', 'url': 'https://www.nytimes.com/athletic/rss/nfl/'},
            {'name': 'NFL - ESPN', 'url': 'https://www.espn.com/espn/rss/nfl/news'},
        ],
        "CollegeFootball": [
            {'name': 'College Football - The Athletic', 'url': 'https://www.nytimes.com/athletic/rss/college-football/'},
            {'name': 'College Football - ESPN', 'url': 'https://www.espn.com/espn/rss/ncf/news'},
        ],
    },
    "Climbing": [ # Simple list, no leagues
        {'name': '8a.nu', 'url': 'https://ecstrema.github.io/8a-RSS-feed/rss.xml'},
        {'name': 'Gripped Magazine', 'url': 'https://gripped.com/feed/'},
        # Note: BBC Tennis seems misplaced here, moved to Tennis
    ],
    "Running": [ # Simple list
        {'name': 'Lets Run', 'url': 'https://www.letsrun.com/feed/'},
        {'name': 'Run247', 'url': 'https://run247.com/feed'},
    ],
    "Soccer": {
        "Bundesliga": [
            {'name': 'Bundesliga - The Athletic', 'url': 'https://www.nytimes.com/athletic/rss/bundesliga/'},
            {'name': 'Bundesliga - The Guardian', 'url': 'http://www.guardian.co.uk/football/bundesligafootball/rss'},
        ],
        "ChampionsLeague": [
            {'name': 'Champions League - The Athletic', 'url': 'https://www.nytimes.com/athletic/rss/champions-league/'},
        ],
        "PremierLeague": [
            {'name': 'Premier League - ESPN', 'url': 'http://www.espnfc.com/english-premier-league/23/rss'},
            {'name': 'Premier League - The Athletic', 'url': 'https://www.nytimes.com/athletic/rss/premier-league/'},
        ],
        "MLS": [
            {'name': 'MLS - Yahoo News', 'url': 'http://sports.yahoo.com/mls/rss.xml'},
        ],
        "SerieA": [ # Added Serie A from later in the list
             {'name': 'Serie A - The Athletic', 'url': 'https://theathletic.com/serie-a/?rss=1'},
        ],
        "LaLiga": [ # Added La Liga from later in the list
             {'name': 'La Liga - The Athletic', 'url': 'https://www.nytimes.com/athletic/rss/la-liga/'},
             {'name': 'La Liga - The Guardian', 'url': 'http://www.guardian.co.uk/football/laligafootball/rss'},
        ],
         "GeneralSoccer": [
            {'name': 'General Soccer - ESPN', 'url': 'https://www.espn.com/espn/rss/soccer/news'},
            {'name': 'General Soccer - Soccer News', 'url': 'https://www.soccernews.com/feed/'},
            {'name': 'General Soccer - The Athletic', 'url': 'https://www.nytimes.com/athletic/rss/football/'},
        ],
    },
    "Cycling": [ # Simple list
        {'name': 'CyclingWeekly', 'url': 'https://www.cyclingweekly.com/feeds.xml'},
        {'name': 'CyclingNews', 'url': 'https://airedale.futurecdn.net/feeds/en_US_feed_271bdec3.rss'},
    ],
    "General": [ # Simple list
        {'name': 'ESPN', 'url': 'https://sports.espn.go.com/espn/rss/news'},
        {'name': 'The Athletic', 'url': 'https://www.nytimes.com/athletic/rss/news/'},
        {'name': 'Sports Business - The Athletic', 'url': 'https://www.nytimes.com/athletic/rss/sports-business/'},
        # Duplicate 'Top Stories - ESPN' removed as it's likely same as first ESPN link
    ],
    "Basketball": {
        "NCAAM": [
            {'name': 'NCAAM - Yahoo Sports', 'url': 'https://sports.yahoo.com/ncaab/rss.xml'},
            {'name': 'NCAAB - ESPN', 'url': 'https://www.espn.com/espn/rss/ncb/news'}, # Combined NCAAB/NCAAM ESPN
            {'name': 'NCAAM - The Athletic', 'url': 'https://www.nytimes.com/athletic/rss/college-basketball/'},
            {'name': 'NCAAB - The Score', 'url': 'http://feeds.thescore.com/ncaab.rss'},
        ],
        "NCAAW": [
            {'name': 'NCAAW - ESPN', 'url': 'https://www.espn.com/espn/rss/ncw/news'},
        ],
        "NBA": [
            {'name': 'NBA - ESPN', 'url': 'https://www.espn.com/espn/rss/nba/news'},
            {'name': 'NBA - The Athletic', 'url': 'https://www.nytimes.com/athletic/rss/nba/'},
        ],
    },
    "Combat": {
        "Boxing": [
            #{'name': 'Boxing - Fight News', 'url': 'http://www.fightnews.com/feed'},
            {'name': 'Boxing - ESPN', 'url': 'https://www.espn.com/espn/rss/boxing/news'},
        ],
        "UFC_MMA": [ # Combined UFC/MMA
            {'name': 'UFC News - UFC', 'url': 'https://www.ufc.com/rss/news'},
            {'name': 'MMA - ESPN', 'url': 'https://www.espn.com/espn/rss/mma/news'},
        ],
    },
    "Baseball": {
        "MLB": [
            {'name': 'MLB - ESPN', 'url': 'https://www.espn.com/espn/rss/mlb/news'},
            {'name': 'MLB - The Athletic', 'url': 'https://www.nytimes.com/athletic/rss/mlb/'},
        ],
    },
    "Motorsports": {
        "GeneralRPM": [ # Combined general RPM/NASCAR
             {'name': 'RPM - ESPN', 'url': 'https://www.espn.com/espn/rss/rpm/news'},
             # NASCAR link seems identical, removed duplicate
        ],
        "F1": [
            {'name': 'F1 - ESPN', 'url': 'https://www.espn.com/espn/rss/f1/news'},
        ],
    },
    "Tennis": [ # Simple list
        {'name': 'ESPN', 'url': 'https://www.espn.com/espn/rss/tennis/news'},
        {'name': 'The Athletic', 'url': 'https://www.nytimes.com/athletic/rss/tennis/'},
        {'name': 'BBC Sport Tennis', 'url': 'https://feeds.bbci.co.uk/sport/tennis/rss.xml' }, # Moved from Climbing
    ],
    "Hockey": {
        "NHL": [
            {'name': 'NHL - ESPN', 'url': 'https://www.espn.com/espn/rss/nhl/news'},
            {'name': 'NHL - The Athletic', 'url': 'https://www.nytimes.com/athletic/rss/nhl/'},
        ],
    },
    "Olympics": [ # Simple list
        {'name': 'ESPN', 'url': 'https://www.espn.com/espn/rss/oly/news'},
        {'name': 'The Athletic', 'url': 'https://www.nytimes.com/athletic/rss/olympics/'},
    ],
    "Golf": [ # Simple list
        {'name': 'ESPN', 'url': 'https://www.espn.com/espn/rss/golf/news'},
        {'name': 'The Athletic', 'url': 'https://www.nytimes.com/athletic/rss/golf/'},
    ],
}

# Helper function to get a flat list of all feed dicts {name: url:}
def get_all_feeds_flat():
    flat_list = []
    for sport, content in available_feeds.items():
        if isinstance(content, list): # Simple list of feeds for the sport
            flat_list.extend(content)
        elif isinstance(content, dict): # Dictionary of leagues for the sport
            for league, feeds in content.items():
                flat_list.extend(feeds)
    return flat_list

# Helper function to get feed name from URL
def get_feed_name_from_url(url: str) -> str | None:
     for feed in get_all_feeds_flat():
         if feed['url'] == url:
             return feed['name']
     return None