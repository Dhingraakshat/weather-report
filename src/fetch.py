"""Download historical daily weather data from the Open-Meteo API."""

from pathlib import Path

import pandas as pd
import requests

API_URL = "https://archive-api.open-meteo.com/v1/archive"
DATA_DIR = Path("data")

CITIES = {
    "Milan": (45.46, 9.19),
    "Rome": (41.90, 12.50),
    "Riga": (56.95, 24.11),
    "Delhi": (28.61, 77.21),
}


def fetch_city(name, lat, lon, start="1950-01-01", end="2025-12-31"):
    """Download daily weather data for one city.

    Parameters
    ----------
    name : str
        City name, added as a column.
    lat, lon : float
        Coordinates of the city.
    start, end : str
        Date range in YYYY-MM-DD format.

    Returns
    -------
    pandas.DataFrame
        One row per day with mean/max temperature and precipitation.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": "temperature_2m_mean,temperature_2m_max,precipitation_sum",
        "timezone": "auto",
    }
    try:
        response = requests.get(API_URL, params=params, timeout=60)
        response.raise_for_status()
    except requests.RequestException as error:
        raise RuntimeError(f"Could not download data for {name}: {error}") from error

    df = pd.DataFrame(response.json()["daily"])
    df["city"] = name
    return df


def fetch_all(cities=CITIES):
    """Download data for every city and save each one as a CSV in data/."""
    DATA_DIR.mkdir(exist_ok=True)
    for name, (lat, lon) in cities.items():
        path = DATA_DIR / f"{name.lower()}.csv"
        if path.exists():
            print(f"{name}: already downloaded, skipping")
            continue
        df = fetch_city(name, lat, lon)
        df.to_csv(path, index=False)
        print(f"{name}: saved {len(df)} rows to {path}")


if __name__ == "__main__":
    fetch_all()