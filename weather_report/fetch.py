"""Download historical daily weather data from the Open-Meteo API."""

import time
from pathlib import Path

import pandas as pd
import requests

API_URL = "https://archive-api.open-meteo.com/v1/archive"
DATA_DIR = Path("data")
PAUSE_SECONDS = 60  # Wait a minute before requesting the next city.
TIMEOUT_SECONDS = 60  # Stop waiting if the service takes too long.

CITIES = {
    "Milan": (45.46, 9.19),
    "Rome": (41.90, 12.50),
    "Riga": (56.95, 24.11),
    "Delhi": (28.61, 77.21),
}


def fetch_city(name, lat, lon, start="1950-01-01", end="2025-12-31"):
    """Request daily temperatures and rainfall for one location and date range.

    The city name is added to every returned row. Network problems are
    reported as RuntimeError with a message that names the city.
    """
    # The API needs coordinates, dates, requested measurements, and a time zone.
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": "temperature_2m_mean,temperature_2m_max,precipitation_sum",
        "timezone": "auto",
    }
    try:
        response = requests.get(
            API_URL, params=params, timeout=TIMEOUT_SECONDS
        )
        response.raise_for_status()
    except requests.exceptions.Timeout as error:
        # Handle timeouts first so they get their own clearer message.
        raise RuntimeError(
            f"The API did not answer within {TIMEOUT_SECONDS} seconds "
            f"for {name}. Please try again later."
        ) from error
    except requests.RequestException as error:
        raise RuntimeError(
            f"Could not download data for {name}: {error}"
        ) from error

    df = pd.DataFrame(response.json()["daily"])
    df["city"] = name
    return df


def fetch_all(cities=CITIES):
    """Download each city's CSV, skipping files that are already present.

    ``cities`` maps names to latitude and longitude pairs.
    """
    DATA_DIR.mkdir(exist_ok=True)
    for name, (lat, lon) in cities.items():
        path = DATA_DIR / f"{name.lower()}.csv"
        if path.exists():
            print(f"{name}: already downloaded, skipping")
            continue
        df = fetch_city(name, lat, lon)
        df.to_csv(path, index=False)
        print(f"{name}: saved {len(df)} rows to {path}")
        # Leave time before the next request to respect the API limit.
        time.sleep(PAUSE_SECONDS)


if __name__ == "__main__":
    fetch_all()
