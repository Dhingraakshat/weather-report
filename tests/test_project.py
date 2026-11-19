"""Simple tests for the analysis and processing functions."""

import numpy as np
import pandas as pd
import pytest

from weather_report.analysis import add_anomaly, trend_per_decade, trend_test
from weather_report.process import load_data, yearly_summary


def test_trend_of_straight_line():
    """A line that goes up 0.1 per year must give a trend of 1.0 per decade."""
    years = np.arange(2000, 2010)
    values = 0.1 * years
    assert trend_per_decade(years, values) == pytest.approx(1.0)


def test_trend_test_on_straight_line():
    """A perfect straight line must give 1.0 per decade and a small p-value."""
    years = np.arange(2000, 2010)
    values = 0.1 * years
    warming, p_value = trend_test(years, values)
    assert warming == pytest.approx(1.0)
    assert p_value < 0.05


def test_anomaly_is_zero_on_average_in_baseline():
    """The anomaly is the difference from the baseline average (11.0 here)."""
    yearly = pd.DataFrame({
        "city": ["Milan"] * 4,
        "year": [2000, 2001, 2002, 2003],
        "temp_mean": [10.0, 12.0, 14.0, 16.0],
    })
    result = add_anomaly(yearly, start=2000, end=2001)
    assert result["anomaly"].tolist() == [-1.0, 1.0, 3.0, 5.0]


def test_hot_days_counts_years_with_zero():
    """Years with no hot days must be counted as 0, not left out."""
    daily = pd.DataFrame({
        "city": ["Milan"] * 4,
        "date": pd.to_datetime(["2000-07-01", "2000-07-02", "2001-07-01", "2001-07-02"]),
        "temp_mean": [25.0, 26.0, 20.0, 21.0],
        "temp_max": [31.0, 29.0, 25.0, 26.0],
        "rain": [0.0, 2.0, 1.0, 1.0],
    })
    result = yearly_summary(daily)
    assert result["hot_days"].tolist() == [1, 0]
    assert result["rain"].tolist() == [2.0, 2.0]


def test_heavy_rain_days_counts_years_with_zero():
    """Years with no heavy rain days must be counted as 0, not left out."""
    daily = pd.DataFrame({
        "city": ["Milan"] * 4,
        "date": pd.to_datetime(["2000-10-01", "2000-10-02",
                                "2001-10-01", "2001-10-02"]),
        "temp_mean": [15.0, 15.0, 15.0, 15.0],
        "temp_max": [20.0, 20.0, 20.0, 20.0],
        "rain": [25.0, 20.0, 19.9, 0.0],
    })
    result = yearly_summary(daily)
    assert result["heavy_rain_days"].tolist() == [2, 0]


def test_load_data_without_files_gives_error(tmp_path):
    """An empty data folder must give a FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_data(tmp_path)
