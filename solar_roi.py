# Calculate return on investment of solar panels. Assume no power is used by 
# home. All power is sold back to grid. Calculate value of solar energy.

import pandas as pd
import numpy as np

# Create class to calculate electricity rates purchase and sell back rates
# DTE Residential Electric Pricing Options: 
# https://newlook.dteenergy.com/wps/wcm/connect/23195474-a4d1-4d38-aa30-a4426fd3336b/WholeHouseRateOptions.pdf?MOD=AJPERES

class Rate:
  def __init__(self):
    self.smmr_peak_cap = 0
    self.smmr_peak_ncp = 0
    self.smmr_offpk_cap = 0
    self.smmr_offpk_ncp = 0
    self.wntr_peak_cap = 0
    self.wntr_peak_ncp = 0
    self.wntr_offpk_cap = 0
    self.wntr_offpk_ncp = 0
    self.smmr_peak = 0
    self.smmr_offpk = 0
    self.wntr_peak = 0
    self.wntr_offpk = 0

  def calc_sellback_rates(self, PSCR):
    self.smmr_peak = self.smmr_peak_cap + self.smmr_peak_ncp + PSCR
    self.smmr_offpk = self.smmr_offpk_cap + self.smmr_offpk_ncp + PSCR
    self.wntr_peak = self.wntr_peak_cap + self.wntr_peak_ncp + PSCR
    self.wntr_offpk = self.wntr_offpk_cap + self.wntr_offpk_ncp + PSCR

# Power Supply Cost Recovery
PSCR = 1.917 

# Time of Day 11 a.m. - 7 p.m. Rate (D1.2) 
D1_2 = Rate()
D1_2.smmr_peak_cap = 11.033
D1_2.smmr_peak_ncp = 4.105
D1_2.smmr_offpk_cap = 0.991
D1_2.smmr_offpk_ncp = 4.105
D1_2.wntr_peak_cap = 8.682
D1_2.wntr_peak_ncp = 4.105
D1_2.wntr_offpk_cap = 0.792
D1_2.wntr_offpk_ncp = 4.105
D1_2.calc_sellback_rates(PSCR)

# Time of Day 3 p.m. – 7 p.m. Standard Base Rate (D1.11) 
# TODO

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
            df.iloc[i, df.columns.get_loc("rate")] = D1_2.wntr_offpk
        else:
            # on peak
            df.iloc[i, df.columns.get_loc("rate")] = D1_2.wntr_peak
    else:
        # summer
        if (hour < 11) or (hour > 19):
            # off peak
            df.iloc[i, df.columns.get_loc("rate")] = D1_2.smmr_offpk
        else:
            # on peak
            df.iloc[i, df.columns.get_loc("rate")] = D1_2.smmr_peak

df["profit"] = df["rate"] / 100 * df["AC System Output (W)"] / 1000

#print(df.iloc[:48])

print(df["profit"].sum())
