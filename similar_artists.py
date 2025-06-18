# spotify_similar_artists.py

import os
import time
import spotipy
import statistics
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import quote
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

# Load client credentials from .env file
load_dotenv()
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
))

headers = {"User-Agent": "Mozilla/5.0"}

# --- Get Artist Info ---
def get_artist(artist_name):
    result = sp.search(q=f"artist:{artist_name}", type="artist")['artists']['items']
    return result[0] if result else None

# --- Audio Summary ---
def get_audio_summary(artist_id):
    top_tracks = sp.artist_top_tracks(artist_id, country='US')['tracks']
    features = [{'popularity': t['popularity'], 'explicit': t['explicit']} for t in top_tracks[:10]]

    def avg(key):
        values = [f[key] for f in features if f and f.get(key) is not None]
        return round(statistics.mean(values), 2) if values else "N/A"

    return {
        "Avg Popularity": avg("popularity"),
        "Avg Explicitness": avg("explicit")
    }

# --- Custom Similar Artists ---
def get_custom_similar_artists(seed_artist):
    seed_id = seed_artist['id']
    seed_followers = seed_artist['followers']['total']
    seed_popularity = seed_artist['popularity']
    seed_audio = get_audio_summary(seed_id)
    seed_avg_popularity = seed_audio["Avg Popularity"]
    seed_explicit = seed_audio["Avg Explicitness"]
    seed_genres = seed_artist.get('genres', [])
    has_genres = bool(seed_genres)

    print(f"\n🔁 Searching for similar artists...")
    candidates = []

    # 1. Spotify Related Artists
    try:
        print("🎯 Trying Spotify's related artists API...")
        related = sp.artist_related_artists(seed_id)['artists']
        if related:
            candidates.extend(related)
            print(f"✅ Pulled {len(related)} related artists from Spotify.")
    except Exception as e:
        print(f"⚠️ Related artists API failed: {e}")

    # 2. Genre-Based
    if has_genres:
        print("🔁 Adding genre-based candidates...")
        for genre in seed_genres:
            try:
                print(f"🔍 Searching genre: {genre}")
                res = sp.search(q=f"genre:{quote(genre)}", type="artist", limit=50)
                candidates.extend(res['artists']['items'])
                time.sleep(1)
            except Exception as e:
                print(f"❌ Genre search failed: {e}")
                time.sleep(1)

    # 3. Popularity-Based Fallback
    if not has_genres or not candidates:
        print("🧭 Falling back to popularity-based search...")
        try:
            res = sp.search(q="year:2023", type="artist", limit=50)
            candidates.extend(res['artists']['items'])
            print(f"✅ Pulled {len(res['artists']['items'])} fallback artists.")
            time.sleep(1)
        except Exception as e:
            print(f"❌ Fallback search failed: {e}")

    print(f"🎯 Total candidates pulled (pre-deduplication): {len(candidates)}")

    # Deduplication
    seen_ids = set()
    deduped_candidates = [
        c for c in candidates if c['id'] != seed_id and not (c['id'] in seen_ids or seen_ids.add(c['id']))
    ]
    print(f"✅ After deduplication: {len(deduped_candidates)} unique artists")

    # Filtering
    filtered = []
    for artist in deduped_candidates:
        try:
            followers = artist['followers']['total']
            if not (0.2 * seed_followers <= followers <= 2.5 * seed_followers):
                continue

            popularity = artist['popularity']
            if abs(popularity - seed_popularity) > 25:
                continue

            audio = get_audio_summary(artist['id'])
            if audio["Avg Popularity"] == "N/A" or audio["Avg Explicitness"] == "N/A":
                continue

            if abs(audio["Avg Popularity"] - seed_avg_popularity) > 25:
                continue
            if abs(audio["Avg Explicitness"] - seed_explicit) > 0.3:
                continue

            filtered.append(artist)
            time.sleep(1)
        except Exception as e:
            print(f"❌ Error filtering artist: {e}")
            continue

    print(f"✅ Final similar artist count: {len(filtered)}")
    return filtered

# --- Main Execution ---
def find_similar_artist_names(seed_artist_name):
    seed_artist = get_artist(seed_artist_name)
    if not seed_artist:
        print("❌ Seed artist not found.")
        return []

    print(f"\n✅ Found: {seed_artist['name']}")
    print("🎧 Genres:", ", ".join(seed_artist.get('genres', [])))
    print("👥 Followers:", seed_artist['followers']['total'])

    similar_artists = get_custom_similar_artists(seed_artist)
    all_names = [seed_artist['name']] + [a['name'] for a in similar_artists]

    print("\n🎵 Similar Artists filtered by audio, genre, and popularity:")
    for name in all_names:
        print("-", name)

    return all_names

if __name__ == "__main__":
    seed_input = input("Enter a seed artist (e.g. Weeknd): ")
    all_names = find_similar_artist_names(seed_input)
