# Calculate return on investment of solar panels. Assume no power is used by 
# home. All power is sold back to grid. Calculate value of solar energy.

import pandas as pd
import numpy as np

# DTE Residential Electric Pricing Options: https://newlook.dteenergy.com/wps/wcm/connect/23195474-a4d1-4d38-aa30-a4426fd3336b/WholeHouseRateOptions.pdf?MOD=AJPERES
PSCR = 1.917 # Power Supply Cost Recovery

# Time of Day 3 p.m. – 7 p.m. Standard Base Rate (D1.11) 
# TODO

# Time of Day 11 a.m. - 7 p.m. Rate (D1.2) 
D1_2_smmr_peak_cap = 11.033
D1_2_smmr_peak_ncp = 4.105
D1_2_smmr_offpk_cap = 0.991
D1_2_smmr_offpk_ncp = 4.105

D1_2_wntr_peak_cap = 8.682
D1_2_wntr_peak_ncp = 4.105
D1_2_wntr_offpk_cap = 0.792
D1_2_wntr_offpk_ncp = 4.105

D1_2_smmr_peak = D1_2_smmr_peak_cap + D1_2_smmr_peak_ncp + PSCR
D1_2_smmr_offpk = D1_2_smmr_offpk_cap + D1_2_smmr_offpk_ncp + PSCR
D1_2_wntr_peak = D1_2_wntr_peak_cap + D1_2_wntr_peak_ncp + PSCR
D1_2_wntr_offpk = D1_2_wntr_offpk_cap + D1_2_wntr_offpk_ncp + PSCR

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
            df.iloc[i, df.columns.get_loc("rate")] = D1_2_wntr_offpk
        else:
            # on peak
            df.iloc[i, df.columns.get_loc("rate")] = D1_2_wntr_peak
    else:
        # summer
        if (hour < 11) or (hour > 19):
            # off peak
            df.iloc[i, df.columns.get_loc("rate")] = D1_2_smmr_offpk
        else:
            # on peak
            df.iloc[i, df.columns.get_loc("rate")] = D1_2_smmr_peak

df["profit"] = df["rate"] / 100 * df["AC System Output (W)"] / 1000

#print(df.iloc[:48])

print(df["profit"].sum())
