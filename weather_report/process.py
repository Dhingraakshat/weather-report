"""Load the downloaded CSV files and prepare them for analysis."""

import pandas as pd

from weather_report.fetch import DATA_DIR

HOT_DAY_THRESHOLD = 30  # A day counts as hot at this maximum temperature (°C).
HEAVY_RAIN_THRESHOLD = 20  # A day counts as heavy rain at this amount (mm).


def load_data(data_dir=DATA_DIR):
    """Join the city's daily CSV files into one table and clean the columns.

    Raises FileNotFoundError if the folder contains no CSV files.
    """
    files = list(data_dir.glob("*.csv"))
    if not files:
        raise FileNotFoundError(
            "No CSV files found. Run 'python -m weather_report.fetch' first."
        )

    df = pd.concat([pd.read_csv(file) for file in files], ignore_index=True)
    # Shorter names make the columns easier to use in later steps.
    df = df.rename(
        columns={
            "time": "date",
            "temperature_2m_mean": "temp_mean",
            "temperature_2m_max": "temp_max",
            "precipitation_sum": "rain",
        }
    )
    df["date"] = pd.to_datetime(df["date"])
    # Incomplete days cannot be included in the summaries.
    return df.dropna()


def yearly_summary(df):
    """Make one row per city and year from the daily records."""
    df = df.copy()
    df["year"] = df["date"].dt.year
    df["hot_day"] = df["temp_max"] >= HOT_DAY_THRESHOLD
    df["heavy_rain_day"] = df["rain"] >= HEAVY_RAIN_THRESHOLD

    # Summing True/False flags counts qualifying days, including years with 0.
    # Rain is summed for the year; temperatures are averaged.
    yearly = df.groupby(["city", "year"]).agg(
        temp_mean=("temp_mean", "mean"),
        temp_max=("temp_max", "mean"),
        rain=("rain", "sum"),
        hot_days=("hot_day", "sum"),
        heavy_rain_days=("heavy_rain_day", "sum"),
    )
    return yearly.reset_index()


def monthly_summary(df):
    """Make one row per city, year, and month for seasonal charts."""
    df = df.copy()
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month

    monthly = df.groupby(["city", "year", "month"])["temp_mean"].mean()
    return monthly.reset_index()


if __name__ == "__main__":
    data = load_data()
    print(data.head())
    print(yearly_summary(data).tail())
