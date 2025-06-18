import asyncio
import csv
from urllib.parse import quote
from playwright.async_api import async_playwright

# Convert artist name to a URL-friendly slug
def slugify(name: str) -> str:
    return (
        name.lower()
        .replace("&", "and")
        .replace(".", "")
        .replace(",", "")
        .replace("'", "")
        .replace("\"", "")
        .replace("(", "")
        .replace(")", "")
        .replace("–", "-")
        .replace("—", "-")
        .replace(" ", "-")
    )

# Build URL for a given artist and page number
def build_url(slug: str, page: int = 1) -> str:
    base = f"https://www.concertarchives.org/bands/{slug}"
    return base if page == 1 else f"{base}?page={page}#concert-table"

# Save data to CSV
def save_to_csv(filename: str, data: list):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Date", "Artist/Show Name", "Venue", "Location", "Concert URL"])
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ Saved to CSV: {filename}")

# Scrape one page of concert data
async def scrape_page(url: str, shows: list):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121 Safari/537.36"
        )
        page = await context.new_page()

        print("🌐 Scraping concerts...")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_selector("table tbody tr", timeout=15000)
        except Exception as e:
            print(f"❌ Failed to load page or data: {e}")
            await browser.close()
            return False

        print("📄 Parsing concert data...")
        found_data = False
        try:
            rows = await page.query_selector_all("table tbody tr")
            if not rows:
                print("⚠️ No concerts found on this page.")
            else:
                found_data = True
                for row in rows:
                    try:
                        date_el = await row.query_selector("td:nth-child(1) span")
                        artist_el = await row.query_selector("td:nth-child(2) a")
                        venue_el = await row.query_selector("td:nth-child(3) a")
                        location_el = await row.query_selector("td:nth-child(4) a")

                        if not all([date_el, artist_el, venue_el, location_el]):
                            continue

                        date = await date_el.inner_text()
                        artist = await artist_el.inner_text()
                        venue = await venue_el.inner_text()
                        location = await location_el.inner_text()
                        concert_href = await artist_el.get_attribute("href")
                        concert_url = f"https://www.concertarchives.org{concert_href}" if concert_href else ""

                        shows.append({
                            "Date": date.strip(),
                            "Artist/Show Name": artist.strip(),
                            "Venue": venue.strip(),
                            "Location": location.strip(),
                            "Concert URL": concert_url
                        })
                    except Exception as e:
                        print("⚠️ Skipping row due to issue:", e)
        except Exception as e:
            print(f"⚠️ Error parsing data: {e}")

        await browser.close()
        return found_data

# Main flow
async def main():
    artist_name = input("🎤 Enter artist name: ").strip()
    slug = slugify(artist_name)
    name_base = slug.replace("-", "_")
    csv_filename = f"{name_base}.csv"
    all_shows = []
    current_page = 1

    while True:
        url = build_url(slug, current_page)
        success = await scrape_page(url, all_shows)

        if not success:
            print("🚫 Stopping — no data on this page or an error occurred.")
            break

        print(f"🎯 Shows scraped so far: {len(all_shows)}")
        another = input("➕ Scrape more? (y/n): ").strip().lower()
        if another != 'y':
            break

        current_page += 1

    if all_shows:
        # 🧼 Remove duplicates
        unique_shows = list({tuple(sorted(show.items())) for show in all_shows})
        unique_shows = [dict(show) for show in unique_shows]

        duplicates_removed = len(all_shows) - len(unique_shows)
        print(f"🧹 Removed {duplicates_removed} duplicate rows.")
        save_to_csv(csv_filename, unique_shows)
        print(f"✅ Successfully saved {len(unique_shows)} concerts to CSV.")
    else:
        print("🚫 No concert data was scraped.")

# Run it
asyncio.run(main())

