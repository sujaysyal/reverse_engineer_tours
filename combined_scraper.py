import requests, time, json, re, sqlite3, pandas as pd, asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import quote
from playwright.async_api import async_playwright

# -------------------- SONGKICK --------------------
headers = {"User-Agent": "Mozilla/5.0"}

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
                'type': section_name,
                'source': 'Songkick'
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
                            'type': 'Past',
                            'source': 'Songkick'
                        })
                        found_event_on_page = True
            except:
                continue
        if not found_event_on_page:
            break
        time.sleep(0.3)
    return all_events

def get_songkick_data(artist_name):
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
    print(f"✅ Songkick: Scraped {len(events)} total events.")
    return events

# -------------------- CONCERT ARCHIVES --------------------
def slugify(name: str) -> str:
    return name.lower().replace("&", "and").replace(".", "").replace(",", "").replace("'", "").replace("\"", "").replace("(", "").replace(")", "").replace("–", "-").replace("—", "-").replace(" ", "-")

def build_url(slug: str, page: int = 1) -> str:
    return f"https://www.concertarchives.org/bands/{slug}" + (f"?page={page}#concert-table" if page > 1 else "")

async def scrape_concert_archives(artist_name):
    slug = slugify(artist_name)
    all_shows = []
    current_page = 1
    while True:
        url = build_url(slug, current_page)
        success = await scrape_page(url, all_shows, slug)
        if not success:
            print("🚫 No data found or error occurred.")
            break
        print(f"🎯 Concert Archives: {len(all_shows)} shows scraped so far.")
        more = input("➕ Scrape more Concert Archives pages? (y/n): ").strip().lower()
        if more != 'y':
            break
        current_page += 1
    if all_shows:
        unique = list({tuple(sorted(show.items())) for show in all_shows})
        return [dict(show) | {"artist": artist_name, "type": "Past", "source": "Concert Archives"} for show in unique]
    return []

async def scrape_page(url: str, shows: list, slug: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            try:
                await page.wait_for_selector("table tbody tr", timeout=30000)
            except:
                print("⏳ Table rows not found in time. Waiting fallback 5s...")
                await page.wait_for_timeout(5000)
        except Exception as e:
            print(f"❌ Failed to load page or data: {e}")
            await browser.close()
            return False
        try:
            rows = await page.query_selector_all("table tbody tr")
            for row in rows:
                try:
                    date = await (await row.query_selector("td:nth-child(1) span")).inner_text()
                    artist = await (await row.query_selector("td:nth-child(2) a")).inner_text()
                    venue = await (await row.query_selector("td:nth-child(3) a")).inner_text()
                    location = await (await row.query_selector("td:nth-child(4) a")).inner_text()
                    href = await (await row.query_selector("td:nth-child(2) a")).get_attribute("href")
                    shows.append({
                        "date": date.strip(),
                        "venue": venue.strip(),
                        "venue_address": "N/A",
                        "venue_city": location.strip(),
                        "venue_region": "N/A",
                        "venue_country": "N/A",
                        "venue_postal": "N/A",
                        "city": location.strip(),
                        "url": f"https://www.concertarchives.org{href}" if href else ""
                    })
                except:
                    continue
        except:
            print(f"⚠️ Error parsing concert data.")
        await browser.close()
        return True

# -------------------- MAIN --------------------
if __name__ == "__main__":
    conn = sqlite3.connect("tour_data.db")
    all_dfs = []

    while True:
        artist_name = input("🎤 Enter artist name (or type 'done' to finish): ").strip()
        if artist_name.lower() == 'done':
            break

        print(f"\n🔍 Fetching Songkick data for: {artist_name}")
        events = get_songkick_data(artist_name)

        ca_prompt = input("🎫 Would you also like concert archives for this artist? (y/n): ").strip().lower()
        if ca_prompt == 'y':
            print("⏳ Loading Concert Archives data...")
            ca_data = asyncio.run(scrape_concert_archives(artist_name))
            events.extend(ca_data)

        if not events:
            print(f"❌ No events found for {artist_name}.")
            continue

        df = pd.DataFrame(events, columns=[
            "artist", "type", "date", "venue", "venue_address", "venue_city",
            "venue_region", "venue_country", "venue_postal", "city", "url", "source"
        ])
        df = df.drop_duplicates()

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

