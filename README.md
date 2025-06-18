# 🎧 Artist Touring Analytics Platform

A modular pipeline and analytics tool for collecting and exploring global artist touring data. It brings together multiple event sources into a consistent, structured format to surface patterns in performance history, geography, and scheduling.

---

## Overview

The system enables:

- Aggregation of artist tour data across multiple public platforms
- Resolution of location, venue, and event information into a unified schema
- Interactive visual analysis and exportable insights
- A lightweight but extensible foundation for downstream workflows and experimentation

---

## Architecture

### 1. **Data Ingestion**

Scrapers gather live performance data using headless browsers and traditional requests from:

- `songkick.py`: Historical and upcoming concerts
- `residentadvisor.py`: Club events
- `edmtrain.py`: U.S. electronic music events
- `concertarchives.py`: Fan-reported past shows

Each module outputs consistent structured records with fields like:

```text
artist, date, venue, city, country, region, url, type, source
````

---

### 2. **Storage & Modeling**

Event records are stored in a **SQLite** database and/or exported to **CSV**. The data structure supports easy joining, filtering, and transformation — designed for reuse across different analysis or labeling pipelines.

---

### 3. **Visualization Dashboard**

Built using **Streamlit** and **Plotly**, the dashboard allows for:

* Filtering by year, country, and artist
* Visualizing top venues, cities, and performance frequency
* Identifying seasonal or regional touring trends
* Exporting data for further use

---

## Development Approach

This system was developed with:

* A focus on **product discovery** through iterative insight generation
* Clean data modeling for interpretability and reuse
* Lightweight tooling that enables **fast experimentation**
* Built-in support for metrics-driven workflows (e.g., active years, tour density, location spread)

---

## Technical Stack

* **Data collection**: Playwright (async + sync), BeautifulSoup, requests
* **Processing**: pandas, re, datetime
* **Storage**: SQLite, CSV
* **UI & Visualization**: Streamlit, Plotly

---

## Sample Use Cases

* Understand where and when an artist performs most frequently
* Track touring momentum over time
* Identify high-density venues and cities
* Build labeled datasets for internal tools or systems

---

## Run the Project

```bash
# Scrape data from sources
python songkick.py
python residentadvisor.py
python edmtrain.py
python concertarchives.py

# Launch dashboard
streamlit run dashboard.py
```

---

## Design Philosophy

Organizing and connecting content data — across time, place, and platform — can reveal new opportunities for discovery, association, and context. This project serves as a lightweight framework for doing exactly that in a space where structured insight is often locked inside unstructured sources.

```

---
