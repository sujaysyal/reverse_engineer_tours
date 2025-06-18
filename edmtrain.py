import pandas as pd
import sqlite3
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright

def get_first_edmtrain_url_from_user():
    artist_url = input("🔗 Enter EDMTrain tour URL (e.g. https://edmtrain.com/tours/artist-name-id): ").strip()
    if re.match(r"^https://edmtrain\.com/tours/[a-z0-9\-]+-\d+$", artist_url):
        print(f"✅ Using direct EDMTrain URL: {artist_url}")
        return artist_url
    print("❌ Invalid EDMTrain tour URL format.")
    return None

def get_artist_events(artist_url, artist_name, page):
    print(f"🌐 Fetching: {artist_url}")
    page.goto(artist_url, timeout=60000)
    page.wait_for_timeout(3000)
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.select("a.event.callout")
    print(f"🔍 Found {len(rows)} events for {artist_name}")

    events = []
    for row in rows:
        try:
            title_el = row.select_one("div.eventTitle")
            date_el = row.select_one("time[itemprop='startDate']")
            if not (title_el and date_el):
                continue

            location = title_el.get_text(strip=True)
            date = date_el.get("datetime", "N/A")
            city, venue = ("", location.strip())
            if " - " in location:
                city, venue = [s.strip() for s in location.split(" - ", 1)]

            events.append({
                "artist": artist_name.strip(),
                "type": "EDMTrainDirect",
                "date": date.strip(),
                "venue": venue,
                "venue_city": city,
                "url": artist_url
            })
        except Exception as e:
            print(f"⚠️ Failed to parse event: {e}")
    return events

# 🏁 MAIN
if __name__ == "__main__":
    conn = sqlite3.connect("edmtrain_google_scraped.db")
    all_dfs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US"
        )

        while True:
            artist_name = input("🎤 Enter artist name (or 'done' to finish): ").strip()
            if artist_name.lower() == 'done':
                break

            artist_url = get_first_edmtrain_url_from_user()
            if not artist_url:
                continue

            events = get_artist_events(artist_url, artist_name, page)
            if not events:
                print(f"⚠️ No events found for {artist_name}")
                continue

            df = pd.DataFrame(events).drop_duplicates()
            table_name = re.sub(r'\W+', '_', artist_name.lower())
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"✅ Saved {len(df)} events to '{table_name}' table")
            all_dfs.append(df)
            time.sleep(0.5)

        browser.close()

    conn.close()

    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"edmtrain_google_scraped_{timestamp}.csv"
        combined_df.to_csv(csv_filename, index=False)
        print(f"\n📁 Combined CSV saved as: {csv_filename}")
    else:
        print("⚠️ No data to save")

    print("🏁 Done.")

