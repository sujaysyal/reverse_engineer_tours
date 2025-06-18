import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

DB_PATH = "tour_data.db"

@st.cache_data
def get_artist_tables(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    raw_tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    excluded = {"tour_data", "finish"}
    return {t.replace("_", " ").title(): t for t in raw_tables if t.lower() not in excluded}

@st.cache_data
def load_data(table_name, db_path, artist_name):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    df['artist'] = artist_name
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.strftime('%b')
    df['weekday'] = df['date'].dt.day_name()
    return df

# === Streamlit Config ===
st.set_page_config(page_title="Touring Dashboard", layout="wide")
st.title("🎧 JORA Touring Dashboard")

# === Sidebar: Artist Selection ===
artist_table_map = get_artist_tables(DB_PATH)
st.sidebar.markdown("### 🎤 Select an Artist")
selected_display_name = st.sidebar.selectbox("Search or Select Artist", sorted(list(artist_table_map.keys())))
selected_table = artist_table_map[selected_display_name]
df = load_data(selected_table, DB_PATH, selected_display_name)

if df.empty:
    st.warning("No data found for this artist.")
    st.stop()

# === Filter by Year (Checkbox style) ===
st.sidebar.markdown("### 📅 Filter by Year")
years = sorted(df['year'].dropna().unique())
select_all_years = st.sidebar.checkbox("Select All Years", value=True)
if select_all_years:
    selected_years = years
else:
    selected_years = st.sidebar.multiselect("Choose Year(s)", options=years, default=years)

# === Filter by Country (Checkbox style) ===
st.sidebar.markdown("### 🌍 Filter by Country")
countries = sorted(df['venue_country'].dropna().unique())
select_all_countries = st.sidebar.checkbox("Select All Countries", value=True)
if select_all_countries:
    selected_countries = countries
else:
    selected_countries = st.sidebar.multiselect("Choose Country(ies)", options=countries, default=countries)

# === Filter Data ===
df = df[df['year'].isin(selected_years) & df['venue_country'].isin(selected_countries)]

# === Overview Metrics ===
st.info(f"✅ Loaded {len(df)} filtered shows for {selected_display_name}")

st.header(f"Touring Overview for {selected_display_name}")
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Shows", len(df))
col2.metric("Unique Cities", df['venue_city'].nunique())
col3.metric("Countries Played", df['venue_country'].nunique())
col4.metric("Active Years", df['year'].nunique())
if df['year'].nunique() > 0:
    col5.metric("Avg Shows/Year", round(len(df) / df['year'].nunique(), 1))
if not df.empty:
    top_year = df['year'].value_counts().idxmax()
    top_count = df['year'].value_counts().max()
    col6.metric("Most Active Year", f"{top_year} ({top_count})")
    
# === Shows by Country ===
st.subheader("🌍 Shows by Country")
country_df = df['venue_country'].value_counts().reset_index()
country_df.columns = ['country', 'count']
col_table, col_map = st.columns([1.5, 2.5])

with col_table:
    st.dataframe(country_df, use_container_width=True, height=400)

with col_map:
    fig = px.choropleth(country_df, locations='country', locationmode='country names',
                        color='count', color_continuous_scale="plasma", title="Tour Frequency")
    st.plotly_chart(fig, use_container_width=True)
    if not country_df.empty:
        st.markdown(f"**Insight:** Most international shows occurred in **{country_df.iloc[0]['country']}**.")
        

# === Top Cities & Venues ===
st.subheader("🏙️ Top Cities and Venues")
col1, col2 = st.columns(2)

with col1:
    top_cities = df['venue_city'].value_counts().head(10).reset_index()
    top_cities.columns = ['venue_city', 'count']
    fig = px.bar(top_cities.sort_values(by='count'), x='count', y='venue_city', orientation='h',
                 labels={'venue_city': 'City', 'count': 'Shows'}, title="Top Cities", text='count')
    st.plotly_chart(fig, use_container_width=True)
    if not top_cities.empty:
        st.markdown(f"**Insight:** Top city: **{top_cities.iloc[0]['venue_city']}** with **{top_cities.iloc[0]['count']}** shows.")

with col2:
    top_venues = df['venue'].value_counts().head(10).reset_index()
    top_venues.columns = ['venue', 'count']
    fig = px.bar(top_venues.sort_values(by='count'), x='count', y='venue', orientation='h',
                 labels={'venue': 'Venue', 'count': 'Shows'}, title="Top Venues", text='count')
    st.plotly_chart(fig, use_container_width=True)
    if not top_venues.empty:
        st.markdown(f"**Insight:** Most played venue: **{top_venues.iloc[0]['venue']}** with **{top_venues.iloc[0]['count']}** shows.")
    

# === Shows by Year ===
st.subheader("📊 Shows by Year")
year_df = df['year'].value_counts().sort_index().reset_index()
year_df.columns = ['Year', 'Count']
fig = px.bar(year_df, x='Year', y='Count', title="Total Shows Per Year", text='Count')
st.plotly_chart(fig, use_container_width=True)
if not year_df.empty:
    st.markdown(f"**Insight:** Peak activity occurred in **{top_year}** with **{top_count}** shows.")
    
# === Cumulative Growth ===
st.subheader("📈 Cumulative Growth Over Time")
df_sorted = df.sort_values("date")
df_sorted['cumulative'] = range(1, len(df_sorted) + 1)
fig = px.line(df_sorted, x='date', y='cumulative', title="Growth in Total Shows Over Time")
st.plotly_chart(fig, use_container_width=True)
if not df_sorted.empty:
    growth_year = df_sorted['year'].mode().iloc[0]
    st.markdown(f"**Insight:** Major touring growth occurred in **{growth_year}**.")
    
# === Calendar Heatmap ===
st.subheader("📆 Shows by Year & Month")
heatmap = df.pivot_table(index='month_name', columns='year', values='venue', aggfunc='count').fillna(0)
fig = px.imshow(heatmap, labels=dict(x="Year", y="Month", color="Show Count"),
                color_continuous_scale="Blues", x=heatmap.columns, y=heatmap.index)
st.plotly_chart(fig, use_container_width=True)
if not df.empty:
    top_month = df['month_name'].mode().iloc[0]
    st.markdown(f"**Insight:** Touring peaks in **{top_month}**, aligning with seasonal demand.")


# === Monthly Spread ===
st.subheader("📦 Touring Spread by Month")
fig = px.box(df, x='month_name', y='year', points="all", title="Touring Seasonality")
st.plotly_chart(fig, use_container_width=True)
if not df.empty:
    peak_months = df['month_name'].value_counts().head(2).index.tolist()
    st.markdown(f"**Insight:** Key months for touring: **{peak_months[0]}** and **{peak_months[1]}**.")

# === Shows by Weekday ===
st.subheader("📅 Shows by Day of the Week")
weekday_df = df['weekday'].value_counts().reindex([
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
]).reset_index()
weekday_df.columns = ['Weekday', 'Count']
fig = px.bar(weekday_df, x='Weekday', y='Count', title="Shows by Weekday", text='Count')
st.plotly_chart(fig, use_container_width=True)
if not weekday_df.empty:
    busiest_day = weekday_df.loc[weekday_df['Count'].idxmax(), 'Weekday']
    st.markdown(f"**Insight:** Most shows happen on **{busiest_day}**, aligning with audience availability.")


# === CSV Export (Styled Button) ===
csv_data = df.copy()
csv_data['artist'] = selected_display_name

st.markdown(f"""
<style>
    .stDownloadButton > button {{
        color: #d33;
        border: 1px solid #d33;
        border-radius: 8px;
        background: #fff;
        font-weight: 600;
        padding: 0.6em 1em;
        margin-top: 10px;
    }}
</style>
""", unsafe_allow_html=True)

st.download_button(
    label=f"⬇️ Download {selected_display_name} Tour Data",
    data=csv_data.to_csv(index=False),
    file_name=f"{selected_display_name.replace(' ', '_')}_tour_data.csv",
    mime="text/csv"
)

st.caption("Built with ❤️ using Streamlit, Plotly, and SQLite — Empowering data-driven music tours.")

