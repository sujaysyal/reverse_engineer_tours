from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

def scrape_ra_events(artist):
    url = f"https://ra.co/dj/{artist}/past-events"
    all_events = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # set to False to debug
        page = browser.new_page()
        print(f"🌐 Visiting: {url}")
        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)

        # ⬇️ Scroll to load more events (repeat if needed)
        for _ in range(3):
            page.mouse.wheel(0, 5000)
            page.wait_for_timeout(1500)

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        event_blocks = soup.select("li[class*='Column-sc']")  # updated generic selector
        print(f"🔍 Found {len(event_blocks)} events for {artist}")

        if not event_blocks:
            print("⚠️ No events found. Dumping HTML for debugging.")
            with open("debug_ra_page.html", "w", encoding="utf-8") as f:
                f.write(html)

        for event in event_blocks:
            try:
                date_el = event.select_one("span.loAMdA")
                title_el = event.select_one("h3 a span")
                link_el = event.select_one("h3 a")
                city_el = event.select_one("a[href*='/events/'] span")
                venue_el = event.select_one("a[data-pw-test-id='event-venue-link'] span")

                date = date_el.text.strip() if date_el else ""
                title = title_el.text.strip() if title_el else ""
                city = city_el.text.strip() if city_el else ""
                venue = venue_el.text.strip() if venue_el else ""
                link = link_el['href'] if link_el and link_el.has_attr('href') else ""

                if link.startswith("/"):
                    link = f"https://ra.co{link}"

                all_events.append({
                    "date": date,
                    "title": title,
                    "city": city,
                    "venue": venue,
                    "link": link
                })
            except Exception as e:
                print(f"⚠️ Failed to parse an event: {e}")

        browser.close()

    return all_events

# 🏁 MAIN
if __name__ == "__main__":
    artist = input("🎤 Enter RA artist name (e.g. justinpaul): ").strip().lower()
    events = scrape_ra_events(artist)

    df = pd.DataFrame(events)
    filename = f"{artist}_ra_events.csv"
    df.to_csv(filename, index=False)
    print(f"✅ Saved {len(df)} events to {filename}")
