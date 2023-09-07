# Calculate return on investment of solar panels. Assume no power is used by 
# home. All power is sold back to grid. Calculate value of solar energy.

import pandas as pd
import numpy as np

# import csv file generate from NREL PV_Watts Calculator
df = pd.read_csv("pvwatts_hourly.csv", skiprows=31)

# Add two empty columns to the dataframe: One to capture electric sellback rate 
# ($/100/kWh) each hour and another to capture hourly profit
df["rate"] = np.nan
df["profit"] = np.nan

# D1.2
for i in range(0, len(df.index)):
    hour = df.iloc[i][2]
    month = df.iloc[i][0]
    if (month < 6) or (month > 10):
        # winter
        if (hour < 11) or (hour > 19):
            # off peak
            df.iloc[i, df.columns.get_loc("rate")] = 6.814
        else:
            # on peak
            df.iloc[i, df.columns.get_loc("rate")] = 14.704
    else:
        # summer
        if (hour < 11) or (hour > 19):
            # off peak
            df.iloc[i, df.columns.get_loc("rate")] = 7.013
        else:
            # on peak
            df.iloc[i, df.columns.get_loc("rate")] = 17.055

df["profit"] = df["rate"] / 100 * df["AC System Output (W)"] / 1000

#print(df.iloc[:48])

print(df["profit"].sum())
