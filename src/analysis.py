"""Numerical analysis of climate trends: anomalies and warming rates."""

import numpy as np
import pandas as pd

BASELINE_START = 1961
BASELINE_END = 1990


def add_anomaly(yearly, start=BASELINE_START, end=BASELINE_END):
    """Add the temperature anomaly compared to a baseline period.

    Parameters
    ----------
    yearly : pandas.DataFrame
        Yearly data from process.yearly_summary().
    start, end : int
        First and last year of the baseline ("normal") period.

    Returns
    -------
    pandas.DataFrame
        Same table with an extra 'anomaly' column in °C.
    """
    yearly = yearly.copy()
    in_baseline = yearly["year"].between(start, end)
    baseline = yearly[in_baseline].groupby("city")["temp_mean"].mean()
    yearly["anomaly"] = yearly["temp_mean"] - yearly["city"].map(baseline)
    return yearly


def trend_per_decade(years, values):
    """Fit a straight line and return how much the values change per decade.

    Parameters
    ----------
    years : array-like
        The years (x axis).
    values : array-like
        The values for each year (y axis), e.g. temperatures.

    Returns
    -------
    float
        Change per 10 years.
    """
    slope, _ = np.polyfit(years, values, deg=1)
    return slope * 10


def trend_line(years, values):
    """Return the points of the best-fit straight line, used for plotting.

    Parameters
    ----------
    years : array-like
        The years (x axis).
    values : array-like
        The values for each year (y axis).

    Returns
    -------
    numpy.ndarray
        The y value of the trend line for each year.
    """
    slope, intercept = np.polyfit(years, values, deg=1)
    return slope * np.asarray(years) + intercept


def city_summary(yearly, period=30):
    """Build a table with the main climate numbers for each city.

    Parameters
    ----------
    yearly : pandas.DataFrame
        Yearly data from process.yearly_summary().
    period : int
        Number of years used for the "old" and "recent" averages.

    Returns
    -------
    pandas.DataFrame
        One row per city with warming trend, old vs recent
        temperature and change in hot days.
    """
    rows = []
    for city, group in yearly.groupby("city"):
        years = group["year"].to_numpy()
        temps = group["temp_mean"].to_numpy()
        hot_days = group["hot_days"].to_numpy()

        old_avg = np.mean(temps[:period])
        recent_avg = np.mean(temps[-period:])

        rows.append({
            "city": city,
            "warming_per_decade": round(trend_per_decade(years, temps), 2),
            "old_avg_temp": round(old_avg, 2),
            "recent_avg_temp": round(recent_avg, 2),
            "difference": round(recent_avg - old_avg, 2),
            "hot_days_change_per_decade": round(trend_per_decade(years, hot_days), 1),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    from src.process import load_data, yearly_summary

    yearly = add_anomaly(yearly_summary(load_data()))
    print(city_summary(yearly))