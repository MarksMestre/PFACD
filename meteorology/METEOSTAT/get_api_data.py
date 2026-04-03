import os
import json
import pandas as pd
import meteostat as ms
from datetime import date
import matplotlib.pyplot as plt


# Specify location and time range
POINT = ms.Point(50.1155, 8.6842, 113)  # Try with your location
START = date(2025, 1, 1)
END = date(2025, 12, 31)

# Get nearby weather stations
stations = ms.stations.nearby(POINT, limit=4)

# Get daily data & perform interpolation
ts = ms.daily(stations, START, END)
df = ms.interpolate(ts, POINT).fetch()

if df is not None:
    df.plot(y=[ms.Parameter.TEMP, ms.Parameter.TMIN, ms.Parameter.TMAX])
    plt.show()
else:
    print("Não foram encontrados dados para esta localização/período.")