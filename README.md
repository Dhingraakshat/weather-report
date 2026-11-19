# Weather Report: Is Milan getting hotter?

This is my project for the Python module of the course Coding for Data Science and Data Management (University of Milan, 2026/27).

I wanted to check if the climate in Milan is really getting warmer, and how Milan compares to other cities. I chose Rome because it is another big Italian city, Riga because I studied there, and Delhi because I am from India. I use daily weather data from 1950 to 2025.

## Questions I want to answer

1. Is the average temperature going up, and how fast?
2. How much warmer are the last years compared to the period 1961 to 1990?
3. Are there more hot days now (days with a max temperature of 30 °C or more)?
4. Is the change the same in every city and in every month?

## Data

The data comes from the Open-Meteo Historical Weather API:
https://open-meteo.com/en/docs/historical-weather-api

It is free and you do not need an API key. For every day I download:

- the mean temperature
- the max temperature
- the total rain

The data is not saved in this repository. The script `weather_report/fetch.py` downloads it into the `data` folder. The app also does this by itself the first time you run it.

## Libraries

- `requests` downloads the data from the API
- `pandas` loads the data and makes the yearly and monthly tables
- `numpy` fits the straight trend line
- `scipy` calculates the p-value of the trend
- `matplotlib` makes the charts
- `streamlit` runs the app
- `pytest` runs the tests

The exact versions are in `requirements.txt`.

## Files

```
weather-report/
    app.py              the Streamlit app
    requirements.txt    the libraries I use
    LICENSE             the MIT license
    figures/            the charts
    data/               the downloaded CSV files (not on GitHub)
    notebooks/          exploration.ipynb, my first look at the data
    tests/              the tests (test_project.py)
    weather_report/     the Python package with my code
        __init__.py     makes the folder a package
        fetch.py        downloads the data from the API
        process.py      loads and cleans the data, makes yearly and monthly tables
        analysis.py     calculates the anomaly and the warming trend
        plots.py        makes the charts
```

## How to install

You need Python 3.11 or newer.

```bash
git clone https://github.com/Dhingraakshat/weather-report.git
cd weather-report
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On Mac or Linux, use `source .venv/bin/activate` instead of the fourth line.

## How to run

To open the app:

```bash
python -m streamlit run app.py
```

In the app you can choose the cities, the years and the length of the moving average. You can also download the results table as a CSV file.

You can also run each part alone:

```bash
python -m weather_report.fetch       # download the data
python -m weather_report.analysis    # print the results table
python -m weather_report.plots       # save the charts in the figures folder
```

## Tests

I wrote some small tests with pytest. They check the trend, the anomaly, the hot day count and the error when the data is missing. To run them:

```bash
python -m pytest
```

## What I did

- I grouped the daily data by city and year. For each year I took the average temperature, the total rain and the number of hot days.
- For the anomaly, I took the average temperature of 1961 to 1990 for each city. Then for every year I calculated how much warmer or colder it was than this average. 1961 to 1990 is a normal reference period in climate studies.
- For the trend, I used `numpy.polyfit` to fit a straight line through the yearly temperatures. I show the result in °C per 10 years, because per year the numbers are very small.
- To check if the trend is real or just random, I used `scipy.stats.linregress`. It gives a p-value. If the p-value is smaller than 0.05, I say the trend is significant.
- I also compared the average of the first 30 years (1950 to 1979) with the last 30 years (1996 to 2025).
- In the heatmap, I compare every month with the normal value for that month. Without this, the chart only shows that summer is hot and winter is cold.
- I also calculated the trend for each season (winter, spring, summer, autumn), to see if some parts of the year get warmer faster than others.

## Results

| City | Change per 10 years (°C) | p-value | Significant | First 30 years (°C) | Last 30 years (°C) | Difference (°C) | Hot days, change per 10 years |
|---|---|---|---|---|---|---|---|
| Milan | +0.41 | < 0.0001 | Yes | 11.32 | 13.25 | +1.93 | +4.6 |
| Rome | +0.25 | < 0.0001 | Yes | 14.74 | 15.92 | +1.18 | +6.7 |
| Riga | +0.33 | < 0.0001 | Yes | 6.20 | 7.68 | +1.49 | +0.4 |
| Delhi | -0.03 | 0.34 | No | 24.75 | 24.59 | -0.16 | +1.0 |


Warming by season (°C per 10 years):

| City | Winter | Spring | Summer | Autumn |
|---|---|---|---|---|
| Milan | +0.43 | +0.36 | +0.53 | +0.31 |
| Rome | +0.15 | +0.23 | +0.40 | +0.23 |
| Riga | +0.47 | +0.42 | +0.23 | +0.19 |
| Delhi | -0.03 | -0.11 | -0.09 | +0.13 |

What I found:

- Milan gets warmer faster than the other cities. The trend line goes up about 3 °C from 1950 to 2025 (0.41 °C per 10 years for 7.5 decades). The last 30 years are 1.93 °C warmer than the first 30 years. Every year after 1990 was warmer than the 1961 to 1990 average.
- The warming happens in all months, also in winter, not only in summer.
- Rome gets warmer more slowly than Milan, but it gets more new hot days. I think this is because summers in Rome were already close to 30 °C, so a small change makes many more days go over 30 °C.
- Riga gets warmer too, but it still has almost no hot days, because it is rarely that hot there.
- Delhi does not show a warming trend in this data. The p-value is 0.34, so the small change could be just random. I was surprised by this. Some studies say that air pollution and more irrigation in north India can make temperatures lower, but I did not test this in my project.
- In Milan and Rome, summer gets warmer the fastest. In Riga it is the opposite: winter and spring get warmer faster than summer. This is also why Riga still has almost no hot days. For Delhi the values are small and go in both directions, so there is no clear change.

![Yearly temperature](figures/temperature.png)
![Milan anomaly](figures/anomaly_milan.png)
![Milan monthly heatmap](figures/heatmap_milan.png)
![Hot days](figures/hot_days.png)

## Limits of this project

- The data is not from one weather station in each city. It comes from a weather model that mixes real measurements and calculations.
- I use 30 °C as a hot day for all cities, but a hot day in Riga is not the same as a hot day in Delhi.
- A straight line is a simple way to show the trend. In reality, the warming is faster in the last years than at the start.
- The p-value test thinks that every year is independent. But a warm year is often followed by another warm year, so the real p-values are probably a bit bigger. For Milan, Rome and Riga they are so small that this does not change the result.
- For seasons, I put December in the same year as January and February. Climate studies usually put it with the next year. This changes the results only very little.

## Problems I had

- At first, only Milan and Rome downloaded. The API stopped me because I sent too many requests too fast. I added a pause of 5 seconds between cities, and after that all four cities worked.

## License

MIT
