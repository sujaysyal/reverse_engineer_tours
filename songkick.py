import requests
from bs4 import BeautifulSoup
import time
import json
import pandas as pd
import sqlite3
import re
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0"
}

def find_songkick_artist_url(artist_name):
    search_url = f"https://www.songkick.com/search?query={artist_name.replace(' ', '+')}"
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        return None, f"Search failed: {response.status_code}"

    soup = BeautifulSoup(response.text, 'html.parser')
    for link in soup.select('li a[href^="/artists/"]'):
        if artist_name.lower() in link.text.strip().lower():
            return "https://www.songkick.com" + link['href'], None

    return None, f"Artist '{artist_name}' not found on Songkick"

def scrape_events_from_page(url, section_name):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return [], f"Failed to fetch {section_name} page: {response.status_code}"

    soup = BeautifulSoup(response.text, 'html.parser')
    events = []

    for li in soup.select('li.concert'):
        date = li.select_one('.date strong')
        venue = li.select_one('.location .venue-name')
        city = li.select_one('.location .location')
        link = li.select_one('a.event-link')

        if date and venue and city and link:
            events.append({
                'date': date.text.strip(),
                'venue': venue.text.strip(),
                'venue_address': 'N/A',
                'venue_city': city.text.strip(),
                'venue_region': 'N/A',
                'venue_country': 'N/A',
                'venue_postal': 'N/A',
                'city': city.text.strip(),
                'url': "https://www.songkick.com" + link['href'],
                'type': section_name
            })

    return events, None

def scrape_all_past_events(artist_url, max_pages=50):
    all_events = []
    base_url = artist_url.rstrip('/') + "/gigography"

    for page_num in range(1, max_pages + 1):
        paged_url = f"{base_url}?page={page_num}"
        response = requests.get(paged_url, headers=headers)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all("script", type="application/ld+json")

        found_event_on_page = False
        for script in scripts:
            try:
                data = json.loads(script.string)
                events = data if isinstance(data, list) else [data]

                for event in events:
                    if event.get('@type') == 'MusicEvent':
                        location = event.get('location', {})
                        address = location.get('address', {})

                        all_events.append({
                            'date': event.get('startDate', 'N/A'),
                            'venue': location.get('name', 'N/A'),
                            'venue_address': address.get('streetAddress', 'N/A'),
                            'venue_city': address.get('addressLocality', 'N/A'),
                            'venue_region': address.get('addressRegion', 'N/A'),
                            'venue_country': address.get('addressCountry', 'N/A'),
                            'venue_postal': address.get('postalCode', 'N/A'),
                            'city': address.get('addressLocality', 'N/A'),
                            'url': event.get('url', artist_url),
                            'type': 'Past'
                        })

                        found_event_on_page = True

            except (json.JSONDecodeError, TypeError):
                continue

        if not found_event_on_page:
            break

        time.sleep(0.3)

    return all_events

def get_tour_data_for_artist(artist_name):
    artist_url, error = find_songkick_artist_url(artist_name)
    if error:
        print(f"⚠️ {artist_name}: {error}")
        return []

    print(f"🔗 Found artist page: {artist_url}")
    print("🎟️ Scraping all concert data for your chosen artist...")

    upcoming, _ = scrape_events_from_page(artist_url, "Upcoming")
    past = scrape_all_past_events(artist_url)

    events = upcoming + past
    for e in events:
        e["artist"] = artist_name

    return events

# 🏁 MAIN
if __name__ == "__main__":
    conn = sqlite3.connect("tour_data.db")
    all_dfs = []

    while True:
        artist_name = input("🎤 Enter artist name (or type 'done' to finish): ").strip()
        if artist_name.lower() == 'done':
            break

        print(f"\n🔍 Fetching data for: {artist_name}")
        events = get_tour_data_for_artist(artist_name)
        if not events:
            print(f"❌ No events found for {artist_name}.")
            continue

        df = pd.DataFrame(events, columns=[
            "artist", "type", "date", "venue", "venue_address", "venue_city",
            "venue_region", "venue_country", "venue_postal", "city", "url"
        ])
        df = df.drop_duplicates()

        # Sanitize table name for SQLite
        table_name = re.sub(r'\W+', '_', artist_name.lower())
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"✅ Saved {len(df)} events to table '{table_name}' in database.")

        all_dfs.append(df)
        time.sleep(0.5)

    conn.close()

    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"all_tour_data_{timestamp}.csv"
        combined_df.to_csv(csv_filename, index=False)
        print(f"📁 Combined CSV saved as '{csv_filename}' with {len(combined_df)} total events.")
    else:
        print("⚠️ No data to save to CSV.")

    print("🏁 Done. All artist data saved.")

