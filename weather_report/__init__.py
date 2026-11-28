"""Weather Report: is Milan getting hotter?

This package downloads daily weather data for Milan, Rome, Riga and Delhi
from Open-Meteo, then compares their weather from 1950 to 2025.

Modules
-------
fetch
    Gets daily records from the API and saves them as CSV files.
process
    Joins the files and makes yearly and monthly tables.
analysis
    Measures temperature differences and trends.
plots
    Draws the charts used in the app and notebook.
"""
