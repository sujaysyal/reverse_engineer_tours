# 🎧 Artist Touring Analytics Platform

A modular data infrastructure and analytics layer for understanding artist touring behavior across multiple public event sources. Designed to surface high-signal patterns in where, when, and how artists perform — with outputs that can drive internal tools, feature discovery, and machine learning workflows.

---

## Context

Live event data carries unique information: it captures momentum, geographic reach, and frequency that aren’t always visible in stream counts. But this data is fragmented, inconsistently structured, and not directly usable by downstream systems.

This platform addresses that gap — by consolidating structured signals from disparate sources into a clean, queryable, and interpretable format.

---

## Capabilities

- Multi-source scraping across **Songkick**, **Resident Advisor**, **EDMTrain**, and **Concert Archives**
- Unified schema:  
  `artist, date, venue, city, country, region, url, source, type`
- Normalized storage in **SQLite**, with outputs to **CSV** for portability
- An interactive **Streamlit** dashboard for filtering, metrics, and insights
- Designed to support ML feature generation, entity resolution, and content enrichment

---

## System Architecture

### 🧱 Data Layer

- Asynchronous and synchronous scraping using `Playwright`, `requests`, `BeautifulSoup`
- Parsing and cleaning logic designed to standardize unstructured HTML content
- Built-in de-duplication, URL handling, and minimal geocoding logic

### 🗃️ Storage Layer

- All event records are stored in a local **SQLite** instance
- Schema optimized for joins, time-series aggregation, and filtering
- Supports both single-artist and multi-artist pipelines

### 📊 Visualization Layer

- Streamlit + Plotly dashboard
- Core filters: artist name, country, year
- Metrics: top venues, top cities, most active years, touring growth, weekday distributions
- Export: filtered CSVs with schema-aligned records for reuse in external systems

---

## ML & Platform Use Cases

This platform provides input data suitable for:

- **Entity resolution**: resolving venues, artist aliases, and multi-platform IDs  
- **Supervised labeling**: training ML models to predict event-level metadata (e.g. live vs. studio, region trends)  
- **Temporal modeling**: extracting features for models that care about frequency, spacing, or peak activity  
- **Graph enrichment**: adding real-world context to internal content graphs (artists ↔ venues ↔ places ↔ time)

The goal is not just to visualize, but to **generate high-quality, ML-ready signals** from public data with minimal human intervention.

---

## Iteration Model

Each module was built following a tight experimentation loop:

1. **Scrape + Normalize**: extract from source, align to internal schema
2. **Visualize + Measure**: surface aggregate patterns, flag inconsistencies
3. **Export + Apply**: move data into modeling pipelines or internal prototypes

This supports lightweight product discovery cycles and rapid validation of new data use cases.

---

## Technical Stack

| Layer          | Tools/Libs                                 |
|----------------|---------------------------------------------|
| Collection     | `Playwright`, `requests`, `BeautifulSoup`, `asyncio` |
| Processing     | `pandas`, `re`, `datetime`, CSV I/O         |
| Storage        | `sqlite3`, schema normalization             |
| Visualization  | `Streamlit`, `Plotly`, caching optimizations|

---

## Running the Project

```bash
# Scrape artist data
python songkick.py
python residentadvisor.py
python edmtrain.py
python concertarchives.py

# Launch dashboard
streamlit run dashboard.py
