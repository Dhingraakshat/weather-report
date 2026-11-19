"""Weather Report: is Milan getting hotter?

This package downloads daily weather data for Milan, Rome, Riga and Delhi
from the Open-Meteo Historical Weather API, and studies how the climate
changed from 1950 to 2025.

Modules
-------
fetch
    Downloads the data from the API and saves it as CSV files.
process
    Loads the CSV files and makes yearly and monthly tables.
analysis
    Calculates the anomaly, the trends and the p-values.
plots
    Makes the charts with matplotlib.
"""
