"""Streamlit app: Is Milan getting hotter?"""

import matplotlib.pyplot as plt
import streamlit as st

from src.analysis import add_anomaly, city_summary
from src.fetch import fetch_all
from src.plots import (plot_anomaly, plot_hot_days, plot_monthly_heatmap,
                       plot_temperature)
from src.process import load_data, monthly_summary, yearly_summary


@st.cache_data
def get_data():
    """Load the data (downloading it first if missing) and prepare the tables.

    Returns
    -------
    tuple of pandas.DataFrame
        Yearly data with anomalies, and monthly data.
    """
    try:
        daily = load_data()
    except FileNotFoundError:
        fetch_all()
        daily = load_data()
    return add_anomaly(yearly_summary(daily)), monthly_summary(daily)


def show(fig):
    """Display a matplotlib figure in the app, then close it to free memory."""
    st.pyplot(fig)
    plt.close(fig)


st.set_page_config(page_title="Weather Report", page_icon="🌡️", layout="wide")
st.title("🌡️ Is Milan getting hotter?")
st.write("Climate trends from 1950 to 2025, using daily data from the "
         "Open-Meteo Historical Weather API.")

with st.spinner("Loading weather data..."):
    yearly, monthly = get_data()

all_cities = sorted(yearly["city"].unique())

st.sidebar.header("Settings")
cities = st.sidebar.multiselect("Cities to compare", all_cities, default=all_cities)
focus_city = st.sidebar.selectbox("City for detailed view", all_cities,
                                  index=all_cities.index("Milan"))

if not cities:
    st.warning("Select at least one city in the sidebar.")
    st.stop()

summary = city_summary(yearly)
row = summary[summary["city"] == focus_city].iloc[0]

st.header(f"{focus_city} at a glance")
col1, col2, col3 = st.columns(3)
col1.metric("Warming trend", f"{row['warming_per_decade']} °C / decade")
col2.metric("Last 30 years average", f"{row['recent_avg_temp']} °C",
            f"{row['difference']:+} °C vs first 30 years", delta_color="inverse")
col3.metric("Hot days trend", f"{row['hot_days_change_per_decade']:+} days / decade")

st.header("Comparing cities")
show(plot_temperature(yearly, cities))
show(plot_hot_days(yearly, cities))
st.subheader("Summary table")
st.dataframe(summary[summary["city"].isin(cities)], hide_index=True)

st.header(f"{focus_city} in detail")
show(plot_anomaly(yearly, focus_city))
show(plot_monthly_heatmap(monthly, focus_city))

st.caption("Hot day = maximum temperature ≥ 30°C. Anomaly baseline: 1961–1990.")