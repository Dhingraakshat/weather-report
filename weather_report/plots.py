"""Charts for the climate analysis, built with matplotlib."""

import matplotlib.pyplot as plt

from weather_report.analysis import BASELINE_END, BASELINE_START, trend_line
from weather_report.process import HEAVY_RAIN_THRESHOLD, HOT_DAY_THRESHOLD

# Keep a city's colour the same in every chart.
CITY_COLORS = {
    "Milan": "tab:blue",
    "Rome": "tab:orange",
    "Riga": "tab:green",
    "Delhi": "tab:purple",
}

MONTH_NAMES = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def plot_temperature(yearly, cities, title=None):
    """Plot yearly average temperatures and a dashed trend for each city."""
    fig, ax = plt.subplots(figsize=(10, 5), layout="constrained")
    for city in cities:
        data = yearly[yearly["city"] == city]
        color = CITY_COLORS[city]
        ax.plot(
            data["year"], data["temp_mean"], color=color, label=city, alpha=0.6
        )
        ax.plot(
            data["year"],
            trend_line(data["year"], data["temp_mean"]),
            color=color,
            linestyle="--",
        )
    if title is None:
        title = "Yearly average temperature"
    ax.set_xlabel("Year")
    ax.set_ylabel("Average temperature (°C)")
    ax.set_title(f"{title} (dashed line = trend)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
    return fig


def plot_anomaly(yearly, city, window=10, title=None):
    """Plot one city's anomalies and their rolling average.

    ``window`` is the number of years averaged for each point on the black line.
    """
    data = yearly[yearly["city"] == city]
    # Red bars are above the reference average; blue bars are below it.
    colors = [
        "tab:red" if value > 0 else "tab:blue" for value in data["anomaly"]
    ]
    moving_avg = data["anomaly"].rolling(window).mean()

    fig, ax = plt.subplots(figsize=(10, 4), layout="constrained")
    ax.bar(data["year"], data["anomaly"], color=colors)
    ax.plot(
        data["year"], moving_avg, color="black", label=f"{window}-year average"
    )
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Year")
    ax.set_ylabel("Anomaly (°C)")
    if title is None:
        title = (
            f"{city}: temperature compared to the "
            f"{BASELINE_START}-{BASELINE_END} average"
        )
    ax.set_title(title)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend()
    return fig


def plot_monthly_heatmap(monthly, city, title=None):
    """Show whether each month was warmer or colder than that month's average."""
    data = monthly[monthly["city"] == city]
    table = data.pivot(index="month", columns="year", values="temp_mean")
    # Compare January with January's average, February with February's, etc.
    table = table.sub(table.mean(axis=1), axis=0)

    first_year, last_year = table.columns.min(), table.columns.max()
    fig, ax = plt.subplots(figsize=(12, 4), layout="constrained")
    image = ax.imshow(
        table,
        aspect="auto",
        cmap="coolwarm",
        vmin=-4,
        vmax=4,
        extent=[first_year - 0.5, last_year + 0.5, 12.5, 0.5],
    )
    fig.colorbar(image, ax=ax, label="°C vs month average")
    ax.set_yticks(range(1, 13))
    ax.set_yticklabels(MONTH_NAMES)
    if title is None:
        title = f"{city}: monthly temperature, warmer or colder than usual"
    ax.set_xlabel("Year")
    ax.set_ylabel("Month")
    ax.set_title(title)
    ax.spines[["top", "right"]].set_visible(False)
    return fig


def plot_hot_days(yearly, cities, title=None):
    """Plot the yearly count of hot days for the selected cities."""
    fig, ax = plt.subplots(figsize=(10, 5), layout="constrained")
    for city in cities:
        data = yearly[yearly["city"] == city]
        ax.plot(
            data["year"], data["hot_days"], color=CITY_COLORS[city], label=city
        )
    if title is None:
        title = "Hot days per year"
    ax.set_xlabel("Year")
    ax.set_ylabel(f"Days with max temperature ≥ {HOT_DAY_THRESHOLD} °C")
    ax.set_title(title)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend()
    return fig


def plot_heavy_rain_days(yearly, cities, title=None):
    """Plot the yearly count of heavy-rain days for the selected cities."""
    fig, ax = plt.subplots(figsize=(10, 5), layout="constrained")
    for city in cities:
        data = yearly[yearly["city"] == city]
        ax.plot(
            data["year"],
            data["heavy_rain_days"],
            color=CITY_COLORS[city],
            label=city,
        )
    if title is None:
        title = "Heavy rain days per year"
    ax.set_xlabel("Year")
    ax.set_ylabel(f"Days with rain ≥ {HEAVY_RAIN_THRESHOLD} mm")
    ax.set_title(title)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend()
    return fig


if __name__ == "__main__":
    from pathlib import Path

    from weather_report.analysis import add_anomaly
    from weather_report.process import (
        load_data,
        monthly_summary,
        yearly_summary,
    )

    daily = load_data()
    yearly = add_anomaly(yearly_summary(daily))
    monthly = monthly_summary(daily)
    cities = sorted(yearly["city"].unique())

    output_dir = Path("figures")
    output_dir.mkdir(exist_ok=True)

    # These titles describe the full-data charts. The app uses neutral titles
    # because its city and year selections can change.
    charts = {
        "temperature.png": plot_temperature(
            yearly,
            cities,
            title="Milan, Rome and Riga get warmer, Delhi does not",
        ),
        "anomaly_milan.png": plot_anomaly(
            yearly,
            "Milan",
            title="Milan: every year since 1985 was warmer than "
            "the 1961-1990 average",
        ),
        "heatmap_milan.png": plot_monthly_heatmap(
            monthly,
            "Milan",
            title="Milan: since 1990, most months are warmer than usual",
        ),
        "hot_days.png": plot_hot_days(
            yearly,
            cities,
            title="Milan and Rome now have many more hot days than before",
        ),
        "heavy_rain_days.png": plot_heavy_rain_days(
            yearly,
            cities,
            title="Heavy rain days go up and down, with no clear trend",
        ),
    }
    for filename, fig in charts.items():
        fig.savefig(output_dir / filename, dpi=150, bbox_inches="tight")
    print(f"Saved {len(charts)} charts in {output_dir}/")
