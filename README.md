
# 🎧 Artist Similarity & Touring Analytics Platform

A modular platform for generating similar artists using Spotify metadata, collecting their live performance histories from public sources, and visualizing geo-temporal patterns through an interactive dashboard.

Designed for teams exploring content understanding, catalog modeling, and artist-level analysis at scale.

---

## 🔁 Workflow Overview

### 1. Generate similar artists via Spotify metadata  
→ genre, popularity, explicitness, followers, and top track behavior

### 2. Scrape tour data for those artists  
→ across Songkick, Resident Advisor, EDMTrain, and Concert Archives

### 3. Explore patterns and export insights via dashboard  
→ top cities, seasons, venues, growth curves, weekday trends

---

## 🧠 Purpose

Touring data reflects artist activity in time and space. Combined with streaming metadata, it forms a strong foundation for:

- Artist clustering
- Entity resolution
- Regional momentum tracking
- ML labeling and recommendation inputs
- Context-aware content graph enrichment

---

## 🧱 System Components

### 1. 🔁 Spotify Similarity Engine (`spotify_similar_artists.py`)

- Uses Spotify APIs (`related_artists`, genre search, fallback logic)
- Filters based on:
  - Audio features (popularity, explicitness)
  - Genre overlap
  - Follower scaling
- Output: a deduplicated list of artists with similar audience profiles

### 2. 🎟️ Touring Data Pipeline

- Scrapers:  
  - `songkick.py`  
  - `residentadvisor.py`  
  - `edmtrain.py`  
  - `concertarchives.py`  
- Shared schema:  
  `artist, date, venue, city, country, region, source, url`
- Outputs:  
  - SQLite tables  
  - CSV exports

### 3. 📊 Touring Dashboard (`dashboard.py`)

- Built with **Streamlit** and **Plotly**
- Real-time filtering by artist, year, country
- Visuals: choropleths, bar charts, growth timelines, weekday breakdowns
- CSV export for downstream systems

---

## 🛠️ Tech Stack

| Layer              | Tools / Libraries                                        |
|-------------------|-----------------------------------------------------------|
| Spotify API        | `spotipy`, `dotenv`, `urllib.parse`, `statistics`        |
| Scraping           | `requests`, `Playwright`, `BeautifulSoup`, `asyncio`     |
| Storage            | `SQLite`, `pandas`, `CSV`                                |
| Visualization      | `Streamlit`, `Plotly`                                    |
| Security           | `.env`-based secrets (GitHub-safe)                       |

---

## 🧠 Design Principles

- **ML lifecycle readiness**: All outputs are structured for feature engineering, supervised learning, and labeling workflows  
- **Build-measure-learn loop**: Modular code allows fast iteration on sources, filters, and dashboards  
- **Cross-functional output**: Designed for data science, product discovery, and editorial tooling alike  
- **Low barrier to entry**: CLI-based artist input → full stack insight in under 5 minutes

---

## ▶️ Usage

### Step 1: Configure your `.env`

```

SPOTIFY\_CLIENT\_ID=your\_client\_id
SPOTIFY\_CLIENT\_SECRET=your\_client\_secret

````

### Step 2: Generate similar artists

```bash
python spotify_similar_artists.py
# → Enter a seed artist (e.g., The Weeknd)
# → Get a filtered list of similar artists
````

### Step 3: Scrape tour data for those artists

```bash
python songkick.py
python residentadvisor.py
python edmtrain.py
python concertarchives.py
```

### Step 4: Explore and export insights

```bash
streamlit run dashboard.py
```

---

## ✅ Example Use Cases

* Build artist recommendation cohorts using both content metadata and tour history
* Identify cities or regions where multiple similar artists tour (collaborative filtering)
* Track audience scale alignment via follower range + concert density
* Power labeling for “live artist” vs. “digital-first” content modeling
* Generate feature-rich training data for entity resolution models

```
