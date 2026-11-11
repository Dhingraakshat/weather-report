"""Charts for the climate analysis, built with matplotlib."""

import matplotlib.pyplot as plt

from src.analysis import trend_line

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def plot_temperature(yearly, cities):
    """Line chart of yearly average temperature with a trend line per city.

    Parameters
    ----------
    yearly : pandas.DataFrame
        Yearly data from process.yearly_summary().
    cities : list of str
        Cities to show.

    Returns
    -------
    matplotlib.figure.Figure
        The finished chart.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    for city in cities:
        data = yearly[yearly["city"] == city]
        line = ax.plot(data["year"], data["temp_mean"], label=city, alpha=0.6)[0]
        ax.plot(data["year"], trend_line(data["year"], data["temp_mean"]),
                color=line.get_color(), linestyle="--")
    ax.set_xlabel("Year")
    ax.set_ylabel("Average temperature (°C)")
    ax.set_title("Yearly average temperature (dashed = trend)")
    ax.legend()
    return fig


def plot_anomaly(yearly, city):
    """Bar chart of yearly temperature anomaly: red = warmer, blue = colder.

    Parameters
    ----------
    yearly : pandas.DataFrame
        Yearly data with an 'anomaly' column (from analysis.add_anomaly()).
    city : str
        City to show.

    Returns
    -------
    matplotlib.figure.Figure
        The finished chart.
    """
    data = yearly[yearly["city"] == city]
    colors = ["tab:red" if value > 0 else "tab:blue" for value in data["anomaly"]]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(data["year"], data["anomaly"], color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Year")
    ax.set_ylabel("Anomaly (°C)")
    ax.set_title(f"{city}: temperature compared to 1961-1990 average")
    return fig


def plot_monthly_heatmap(monthly, city):
    """Heatmap of each month of each year, compared to that month's average.

    Parameters
    ----------
    monthly : pandas.DataFrame
        Monthly data from process.monthly_summary().
    city : str
        City to show.

    Returns
    -------
    matplotlib.figure.Figure
        The finished chart.
    """
    data = monthly[monthly["city"] == city]
    table = data.pivot(index="month", columns="year", values="temp_mean")
    table = table.sub(table.mean(axis=1), axis=0)

    first_year, last_year = table.columns.min(), table.columns.max()
    fig, ax = plt.subplots(figsize=(12, 4))
    image = ax.imshow(table, aspect="auto", cmap="coolwarm", vmin=-4, vmax=4,
                      extent=[first_year - 0.5, last_year + 0.5, 12.5, 0.5])
    fig.colorbar(image, ax=ax, label="°C vs month average")
    ax.set_yticks(range(1, 13))
    ax.set_yticklabels(MONTH_NAMES)
    ax.set_xlabel("Year")
    ax.set_title(f"{city}: monthly temperature, warmer or colder than usual")
    return fig


def plot_hot_days(yearly, cities):
    """Line chart of the number of hot days per year for each city.

    Parameters
    ----------
    yearly : pandas.DataFrame
        Yearly data from process.yearly_summary().
    cities : list of str
        Cities to show.

    Returns
    -------
    matplotlib.figure.Figure
        The finished chart.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    for city in cities:
        data = yearly[yearly["city"] == city]
        ax.plot(data["year"], data["hot_days"], label=city)
    ax.set_xlabel("Year")
    ax.set_ylabel("Days with max temperature ≥ 30°C")
    ax.set_title("Hot days per year")
    ax.legend()
    return fig


if __name__ == "__main__":
    from pathlib import Path

    from src.analysis import add_anomaly
    from src.process import load_data, monthly_summary, yearly_summary

    daily = load_data()
    yearly = add_anomaly(yearly_summary(daily))
    monthly = monthly_summary(daily)
    cities = sorted(yearly["city"].unique())

    output_dir = Path("figures")
    output_dir.mkdir(exist_ok=True)

    charts = {
        "temperature.png": plot_temperature(yearly, cities),
        "anomaly_milan.png": plot_anomaly(yearly, "Milan"),
        "heatmap_milan.png": plot_monthly_heatmap(monthly, "Milan"),
        "hot_days.png": plot_hot_days(yearly, cities),
    }
    for filename, fig in charts.items():
        fig.savefig(output_dir / filename, dpi=150, bbox_inches="tight")
    print(f"Saved {len(charts)} charts in {output_dir}/")