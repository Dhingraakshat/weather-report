"""Load the downloaded CSV files and prepare them for analysis."""

from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")
HOT_DAY_THRESHOLD = 30  # °C, a day with max temperature >= 30 counts as "hot"


def load_data(data_dir=DATA_DIR):
    """Load every city CSV from the data folder into one table.

    Parameters
    ----------
    data_dir : Path
        Folder containing the CSV files.

    Returns
    -------
    pandas.DataFrame
        All cities together, one row per city per day.
    """
    files = list(data_dir.glob("*.csv"))
    if not files:
        raise FileNotFoundError("No CSV files found. Run 'python -m src.fetch' first.")

    df = pd.concat([pd.read_csv(file) for file in files], ignore_index=True)
    df = df.rename(columns={
        "time": "date",
        "temperature_2m_mean": "temp_mean",
        "temperature_2m_max": "temp_max",
        "precipitation_sum": "rain",
    })
    df["date"] = pd.to_datetime(df["date"])
    return df.dropna()


def yearly_summary(df):
    """Summarise each city's weather per year.

    Parameters
    ----------
    df : pandas.DataFrame
        Daily data from load_data().

    Returns
    -------
    pandas.DataFrame
        One row per city per year with average temperatures,
        total rain and number of hot days.
    """
    df = df.copy()
    df["year"] = df["date"].dt.year
    df["hot_day"] = df["temp_max"] >= HOT_DAY_THRESHOLD

    yearly = df.groupby(["city", "year"]).agg(
        temp_mean=("temp_mean", "mean"),
        temp_max=("temp_max", "mean"),
        rain=("rain", "sum"),
        hot_days=("hot_day", "sum"),
    )
    return yearly.reset_index()


def monthly_summary(df):
    """Average temperature per city, year and month (used for heatmaps).

    Parameters
    ----------
    df : pandas.DataFrame
        Daily data from load_data().

    Returns
    -------
    pandas.DataFrame
        One row per city, year and month with the mean temperature.
    """
    df = df.copy()
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month

    monthly = df.groupby(["city", "year", "month"])["temp_mean"].mean()
    return monthly.reset_index()


if __name__ == "__main__":
    data = load_data()
    print(data.head())
    print(yearly_summary(data).tail())