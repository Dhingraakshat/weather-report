"""Numerical analysis of climate trends: anomalies and warming rates."""

import numpy as np
import pandas as pd
from scipy import stats

BASELINE_START = 1961
BASELINE_END = 1990

SEASONS = {
    12: "Winter",
    1: "Winter",
    2: "Winter",
    3: "Spring",
    4: "Spring",
    5: "Spring",
    6: "Summer",
    7: "Summer",
    8: "Summer",
    9: "Autumn",
    10: "Autumn",
    11: "Autumn",
}


def add_anomaly(yearly, start=BASELINE_START, end=BASELINE_END):
    """Add each year's temperature difference from its city's baseline.

    A positive anomaly means warmer than the baseline average; a negative
    one means colder. The input table is left unchanged.
    """
    yearly = yearly.copy()
    in_baseline = yearly["year"].between(start, end)
    # Give each city its own reference average.
    baseline = yearly[in_baseline].groupby("city")["temp_mean"].mean()
    yearly["anomaly"] = yearly["temp_mean"] - yearly["city"].map(baseline)
    return yearly


def trend_per_decade(years, values):
    """Estimate the change per decade from matching years and measurements.

    The slope is per year, so multiply it by 10 to report a per-decade rate.
    """
    slope, _ = np.polyfit(years, values, deg=1)
    return slope * 10


def trend_line(years, values):
    """Return the fitted value for each year, ready to draw as a chart line."""
    slope, intercept = np.polyfit(years, values, deg=1)
    return slope * np.asarray(years) + intercept


def trend_test(years, values):
    """Return the fitted change per decade and its p-value.

    A small p-value is evidence of a trend, not proof of what caused it.
    """
    result = stats.linregress(years, values)
    return result.slope * 10, result.pvalue


def seasonal_trends(monthly):
    """Calculate each city's temperature trend in each season.

    December is grouped with January and February of the same year.
    """
    monthly = monthly.copy()
    monthly["season"] = monthly["month"].map(SEASONS)
    # Average the monthly values first, giving one value per season and year.
    seasonal = (
        monthly.groupby(["city", "season", "year"])["temp_mean"]
        .mean()
        .reset_index()
    )

    rows = []
    for (city, season), group in seasonal.groupby(["city", "season"]):
        warming = trend_per_decade(group["year"], group["temp_mean"])
        rows.append(
            {
                "city": city,
                "season": season,
                "warming_per_decade": round(warming, 2),
            }
        )
    table = pd.DataFrame(rows).pivot(
        index="city", columns="season", values="warming_per_decade"
    )
    # Keep the season columns in calendar order.
    return table[["Winter", "Spring", "Summer", "Autumn"]]


def city_summary(yearly, period=30):
    """Build one row of trend and comparison results for each city.

    ``period`` sets how many years to average at the start and end.
    """
    rows = []
    for city, group in yearly.groupby("city"):
        # Keep each measurement paired with the same year's data.
        years = group["year"].to_numpy()
        temps = group["temp_mean"].to_numpy()
        hot_days = group["hot_days"].to_numpy()
        rain = group["rain"].to_numpy()
        heavy_rain_days = group["heavy_rain_days"].to_numpy()

        # Compare equally sized periods at the two ends of the record.
        old_avg = np.mean(temps[:period])
        recent_avg = np.mean(temps[-period:])
        warming, p_value = trend_test(years, temps)
        rain_change, rain_p_value = trend_test(years, rain)
        heavy_rain_change = trend_per_decade(years, heavy_rain_days)

        rows.append(
            {
                "city": city,
                "warming_per_decade": round(warming, 2),
                "p_value": round(p_value, 4),
                # The project uses 0.05 as its cutoff for significance.
                "significant": p_value < 0.05,
                "old_avg_temp": round(old_avg, 2),
                "recent_avg_temp": round(recent_avg, 2),
                "difference": round(recent_avg - old_avg, 2),
                "hot_days_change_per_decade": round(
                    trend_per_decade(years, hot_days), 1
                ),
                "rain_change_per_decade": round(rain_change, 1),
                "rain_p_value": round(rain_p_value, 4),
                "heavy_rain_days_change_per_decade": round(
                    heavy_rain_change, 1
                ),
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    from weather_report.process import (
        load_data,
        monthly_summary,
        yearly_summary,
    )

    daily = load_data()
    yearly = add_anomaly(yearly_summary(daily))
    print(city_summary(yearly).to_string())
    print(seasonal_trends(monthly_summary(daily)))
