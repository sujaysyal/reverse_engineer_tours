# 🎧 Artist Analytics & Similarity Platform

A modular system for understanding artists across two dimensions:
1. **Touring behavior**, sourced from multiple live event platforms
2. **Musical and audience similarity**, derived from Spotify metadata

Together, these components form a flexible data foundation for building internal tools, experimentation layers, and machine learning workflows that require interpretable artist-level insights.

---

## 💡 Motivation

Live performance history offers unique visibility into an artist’s trajectory, regional presence, and cadence. Pairing this with structured data from streaming platforms allows us to connect artists not just by genre, but by behavior, audience scale, and musical profile.

The goal is to standardize fragmented external data and combine it with platform-derived attributes to support scalable, insight-driven systems.

---

## 🧱 System Components

### 1. 🎟️ Touring Analytics

A cross-source pipeline that scrapes and models artist event history from:

- **Songkick**
- **Resident Advisor**
- **EDMTrain**
- **Concert Archives**

**Core features:**

- Normalized schema (`artist, date, venue, city, country, source`)
- SQLite + CSV export
- Streamlit dashboard for filtering, mapping, and timeline analysis
- Metrics: top cities, seasonal peaks, growth curves, weekday breakdowns

This layer supports geo-temporal analysis, touring seasonality, and venue clustering.

---

### 2. 🔁 Spotify Similarity Engine

A lightweight Spotify-integrated module that retrieves similar artists based on:

- Top audio features (popularity, explicitness)
- Genre overlap
- Relative follower count and engagement
- Optional fallback using public year-based search

**Key traits:**

- Uses Spotify's `related_artists` and genre search APIs
- Filters for artists with similar popularity and audience scale
- Produces clean, deduplicated lists for downstream use

This tool is useful for artist-level bootstrapping, playlist seeding, or building match graphs.

---

## 🧠 Technical Orientation

This project is designed with:

- **ML lifecycle fluency**: Outputs are structured for supervised labeling, entity resolution, and feature engineering
- **Product discovery in mind**: Rapid filters and exports enable low-friction experimentation
- **Scalability & modularity**: New sources or metrics can be added with minimal refactoring
- **Cross-functional application**: Outputs serve data science, product strategy, and editorial equally well

It enables teams to move from fragmented data → structured insight → practical application.

---

## 🛠️ Tech Stack

| Layer              | Tools / Libraries                                        |
|-------------------|-----------------------------------------------------------|
| Data Collection    | `requests`, `Playwright`, `BeautifulSoup`, `asyncio`     |
| Spotify API        | `spotipy`, `dotenv`, `urllib.parse`                      |
| Storage            | `SQLite`, `pandas`, `CSV`                                |
| Visualization      | `Streamlit`, `Plotly`                                    |
| Auth & Security    | `.env`-based secrets management (GitHub-safe)            |

---

## ▶️ Usage

### Step 1: Set up your `.env`

```

SPOTIFY\_CLIENT\_ID=your\_client\_id
SPOTIFY\_CLIENT\_SECRET=your\_client\_secret

````

### Step 2: Run tour data scraping

```bash
python songkick.py
python residentadvisor.py
python edmtrain.py
python concertarchives.py
````

### Step 3: Launch dashboard

```bash
streamlit run dashboard.py
```

### Step 4: Find similar artists

```bash
python spotify_similar_artists.py
# Enter seed artist when prompted
```

---

## ✅ Example Scenarios

* Recommend comparable artists based on engagement, audio, and genre
* Identify underrepresented tour markets for a specific artist cohort
* Cluster cities or venues by artist overlap for content planning
* Label training data for live vs. studio entity resolution models
* Align touring momentum with digital popularity trends


